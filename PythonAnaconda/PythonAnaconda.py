__author__ = 'Chris Bergh'

from AnalyticContainer.AnalyticContainerLibrary.ACBase import *
from AnalyticContainer.AnalyticContainerLibrary.ACPythonAnaconda import *
ACHelpers.dump_env(False)

# ---------------------------------------------------------------------------------------------------------------------
# PythonAnaconda example container class:
# ---------------------------------------------------------------------------------------------------------------------
class PythonAnaconda(ACBase):
    anaconda = None

    def __init__(self):
        ACBase.__init__(self)
        self.python_anaconda = ACPythonAnaconda()
        self.config_dict = OrderedDict()

    def __str__(self):
        s = ''
        s += 'config_dict = %s' % json.dumps(self.config_dict, indent=4)
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
        except Exception, ex:
            ACLogger().get_logger().error('invalid json loaded to PythonAnaconda %s', ex.message)
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
        if self.is_valid_config() is False:
            ACLogger().get_logger().error('invalid PythonAnaconda json schema %s', self.config_dict)
            return False
        return True

    def is_valid_config(self):
        if self.config_dict is None:
            return False

        return True

    def execute_python_anaconda(self, jupyter_dir=None, notebook_file_dir=None):
        rv = False
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.set_progress('start-time', dt)
        key_values_dict = OrderedDict()
        rv = self.python_anaconda.execute(key_values_dict, jupyter_dir, notebook_file_dir)
        return_key_values_dict = OrderedDict()
        for key, val in key_values_dict.iteritems():
            if 'output' in val:
                return_key_values_dict[key] = val['output']
            else:
                return_key_values_dict[key] = None
            ACLogger.log_and_print('ACPythonAnaconda Logs for key %s *******************************************\n' % key)
            ACLogger.log_and_print('%s returned: status %s' % (key, val['status']))
            ACLogger.log_and_print('%s returned: output %s' % (key, val['output'] if 'output' in val else 'None'))
            ACLogger.log_and_print('%s\n' % val['log'])
            ACLogger.log_and_print('ACPythonAnaconda Logs for key %s *******************************************' % key)
            if ACHelpers.string_is_false(val['status']):
                rv = False
        self.set_progress(DKDATA_KEY, return_key_values_dict)
        self.set_progress('end-time', datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        return rv

def main(parser=None):
    ac_python_anaconda = PythonAnaconda()
    jupyter_dir = os.environ.get('jupyter_dir') # for debug
    notebook_file_dir = os.environ.get('notebook_file_dir') # for debug
    if ac_python_anaconda.python_anaconda.create_from_dict(ac_python_anaconda.configuration) is True :
        if ac_python_anaconda.execute_python_anaconda(jupyter_dir, notebook_file_dir) is True:
            ac_python_anaconda.set_container_status(CONTAINER_STATUS_SUCCESS)
            ACLogger.log_and_print('...PythonAnaconda:  Completed CONTAINER_STATUS_SUCCESS, exiting')
        else:
            ac_python_anaconda.set_container_status(CONTAINER_STATUS_ERROR)
            ACLogger.log_and_print('...PythonAnaconda:  Completed CONTAINER_STATUS_ERROR, exiting')
    else:
        ACLogger.log_and_print_error('PythonAnaconda: Exiting ... invalid config')
        ac_python_anaconda.set_container_status(CONTAINER_STATUS_ERROR)
    ac_python_anaconda.write_log()
    ac_python_anaconda.write_progress()


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description="Welcome to the PythonAnaconda Command Line Program")
    main(cmdline_parser)
