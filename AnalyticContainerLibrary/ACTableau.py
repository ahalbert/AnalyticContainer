__author__ = 'Chris Bergh'
import sys
import json
import time
import copy
from collections import OrderedDict
from tableau_tools.tableau_rest_api import *
from tableau_tools import *
from tableau_tools.tableau_documents import *
from httplib import HTTPException, ResponseNotReady
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as expected_conditions
import requests
import xml.etree.ElementTree as ET
if not '../AnalyticContainerLibrary' \
        in sys.path:
    sys.path.insert(0, '../AnalyticContainerLibrary')
from AnalyticContainer.AnalyticContainerLibrary.ACSingletons import ACLogger, ACHelpers
from AnalyticContainer.AnalyticContainerLibrary.ACSettings import *

class ACTableau(object):
    def __init__(self):
        self.conn = None
        self.logger = None
        self.config_dict = OrderedDict()
        self.pydriver = None

    def __del__(self):
        if self.conn is not None:
            pass
        self.config_dict = OrderedDict()

    def __eq__(self, other):
        if other is None:
            return False
        if self.config_dict != other.config_dict:
            return False
        return True

    def __str__(self):
        s = ''
        s += 'config_dict = %s' % str(self.config_dict)
        return s

    # do not serialize connection
    def __getstate__(self):
        state = dict()
        state['config_dict'] = self.config_dict
        return state

    def __setstate__(self, state):
        self.config_dict = state['config_dict']
        self.conn = None

    def create_from_files(self, file_manifest_json):
        try:
            with open(file_manifest_json) as data_file:
                self.config_dict = json.load(data_file, object_pairs_hook=OrderedDict)
        except (IOError, ValueError), ex:
            ACLogger().get_logger().error('invalid json loaded to ACTableau %s', ex.message)
            self.config_dict = None
            return False
        return self._complete_creation()

    def create_from_strings(self, json_string):
        self.config_dict = json.loads(json_string, object_pairs_hook=OrderedDict)
        return self._complete_creation()

    def create_from_dict(self, config_dict):
        self.config_dict = config_dict
        return self._complete_creation()

    def connect(self):
        if self.is_valid_tableau_schema() is False:
            return False

        if self.conn is not None:
            return True
        try:
            server_url = self.config_dict[TABLEAU_SERVER_URL]
            username = self.config_dict[TABLEAU_SERVER_USERNAME]
            password = self.config_dict[TABLEAU_SERVER_PASSWORD]
            self.conn = TableauRestApiConnection(server_url, username, password, 'datakitchentest')
            if self.conn is None:
                ACLogger().get_logger().error('Unable to do Tableau login')
                return False
            self.conn.signin()
            self.logger = Logger('tableau.log')
            self.conn.enable_logging(self.logger)
        except Exception, e:
            self.conn = None
            ACLogger().get_logger().error('Failed Tableau login: %s' % str(e))
            return False

        return True

    def _complete_creation(self):
        if self.is_valid_tableau_schema() is False:
            ACLogger().get_logger().error('invalid Tableau json schema %s', self.config_dict)
            return False
        return True

    def is_valid_tableau_schema(self):
        if self.config_dict is None:
            return False
        error_list = list()
        if TABLEAU_SERVER_URL not in self.config_dict:
            error_list.append(TABLEAU_SERVER_URL)
        if TABLEAU_SERVER_USERNAME not in self.config_dict:
            error_list.append(TABLEAU_SERVER_USERNAME)
        if TABLEAU_SERVER_PASSWORD not in self.config_dict:
            error_list.append(TABLEAU_SERVER_PASSWORD)
        if TABLEAU_SERVER_KEYS not in self.config_dict or \
                        isinstance(self.config_dict[TABLEAU_SERVER_KEYS], dict) is False:
            error_list.append(TABLEAU_SERVER_PASSWORD)

        if self.config_dict[TABLEAU_SERVER_KEYS] is not None and \
            isinstance(self.config_dict[TABLEAU_SERVER_KEYS], dict) is True:
            for key, item in self.config_dict[TABLEAU_SERVER_KEYS].iteritems():
                if isinstance(item, dict) and TABLEAU_TYPE in item and item[TABLEAU_TYPE] == TABLEAU_UPSERT:
                    if TABLEAU_PROJECT_NAME not in item:
                        error_list.append(key + ': ' + TABLEAU_UPSERT + ': ' + TABLEAU_PROJECT_NAME)
                    if TABLEAU_CONTENT_NAME not in item:
                        error_list.append(key + ': ' + TABLEAU_UPSERT + ': ' + TABLEAU_CONTENT_NAME)
                    if TABLEAU_WORKBOOK_NAME not in item:
                        error_list.append(key + ': ' + TABLEAU_UPSERT + ': ' + TABLEAU_WORKBOOK_NAME)
                    if TABLEAU_DATASOURCE_WORKBOOK_NAME not in item:
                        error_list.append(key + ': ' + TABLEAU_UPSERT + ': ' + TABLEAU_DATASOURCE_WORKBOOK_NAME)
                elif isinstance(item, dict) and TABLEAU_TYPE in item and item[TABLEAU_TYPE] == TABLEAU_DOWNLOAD_CSV:
                    if TABLEAU_SELENIUM_URL not in self.config_dict:
                        if TABLEAU_SELENIUM_URL in item:
                            self.config_dict[TABLEAU_SELENIUM_URL] = item[TABLEAU_SELENIUM_URL]
                        else:
                            error_list.append(key + ': ' + TABLEAU_SELENIUM_URL)
                    if TABLEAU_PROJECT_NAME not in item:
                        error_list.append(key + ': ' + TABLEAU_DOWNLOAD_CSV + ': ' + TABLEAU_PROJECT_NAME)
                    if TABLEAU_CONTENT_NAME not in item:
                        error_list.append(key + ': ' + TABLEAU_DOWNLOAD_CSV + ': ' + TABLEAU_CONTENT_NAME)
                    if TABLEAU_VIEW_NAME not in item:
                        error_list.append(key + ': ' + TABLEAU_DOWNLOAD_CSV + ': ' + TABLEAU_VIEW_NAME)
        if len(error_list) > 0:
            ACLogger().get_logger().error('invalid Tableau json, errors in: %s' % error_list)
            return False
        else:
            return True

    def get_project_workbooks_and_datasources(self, return_dict):
        if self.config_dict is None or self.connect() is False or isinstance(return_dict, dict) is False:
            return False
        try:
            dses = self.conn.query_datasources()
            workbooks = self.conn.query_workbooks()
        except (RecoverableHTTPException, NoResultsException), e:
            ACLogger().get_logger().error('Tableau Exception: %s' % str(e))
            return False

        return_dict['workbooks'] = dict()
        for wb in workbooks:
            workbook_name = wb.get('name')
            for element in wb.iter():
                if element.tag is not None and element.tag.find('project') != -1:
                    project_name = element.get('name')
                    if project_name not in return_dict:
                        return_dict[project_name] = dict()
                    if 'workbooks' not in return_dict[project_name]:
                        return_dict[project_name]['workbooks'] = list()
                    return_dict[project_name]['workbooks'].append(workbook_name)

        for ds in dses:
            datasource_name = ds.get('name')
            for element in ds.iter():
                if element.tag is not None and element.tag.find('project') != -1:
                    project_name = element.get('name')
                    if project_name not in return_dict:
                        return_dict[project_name] = dict()
                    if 'datasources' not in return_dict[project_name]:
                        return_dict[project_name]['datasources'] = list()
                    return_dict[project_name]['datasources'].append(datasource_name)
        return True


    # note:  https://tableauandbehold.com/2015/08/06/tableau-rest-api-400-error-response-code-400011/
    #  IN ORDER TO PUBLISH MUST DO FIVE THINGS:
    #   1.  In your tableau desktop UI, for each workbook workbook, publish datasources to tableau server first, and check that all relevant views reference that datasource(s)
    #   2.  In tableau online UI, Make sure that datasource has embed the credentials and password that are necessary
    #   3.  In your tableau desktop UI, publish the entire workbook to any project
    #   4.  In tableau online UI, download that same workbook as a .twb file
    #   5.  Move that twb file into the docker-share directory in the Recipe
    #   NOTE: you will need to publish the data source to every tableau online project you will use, (via tableau desktop)
    #
    # OTHER LINKS TRIED, DID NOT WORK
    # https://community.tableau.com/thread/159524
    # https://community.tableau.com/thread/178756
    def upsert_workbook_in_project(self, project_name, twb_content_name, twb_filename, twb_datasource_filename):
        if project_name is None or twb_filename is None or twb_datasource_filename is None:
            return False
        def find_datasource(the_child):
            the_sqlproxy_name = None
            if child is None or len(list(child)) == 0:
                return None
            for s in the_child.iter():
                if the_sqlproxy_name is None and 'datasource' in s.attrib:
                    the_sqlproxy_name = s.attrib['datasource']
            if the_sqlproxy_name is None:
                return find_datasource(list(the_child))
            else:
                return the_sqlproxy_name

        wd = dict()
        twb = None
        do_the_mod_via_xml = False
        new_wb_luid = None
        # remove thumbnails, switch out datasources by changing the 'datasource' xml section and chanign the sqlproxy
        ds_tree = ET.parse(twb_datasource_filename)
        ds_root = ds_tree.getroot()
        ds_datasources = None
        sqlproxy_name = None
        for ds_child in ds_root:
            if ds_child.tag == 'datasources':
                for sc in ds_child.iter():
                    if 'caption' in sc.attrib and 'name' in sc.attrib and 'version' in sc.attrib:
                        sqlproxy_name = sc.attrib['name']
                if sqlproxy_name is not None:
                    ds_datasources = ds_child
                else:
                    return False
        tree = ET.parse(twb_filename)
        root = tree.getroot()
        previous_sqlproxy_name = ''
        for child in root:
            if child.tag == 'worksheets':
                previous_sqlproxy_name = find_datasource(child)
                if previous_sqlproxy_name is None or isinstance(previous_sqlproxy_name, basestring) is False:
                    return False

        if do_the_mod_via_xml is True:
            for child in root:
                if child.tag == 'thumbnail':
                    root.remove(child) # remove it
                if child.tag == 'datasources' and ds_datasources is not None:
                    root.remove(child) #do switcheroo
                    root.insert(2, ds_datasources)
                    #root.append(copy.deepcopy(ds_datasources))
            tree.write(twb_filename)
        else:
            with open(twb_filename, 'r+') as fwb:
                twb_str = fwb.read()
                fwb.seek(0)
                try:
                    ts1_index = twb_str.index('<thumbnails>')
                    ts2_index = twb_str.index('</thumbnails>') + len('</thumbnails>')
                    new_twb_str = '%s%s' % (twb_str[:ts1_index], twb_str[ts2_index:])
                    fwb.write(new_twb_str)
                    fwb.truncate()
                except ValueError:
                    pass

            ds_string = ''
            with open(twb_datasource_filename, 'r+') as fwb:
                twb_str = fwb.read()
                try:
                    ds1_index = twb_str.index('<datasources>')
                    ds2_index = twb_str.index('</datasources>') + len('</datasources>')
                    ds_string = twb_str[ds1_index-1:ds2_index]
                except ValueError:
                    return False

            with open(twb_filename, 'r+') as fwb:
                twb_str = fwb.read()
                fwb.seek(0)
                try:
                    ds1_index = twb_str.index('<datasources>')
                    ds2_index = twb_str.index('</datasources>') + len('</datasources>')
                    new_twb_str = '%s%s%s' % (twb_str[:ds1_index], ds_string, twb_str[ds2_index:])
                    fwb.write(new_twb_str)
                except ValueError:
                    return False
                finally:
                    fwb.truncate()

        with open(twb_filename, 'r+') as fwb:
            twb_str = fwb.read()
            fwb.seek(0)
            try:
                fwb.write(twb_str.replace(previous_sqlproxy_name, sqlproxy_name))
            except ValueError:
                return False
            finally:
                fwb.truncate()
        def case_insensitive_eq(pn, wd1):
            for key, val in wd1.iteritems():
                if key.lower() == pn.lower():
                    return True
            return False
        if self.get_project_workbooks_and_datasources(wd) is False or isinstance(wd, dict) is False or case_insensitive_eq(project_name,wd) is False:
            ACLogger().get_logger().error('upsert_workbook_in_project: project not found %s' % project_name)
            return False
        try:
            project_luid = self.conn.query_project_luid_by_name(project_name)
            if project_luid is not None and len(project_luid) > 0:
                new_wb_luid = self.conn.publish_workbook(twb_filename, twb_content_name, project_luid, True)
            else:
                ACLogger().get_logger().error('upsert_workbook_in_project: project_luid is bad %s' % project_luid)
        except (RecoverableHTTPException, NoResultsException, IOError, Exception), e:
            ACLogger().get_logger().error('upsert_workbook_in_project Exception: (%s), new_wb_luid: (%s)' % (str(e), new_wb_luid))
            ACLogger().get_logger().info('IN ORDER TO PUBLISH a workbook please do these five things: ')
            ACLogger().get_logger().info('In your tableau desktop UI, for each workbook workbook, publish datasources to tableau server first, and check that all relevant views reference that datasource(s)')
            ACLogger().get_logger().info('In tableau online UI, Make sure that datasource has embed the credentials and password that are necessary')
            ACLogger().get_logger().info('In your tableau desktop UI, publish the entire workbook to any project')
            ACLogger().get_logger().info('In tableau online UI, download that same workbook as a .twb file')
            ACLogger().get_logger().info('Move that twb file into the docker-share directory in the Recipe')
            ACLogger().get_logger().info('NOTE: you will need to publish the data source to every tableau online project you will use, (via tableau desktop)')
            ACLogger().get_logger().info(
                'see: https://tableauandbehold.com/2015/08/06/tableau-rest-api-400-error-response-code-400011/')
            #return False

        if new_wb_luid is None:
            return False
        else:
            return True


    def execute(self, key_values_dict, inside_docker_share_dir):
        if self.connect() is False:
            return False
        twb_file = os.environ.get('twb_file') # for debug
        twb_datasource_file = os.environ.get('twb_datasource_file')  # for debug
        if self.config_dict[TABLEAU_SERVER_KEYS] is not None and \
                        isinstance(self.config_dict[TABLEAU_SERVER_KEYS], dict) is True:
            for key, item in self.config_dict[TABLEAU_SERVER_KEYS].iteritems():
                key_values_dict[key] = None
                if isinstance(item, dict) and TABLEAU_TYPE in item and item[TABLEAU_TYPE] == TABLEAU_UPSERT:
                    if self.upsert_workbook_in_project(item[TABLEAU_PROJECT_NAME],
                                                       item[TABLEAU_CONTENT_NAME],
                                                       twb_file if twb_file is not None else os.path.join(
                                                           inside_docker_share_dir, item[TABLEAU_WORKBOOK_NAME]),
                                                       twb_datasource_file if twb_datasource_file is not None else os.path.join(
                                                           inside_docker_share_dir, item[TABLEAU_DATASOURCE_WORKBOOK_NAME])) is False:
                        ACLogger().get_logger().error('unable to update workbook: %s in project: %s' %
                                                      (item[TABLEAU_WORKBOOK_NAME], item[TABLEAU_PROJECT_NAME]))
                        return False
                    else:
                        ACLogger().get_logger().info('Successfully updated workbook: %s in project: %s' %
                                                      (item[TABLEAU_WORKBOOK_NAME], item[TABLEAU_PROJECT_NAME]))
                if isinstance(item, dict) and TABLEAU_TYPE in item and item[TABLEAU_TYPE] == TABLEAU_DOWNLOAD_CSV:
                    the_data, rv = self.download_crosstab(item[TABLEAU_PROJECT_NAME],
                                                        item[TABLEAU_CONTENT_NAME],
                                                        twb_file if twb_file is not None else item[TABLEAU_VIEW_NAME])
                    if rv is False:
                        ACLogger().get_logger().error(
                            'unable to download view crosstab(%s) in workbook(%s) project(%s)' %
                            (item[TABLEAU_VIEW_NAME], item[TABLEAU_CONTENT_NAME], item[TABLEAU_PROJECT_NAME]))
                        return False
                    else:
                        ACLogger().get_logger().info('successfully downloaded crosstab data %s=%s' % (key, the_data))
                        key_values_dict[key] = copy.copy(ACHelpers.compress(the_data))

        return True

    def selenium_setup(self):
        capabilities = {'browserName': 'chrome'}
        try:
            self.pydriver = webdriver.Remote(self.config_dict[TABLEAU_SELENIUM_URL], capabilities)
        except (WebDriverException, Exception), we:
            ACLogger().get_logger().error('unable to start webdriver.Remote: %s ' % we)
            return False
        return True

    def selenium_login(self):
        try:
            self.pydriver.get(self.config_dict[TABLEAU_SERVER_URL])
            time.sleep(2)
            self.pydriver.page_source.encode('utf-8')
            logins = self.pydriver.find_elements(By.XPATH, '//input')
            if logins is None or len(logins) == 0:
                ACLogger().get_logger().error('selenium_login error 1')
                return False

            the_login = logins[0]
            password = logins[1]
            the_login.send_keys(self.config_dict[TABLEAU_SERVER_USERNAME])
            password.send_keys(self.config_dict[TABLEAU_SERVER_PASSWORD])
            buttons = self.pydriver.find_elements(By.XPATH, '//button')
            button = None
            for b in buttons:
                if str(b.text) == 'Sign In':
                    button = b
            if button is None:
                ACLogger().get_logger().error('selenium_login error 2')
                return False
            button.click()
            time.sleep(2)
            if 'Workbooks' not in self.pydriver.title:
                ACLogger().get_logger().error('selenium_login error 3')
                return False
        except (WebDriverException, StaleElementReferenceException, HTTPException, ResponseNotReady) , e:
            ACLogger().get_logger().error('selenium_login error: %s' % str(e))
            return False
        ACLogger().get_logger().info(
            'Logged in %s successfully, next page title: %s' % (self.config_dict[TABLEAU_SERVER_URL], self.pydriver.title))
        return True


    def download_crosstab(self, project_name, twb_content_name, twb_view_name):
        if project_name is None or twb_content_name is None or twb_view_name is None:
            return None, False
        wd = dict()
        if self.get_project_workbooks_and_datasources(wd) is False or project_name not in wd:
            ACLogger().get_logger().error('download_crosstab: project not found %s' % project_name)
            return None, False
        if 'workbooks' not in wd[project_name] or twb_content_name not in wd[project_name]['workbooks']:
            ACLogger().get_logger().error(
                'download_crosstab: workbook(%s) not found in project(%s)' % (twb_content_name, project_name))
            return None, False
        if self.selenium_setup() is False or self.selenium_login() is False:
            ACLogger.log_and_print_error(
                'download_crosstab: unable to log into Tableau at %s' % self.config_dict[TABLEAU_SERVER_URL])
            return None, False
        # click on the 'Projects'
        if self._get_link('span', '**Projects**', 'Projects') is False:
            return None, False
        # click on the right project --
        if self._get_link('a', 'project', project_name) is False:
            return None, False
        # click on the right workbook --
        if self._get_link('a', 'workbook', twb_content_name) is False:
            return None, False
        # click on the right workbook --
        if self._get_link('a', 'view', twb_view_name) is False:
            return None, False
        # get the data test title
        cookies = self.pydriver.get_cookies()
        try:
            headers = dict()
            headers['User-Agent'] = 'Mozilla/5.0'
            headers['from'] = self.config_dict[TABLEAU_SERVER_USERNAME]
            headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            s = dict()
            for cookie in cookies:
                s[cookie['name']] = cookie['value']
            r = requests.get((self.pydriver.current_url.split('?')[0]).replace('#/site', 't') + '.csv', cookies=s, verify=False, headers=headers)
        except Exception, e:
            ACLogger().get_logger().error('download_crosstab: %s' % str(e))
            return False
        the_data = r.content.encode('utf-8')
        return the_data, True

    def _get_link(self, the_link, link_type, link_text):
        try:
            links = self.pydriver.find_elements(By.XPATH, "//%s" % the_link)
        except (NoSuchElementException, StaleElementReferenceException, WebDriverException), e:
            ACLogger.log_and_print_error(
                '_get_link: unable to find type(%s) links in UI, exception=%s' % (link_type, str(e)))
            return False
        clicked_it = False
        for link in links:
            if clicked_it is False and link.text == link_text:
                try:
                    link.click()
                except (NoSuchElementException, StaleElementReferenceException, WebDriverException), e:
                    ACLogger.log_and_print_error(
                        '_get_link: unable to click on type(%s) text(%s) in UI, exception=%s' % (link_type,link_text,str(e)))
                    return False
                finally:
                    clicked_it = True
                    break
        if clicked_it is False:
            ACLogger.log_and_print_error(
                '_get_link: unable to find link %s in UI ' % link_text)
            return False
        time.sleep(2)
        return True