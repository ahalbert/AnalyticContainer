__author__ = 'Chris Bergh'
import sys
import shutil
import tempfile
import string

def dump_env(de):
    if de is True:
        print("DUMPING ENV ...........")
        for key in os.environ.keys():
            print "%s: %s \n" % (key, os.environ[key])
        print("sys.path: %s \n" % sys.path)
        print("os.cwd: %s \n" % os.getcwd())
dump_env(False)
from AnalyticContainer.AnalyticContainerLibrary.ACBase import *
from AnalyticContainer.AnalyticContainerLibrary.ACPostgresSQL import *
#
TEMPFILE_LOCATION = '/var/tmp'
# ---------------------------------------------------------------------------------------------------------------------
# PostgresContainer example container class:
# ---------------------------------------------------------------------------------------------------------------------
class PostgresContainer(ACBase):
    postgres = None

    def __init__(self):
        ACBase.__init__(self)
        self.postgres = ACPostgreSQL()
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
            ACLogger().get_logger().error('invalid json loaded to PostgresContainer %s', ex.message)
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
            ACLogger().get_logger().error('invalid PostgresContainer json schema %s', self.config_dict)
            return False
        return True

    def is_valid_config(self):
        if self.config_dict is None:
            return False

        return True

    def get_ac_postgres(self):
        return self.postgres


    def execute(self):
        write_variables_to_progess = False
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.set_progress('start-time', dt)
        if DKDATA_KEY in self.postgres.config_dict and \
                        isinstance(self.postgres.config_dict[DKDATA_KEY], dict) is True and \
                        self.postgres.connect() is True:
            if write_variables_to_progess is True:
                variables_dict = dict()
                for key_name, val in self.postgres.config_dict.iteritems():
                    if key_name != DKDATA_KEY:
                        variables_dict[key_name] = val
                self.set_progress('variables', variables_dict)
            key_values_dict = OrderedDict()
            for key_name, query in self.postgres.config_dict[DKDATA_KEY].iteritems():
                temp = tempfile.NamedTemporaryFile(dir=TEMPFILE_LOCATION)
                if temp is not None:
                    st = ['']
                    if self.postgres.postgres_execute(key_name, temp.file) is True:
                        temp.seek(0)
                        st[0] = temp.read()
                        temp.close()
                        key_values_dict[key_name] = ACHelpers.compress(st[0])
                    else:
                        key_values_dict[key_name] = None
                else:
                    return False
            self.set_progress(DKDATA_KEY, key_values_dict)
            rv = True
        else:
            rv = False
        self.set_progress('end-time', datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

        return rv

def main(parser=None):
    ac_postgres_container = PostgresContainer()
    if ac_postgres_container.vaild_config() is True and \
                    ac_postgres_container.create_from_dict(ac_postgres_container.configuration) is True and \
                    ac_postgres_container.postgres.create_from_dict(ac_postgres_container.configuration) is True :
        if ac_postgres_container.parse_command_line(parser) is True:
            if ac_postgres_container.execute() is True:
                ac_postgres_container.set_container_status(CONTAINER_STATUS_SUCCESS)
                ACLogger.log_and_print('...PostgresContainer:  Completed CONTAINER_STATUS_SUCCESS, exiting')
            else:
                ac_postgres_container.set_container_status(CONTAINER_STATUS_ERROR)
                ACLogger.log_and_print('...PostgresContainer:  Completed CONTAINER_STATUS_ERROR, exiting')
        else:
            ACLogger.log_and_print_error('PostgresContainer: Exiting ... invalid command line')
    else:
        ACLogger.log_and_print_error('PostgresContainer: Exiting ... invalid config')
        ac_postgres_container.set_container_status(CONTAINER_STATUS_ERROR)
    ac_postgres_container.write_log()
    ac_postgres_container.write_progress()


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description="Welcome to the PostgresContainer Command Line Program")
    main(cmdline_parser)
