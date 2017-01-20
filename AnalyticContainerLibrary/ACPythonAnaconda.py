
__author__ = 'Chris Bergh'
import os
import json
from datetime import datetime
from collections import OrderedDict
import subprocess
from AnalyticContainer.AnalyticContainerLibrary.ACSingletons import ACLogger, ACHelpers
from AnalyticContainer.AnalyticContainerLibrary.ACSettings import *


class ACPythonAnaconda(object):
    def __init__(self):
        self.conn = None
        self.config_dict = OrderedDict()

    def __del__(self):
        if self.conn is not None:
            self.conn.close()
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
        except (IOError,ValueError), ex:
            ACLogger().get_logger().error('invalid json loaded to ACPythonAnaconda %s', ex.message)
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
        if self.is_valid_schema() is False:
            return False
        return False

    def _complete_creation(self):
        if self.is_valid_schema() is False:
            ACLogger().get_logger().error('invalid ACPythonAnaconda json schema %s', self.config_dict)
            return False
        return True

    def is_valid_schema(self):
        if self.config_dict is None:
            return False
        error_list = list()

        if PYTHON_ANACONDA_KEYS not in self.config_dict or \
                        isinstance(self.config_dict[PYTHON_ANACONDA_KEYS], dict) is False:
            error_list.append(PYTHON_ANACONDA_KEYS)

        if self.config_dict[PYTHON_ANACONDA_KEYS] is not None and \
            isinstance(self.config_dict[PYTHON_ANACONDA_KEYS], dict) is True:
            for key, item in self.config_dict[TABLEAU_SERVER_KEYS].iteritems():
                if isinstance(item, dict) is False:
                    error_list.append('key: ' + key + ' must be in bracket format {}')
                else:
                    if PYTHON_ANACONDA_FILENAME not in item:
                        error_list.append('key: ' + key + ':  ' + PYTHON_ANACONDA_FILENAME)
                    if PYTHON_ANACONDA_FILE_PARAMETERS in item:
                        if isinstance(item[PYTHON_ANACONDA_FILE_PARAMETERS], dict) is False:
                            error_list.append('must be dict for key: ' + key + ':  ' + PYTHON_ANACONDA_FILE_PARAMETERS)
                        else:
                            for param, param_val in item[PYTHON_ANACONDA_FILE_PARAMETERS].iteritems():
                                if isinstance(param, basestring) is False or isinstance(param_val, basestring) is False:
                                    error_list.append('must be strings for {k: val }: ' + key + ':  ' + PYTHON_ANACONDA_FILE_PARAMETERS)
        if len(error_list) > 0:
            ACLogger().get_logger().error('invalid ACPythonAnaconda json, errors in: %s' % error_list)
            return False
        else:
            return True

    def execute(self, key_values_dict, jupyter_dir, notebook_file_dir=None):
        rv = True
        shellret = ''
        if self.config_dict[PYTHON_ANACONDA_KEYS] is not None and \
            isinstance(self.config_dict[PYTHON_ANACONDA_KEYS], dict) is True:
            for key, item in self.config_dict[TABLEAU_SERVER_KEYS].iteritems():
                key_values_dict[key] = dict()
                output_file_path = None
                if jupyter_dir is not None:
                    jupyter = os.path.join(jupyter_dir, 'jupyter')
                else:
                    jupyter = '/opt/conda/bin/jupyter'
                if notebook_file_dir is None:
                    notebook_file = os.path.join(os.getcwd(), 'docker-share', item[PYTHON_ANACONDA_FILENAME])
                    if PYTHON_ANACONDA_NOTEBOOK_OUTPUT_FILENAME in item:
                        output_file_path = os.path.join(os.getcwd(), 'docker-share',
                                                    item[PYTHON_ANACONDA_NOTEBOOK_OUTPUT_FILENAME])
                else:
                    notebook_file = os.path.join(notebook_file_dir, item[PYTHON_ANACONDA_FILENAME])
                    if PYTHON_ANACONDA_NOTEBOOK_OUTPUT_FILENAME in item:
                        output_file_path = os.path.join(notebook_file_dir,
                                                    item[PYTHON_ANACONDA_NOTEBOOK_OUTPUT_FILENAME])
                try:
                    try:
                        statinfo = os.stat(notebook_file)
                    except:
                        pass
                    else:
                        if statinfo is None or statinfo.st_size == 0:
                            ACLogger().get_logger().error(
                                'ACPythonAnaconda unable to open notebook_file %s' % notebook_file)
                            key_values_dict[key]['status'] = False
                            return False

                    params = [jupyter, 'nbconvert', '--execute' , '%s' % notebook_file]
                    my_env = os.environ.copy()
                    if PYTHON_ANACONDA_FILE_PARAMETERS in item:
                        for p, pval in item[PYTHON_ANACONDA_FILE_PARAMETERS].iteritems():
                            my_env[p] = pval
                    #ACLogger.log_and_print("calling jupyter with env variables of: %s" % my_env)
                    shellret = subprocess.check_output(params, env=my_env, stderr=subprocess.STDOUT)
                    key_values_dict[key]['output'] = ACHelpers.compress('')
                    ACLogger.log_and_print("calling jupyter by: %s" % params)
                    if shellret is not None:
                        key_values_dict[key]['status'] = True
                        if output_file_path is not None:
                            try:
                                statinfo = os.stat(output_file_path)
                            except:
                                pass
                            else:
                                if statinfo.st_size > 0:
                                    with open(output_file_path, 'rb') as f:
                                        d = f.read()
                                        if d is not None and len(d) > 0:
                                            key_values_dict[key]['output'] = ACHelpers.compress(d)
                                            ACLogger().get_logger().info(" got outuput data for key %s: %s" % (key,d))
                    else:
                        key_values_dict[key]['status'] = False
                        rv = False

                except Exception, e:
                    ACLogger().get_logger().error('ACPythonAnaconda execute exception: %s shellret(%s)' % (str(e), shellret))
                    key_values_dict[key]['status'] = False
                finally:
                    key_values_dict[key]['log'] = shellret
        return rv