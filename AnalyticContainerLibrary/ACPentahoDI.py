__author__ = 'Chris Bergh'
import sys
import json
import tempfile
import subprocess
from collections import OrderedDict

if not '../AnalyticContainerLibrary' in sys.path:
    sys.path.insert(0, '../AnalyticContainerLibrary')
from AnalyticContainer.AnalyticContainerLibrary.ACSingletons import ACLogger, ACHelpers
from AnalyticContainer.AnalyticContainerLibrary.ACSettings import *

# this is a real simple way to load and run a pan script
# see http://wiki.pentaho.com/display/EAI/Pan+User+Documentation
class ACPentahoDI(object):
    def __init__(self):
        self.config_dict = OrderedDict()

    def __del__(self):
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

    def __getstate__(self):
        state = dict()
        state['config_dict'] = self.config_dict
        return state

    def __setstate__(self, state):
        self.config_dict = state['config_dict']

    def create_from_files(self, file_manifest_json):
        try:
            with open(file_manifest_json) as data_file:
                self.config_dict = json.load(data_file, object_pairs_hook=OrderedDict)
        except (IOError, ValueError), ex:
            ACLogger().get_logger().error('invalid json loaded to ACPentahoDI %s', ex.message)
            self.config_dict = None
            return False
        return self._complete_creation()

    def create_from_strings(self, json_string):
        self.config_dict = json.loads(json_string, object_pairs_hook=OrderedDict)
        return self._complete_creation()

    def create_from_dict(self, config_dict):
        self.config_dict = config_dict
        return self._complete_creation()

    def _complete_creation(self):
        if self.is_valid_pentahodi_schema() is False:
            ACLogger().get_logger().error('invalid Tableau json schema %s', self.config_dict)
            return False
        return True

    def is_valid_pentahodi_schema(self):
        if self.config_dict is None:
            return False
        error_list = list()
        if PENTAHODI_LOGLEVEL not in self.config_dict:
            error_list.append(PENTAHODI_LOGLEVEL)
        if PENTAHODI_KEYS not in self.config_dict or \
                        isinstance(self.config_dict[PENTAHODI_KEYS], dict) is False:
            error_list.append(PENTAHODI_KEYS)

        if self.config_dict[PENTAHODI_KEYS] is not None and \
            isinstance(self.config_dict[PENTAHODI_KEYS], dict) is True:
            for key, item in self.config_dict[TABLEAU_SERVER_KEYS].iteritems():
                if isinstance(item, dict) is False or PENTAHODI_FILENAME not in item:
                    error_list.append('key: ' + key + ':  ' + PENTAHODI_FILENAME)
                if PENTAHODI_FILE_PARAMETERS in item:
                    if isinstance(item[PENTAHODI_FILE_PARAMETERS], dict) is False:
                        error_list.append('must be dict for key: ' + key + ':  ' + PENTAHODI_FILE_PARAMETERS)
                    else:
                        for param, param_val in item[PENTAHODI_FILE_PARAMETERS].iteritems():
                            if isinstance(param, basestring) is False or isinstance(param_val, basestring) is False:
                                error_list.append('must be strings for {k: val }: ' + key + ':  ' + PENTAHODI_FILE_PARAMETERS)
        if len(error_list) > 0:
            ACLogger().get_logger().error('invalid PentahoDI json, errors in: %s' % error_list)
            return False
        else:
            return True

    def execute(self, key_values_dict, pdi_path, pdi_file_path=None):
        rv = True
        if PENTAHODI_LOGLEVEL in self.config_dict:
            loglevel = '%s' % self.config_dict[PENTAHODI_LOGLEVEL]
        else:
            loglevel = 'Minimal'
        shellret = ''
        if self.config_dict[PENTAHODI_KEYS] is not None and \
            isinstance(self.config_dict[PENTAHODI_KEYS], dict) is True:
            for key, item in self.config_dict[TABLEAU_SERVER_KEYS].iteritems():
                key_values_dict[key] = dict()
                key_values_dict[key]['output'] = ACHelpers.compress('')
                key_values_dict[key]['status'] = False
                pdi = os.path.join(pdi_path, 'pan.sh')
                if PENTAHODI_INTEGRATION_OUTPUT_FILENAME in item:
                    output_file_path = os.path.join(os.getcwd(), item[PENTAHODI_INTEGRATION_OUTPUT_FILENAME])
                else:
                    output_file_path = None
                if pdi_file_path is None:
                    pdi_file = os.path.join(os.getcwd(), 'docker-share', item[PENTAHODI_FILENAME])
                else:
                    pdi_file = os.path.join(pdi_file_path, item[PENTAHODI_FILENAME])
                try:
                    # pan.sh -file="/PRD/Customer Dimension.ktr" -level=Minimal -param:MASTER_HOST=192.168.1.3 -param:MASTER_PORT=8181
                    params = [pdi, '-file=%s' % pdi_file, '-level=%s' % loglevel]
                    if PENTAHODI_FILE_PARAMETERS in item:
                        for p, pval in item[PENTAHODI_FILE_PARAMETERS].iteritems():
                            params.append('-param:%s=%s' % (p, pval))
                    shellret = subprocess.check_output(params)
                    ACLogger().get_logger().info("calling pan by: %s" % params)
                    key_values_dict[key]['output'] = ACHelpers.compress('')
                    if shellret is not None and shellret != '':
                        key_values_dict[key]['status'] = True
                        if output_file_path is not None:
                            ACLogger().get_logger().info("looking for file @: %s" % output_file_path)
                            try:
                                statinfo = os.stat(output_file_path)
                            except:
                                pass
                            else:
                                if  statinfo.st_size > 0:
                                    with open(output_file_path, 'rb') as f:
                                        d = f.read()
                                        if d is not None and len(d) > 0:
                                            key_values_dict[key]['output'] = ACHelpers.compress(d)
                                            ACLogger().get_logger().info(" got outuput data for key %s: %s" % (key,d))
                    else:
                        key_values_dict[key]['status'] = False
                        rv = False
                except subprocess.CalledProcessError, e:
                    ACLogger().get_logger().error('PentahoDI execture exception: %s' % str(e))
                    key_values_dict[key]['status'] = False
                finally:
                    key_values_dict[key]['log'] = shellret
        return rv
