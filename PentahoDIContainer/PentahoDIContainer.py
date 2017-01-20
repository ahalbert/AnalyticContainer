__author__ = 'Chris Bergh'
import os
import sys
import shutil
import tempfile
import string
import copy
if not '/dk' in sys.path:
    sys.path.insert(0, '/dk' )
if not '/dk/AnalyticContainer' in sys.path:
    sys.path.insert(0, '/dk/AnalyticContainer')
if not '/dk/AnalyticContainer/AnalyticContainerLibrary' in sys.path:
    sys.path.insert(0, '/dk/AnalyticContainer/AnalyticContainerLibrary')
def dump_env(de):
    if de is True:
        print("DUMPING ENV ...........")
        for key in os.environ.keys():
            print "%s: %s \n" % (key, os.environ[key])
        print("sys.path: %s \n" % sys.path)
        print("os.cwd: %s \n" % os.getcwd())
dump_env(False)
from AnalyticContainer.AnalyticContainerLibrary.ACBase import *
from AnalyticContainer.AnalyticContainerLibrary.ACPentahoDI import *
#
TEMPFILE_LOCATION = '/var/tmp'
# ---------------------------------------------------------------------------------------------------------------------
# PentahoDIContainer container class:
# ---------------------------------------------------------------------------------------------------------------------
class PentahoDIContainer(ACBase):
    PentahoDI = None

    def __init__(self):
        ACBase.__init__(self)
        self.PentahoDI = ACPentahoDI()

    def __str__(self):
        s = ''
        s += 'config_dict = %s' % json.dumps(self.PentahoDI.config_dict, indent=4)
        return s

    def get_ac_pentahodi(self):
        return self.PentahoDI

    def execute_pdi(self, pdi_path, pdi_file_dir=None):
        rv = False
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.set_progress('start-time', dt)
        key_values_dict = OrderedDict()
        rv = self.PentahoDI.execute(key_values_dict, pdi_path, pdi_file_dir)
        return_key_values_dict = OrderedDict()
        for key, val in key_values_dict.iteritems():
            return_key_values_dict[key] = val['output']
            ACLogger.log_and_print('PentahoDI Logs for key %s *******************************************\n' % key)
            ACLogger.log_and_print('%s returned: status %s' % (key, val['status']))
            ACLogger.log_and_print('%s returned: output %s' % (key, val['output']))
            ACLogger.log_and_print('%s\n' % val['log'])
            ACLogger.log_and_print('PentahoDI Logs for key %s *******************************************' % key)
        self.set_progress(DKDATA_KEY, return_key_values_dict)
        self.set_progress('end-time', datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        return rv

def main(parser=None):
    if parser is None:
        parser = argparse.ArgumentParser(description="Welcome to the PentahoDIContainer Command Line Program")
    ac_pentahodi_container = PentahoDIContainer()
    pdi_path = os.environ.get('pdi_home') # for debug
    pdi_file_dir = os.environ.get('pdi_file_dir') # for debug
    if pdi_path is not None:
        if ac_pentahodi_container.PentahoDI.create_from_dict(ac_pentahodi_container.configuration) is True:
            if ac_pentahodi_container.execute_pdi(pdi_path, pdi_file_dir) is True:
                ACLogger.log_and_print('...PentahoDIContainer:  Completed CONTAINER_STATUS_SUCCESS, exiting')
                ac_pentahodi_container.set_container_status(CONTAINER_STATUS_SUCCESS)
            else:
                ACLogger.log_and_print('...PentahoDIContainer:  Completed CONTAINER_STATUS_ERROR, exiting')
                ac_pentahodi_container.set_container_status(CONTAINER_STATUS_ERROR)
        else:
            ACLogger.log_and_print_error('PentahoDIContainer: Exiting ... unable to create from config')
            ac_pentahodi_container.set_container_status(CONTAINER_STATUS_ERROR)
    else:
        ACLogger.log_and_print_error('PentahoDIContainer: Exiting ... requires pdi_path environment variable setup')
        ac_pentahodi_container.set_container_status(CONTAINER_STATUS_ERROR)
    ac_pentahodi_container.write_log()
    ac_pentahodi_container.write_progress()


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description="Welcome to the PentahoDIContainer Command Line Program")
    main(cmdline_parser)
