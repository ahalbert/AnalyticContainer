__author__ = 'Chris Bergh'
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
from AnalyticContainer.AnalyticContainerLibrary.ACTableau import *
#
TEMPFILE_LOCATION = '/var/tmp'
# ---------------------------------------------------------------------------------------------------------------------
# TableauContainer example container class:
# ---------------------------------------------------------------------------------------------------------------------
class TableauContainer(ACBase):
    tableau = None

    def __init__(self):
        ACBase.__init__(self)
        self.tableau = ACTableau()

    def __str__(self):
        s = ''
        s += 'config_dict = %s' % json.dumps(self.tableau.config_dict, indent=4)
        return s

    def get_ac_tableau(self):
        return self.tableau

    def execute(self):
        rv = False
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.set_progress('start-time', dt)
        key_values_dict = OrderedDict()
        rv = self.tableau.execute(key_values_dict, self.inside_docker_share_dir)
        self.set_progress(DKDATA_KEY, key_values_dict)
        self.set_progress('end-time', datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        return rv

def main(parser=None):
    ac_tableau_container = TableauContainer()
    if  ac_tableau_container.tableau.create_from_dict(ac_tableau_container.configuration) is True:
        if ac_tableau_container.parse_command_line(parser) is True:
            if ac_tableau_container.execute() is True:
                ac_tableau_container.set_container_status(CONTAINER_STATUS_SUCCESS)
                ACLogger.log_and_print('...TableauContainer:  Completed CONTAINER_STATUS_SUCCESS, exiting')
            else:
                ac_tableau_container.set_container_status(CONTAINER_STATUS_ERROR)
                ACLogger.log_and_print('...TableauContainer:  Completed CONTAINER_STATUS_ERROR, exiting')
        else:
            ACLogger.log_and_print_error('TableauContainer: Exiting ... invalid command line')
    else:
        ACLogger.log_and_print_error('TableauContainer: Exiting ... invalid config')
        ac_tableau_container.set_container_status(CONTAINER_STATUS_ERROR)
    ac_tableau_container.write_log()
    ac_tableau_container.write_progress()


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description="Welcome to the TableauContainer Command Line Program")
    main(cmdline_parser)
