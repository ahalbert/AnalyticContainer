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
from AnalyticContainer.AnalyticContainerLibrary.ACEmail import *
#
TEMPFILE_LOCATION = '/var/tmp'
# ---------------------------------------------------------------------------------------------------------------------
# CheckTableAndEmail example container class:
# ---------------------------------------------------------------------------------------------------------------------
class CheckTableAndEmail(ACBase):
    postgres = None
    emailer = None

    def __init__(self):
        ACBase.__init__(self)
        self.postgres = ACPostgreSQL()
        self.emailer = ACAWSEmailSender()
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
            ACLogger().get_logger().error('invalid json loaded to ACEmailSender %s', ex.message)
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
            ACLogger().get_logger().error('invalid CheckTableAndEmail json schema %s', self.config_dict)
            return False
        return True

    def is_valid_config(self):
        if self.config_dict is None:
            return False
        if AC_EMAIL_SEND_TEST not in self.config_dict:
            return False
        if AC_EMAIL_LIST not in self.config_dict:
            return False
        if isinstance(self.config_dict[AC_EMAIL_LIST], basestring):
            em = self.config_dict[AC_EMAIL_LIST]
            self.config_dict[AC_EMAIL_LIST] = list()
            self.config_dict[AC_EMAIL_LIST].append(em)
        elif isinstance(self.config_dict[AC_EMAIL_LIST], list):
            if len(self.config_dict[AC_EMAIL_LIST]) == 0:
                return False
        else:
            return False
        if AC_EMAIL_SUBJECT not in self.config_dict:
            self.config_dict[AC_EMAIL_SUBJECT] = "Check Table And Send Email"
        if AC_EMAIL_COUNT_KEY not in self.config_dict[AC_EMAIL_SEND_TEST]:
            return False
        if AC_EMAIL_TEST_LOGIC not in self.config_dict[AC_EMAIL_SEND_TEST]:
            return False
        if self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_TEST_LOGIC] not in AC_EMAIL_TEST_TYPES:
            return False
        if AC_EMAIL_TEST_VALUE not in self.config_dict[AC_EMAIL_SEND_TEST]:
            return False
        if isinstance(self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_TEST_VALUE], int):
            pass
        elif isinstance(self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_TEST_VALUE], basestring):
            try:
                self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_TEST_VALUE] = int(self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_TEST_VALUE])
            except Exception:
                return False
        else:
            return False
        return True

    def get_ac_postgres(self):
        return self.postgres

    def get_emailer(self):
        return self.emailer

    def execute(self):
        send_it = False
        template = None
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.set_progress('start-time', dt)
        if DKDATA_KEY in self.postgres.config_dict and \
                        isinstance(self.postgres.config_dict[DKDATA_KEY], dict) is True and \
                        self.postgres.connect() is True and \
                        self.emailer.is_valid_config() is True:
            sub_dict = dict()
            for key_name, val in self.postgres.config_dict.iteritems():
                if key_name != DKDATA_KEY:
                    sub_dict[key_name] = val
            for key_name, query in self.postgres.config_dict[DKDATA_KEY].iteritems():
                temp = tempfile.NamedTemporaryFile(dir=TEMPFILE_LOCATION)
                if temp is not None:
                    st = ['']
                    if self.postgres.postgres_execute(key_name, temp.file) is True:
                        temp.seek(0)
                        st[0] = temp.read()
                        temp.close()
                        sub_dict[key_name] = st[0]
                    else:
                        self.set_progress(key_name, 'failed')
                else:
                    return False

            try:
                statinfo = os.stat(self.emailer.config_dict[AC_EMAIL_TEMPLATE_LOCATION])
            except:
                statinfo = None
            else:
                if statinfo is not None and statinfo.st_size > 0:
                    with open(self.emailer.config_dict[AC_EMAIL_TEMPLATE_LOCATION], 'r') as rfile:
                        rfile.seek(0)
                        template = string.Template(rfile.read())

            if template is None:
                ACLogger().get_logger().error(
                    'unable to open email template %s in cwd=(%s)' % (self.config_dict[AC_EMAIL_TEMPLATE_LOCATION], os.getcwd()))
                return False

            if self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_COUNT_KEY] not in sub_dict:
                ACLogger().get_logger().error('unable to to find key %s' % self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_COUNT_KEY])
                return False

            the_database_test_val = sub_dict[self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_COUNT_KEY]]
            if isinstance(the_database_test_val, int) is True:
                pass
            elif isinstance(the_database_test_val, basestring):
                try:
                    the_database_test_val = int(the_database_test_val)
                except Exception:
                    ACLogger().get_logger().error('unable to get test val')
                    return False
            else:
                return False

            if self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_TEST_LOGIC] == AC_EMAIL_TEST_GT:
                if the_database_test_val > self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_TEST_VALUE]:
                    send_it = True
            elif self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_TEST_LOGIC] == AC_EMAIL_TEST_LT:
                if the_database_test_val < self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_TEST_VALUE]:
                    send_it = True
            elif self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_TEST_LOGIC] == AC_EMAIL_TEST_EQUAL_TO:
                if the_database_test_val == self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_TEST_VALUE]:
                    send_it = True
            else:
                send_it = False
            self.set_progress('variables', sub_dict)
            sub_dict[AC_EMAIL_TEST_RESULTS] = '%s(%d) %s %s' % (self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_COUNT_KEY],
                                                        the_database_test_val,
                                                        self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_TEST_LOGIC],
                                                        self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_TEST_VALUE])
            self.set_test_results(self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_COUNT_KEY],
                                  self.config_dict[AC_EMAIL_SEND_TEST][AC_EMAIL_TEST_LOGIC],
                                  send_it, sub_dict[AC_EMAIL_TEST_RESULTS])

            if send_it is True and self.emailer.apply_template_and_send_email(template,
                                                          self.emailer.config_dict[AC_EMAIL_LIST], sub_dict,
                                                          self.emailer.config_dict[AC_EMAIL_SUBJECT], None) is False:
                ACLogger().get_logger().error('unable to send completion email')
            rv = True
        else:
            rv = False
        self.set_progress('end-time', datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

        return rv

def main(parser=None):
    ac_check_table = CheckTableAndEmail()
    if ac_check_table.vaild_config() is True and \
                    ac_check_table.create_from_dict(ac_check_table.configuration) is True and \
                    ac_check_table.postgres.create_from_dict(ac_check_table.configuration) is True and \
                    ac_check_table.emailer.create_from_dict(ac_check_table.configuration) is True:
        ACLogger.log_and_print('...CheckTableAndEmail config:  %s' % ac_check_table.__str__())
        if ac_check_table.parse_command_line(parser) is True:
            if ac_check_table.execute() is True:
                ac_check_table.set_container_status(CONTAINER_STATUS_SUCCESS)
                ACLogger.log_and_print('...CheckTableAndEmail:  Completed CONTAINER_STATUS_SUCCESS, exiting')
            else:
                ac_check_table.set_container_status(CONTAINER_STATUS_ERROR)
                ACLogger.log_and_print('...CheckTableAndEmail:  Completed CONTAINER_STATUS_ERROR, exiting')
        else:
            ACLogger.log_and_print_error('CheckTableAndEmail: Exiting ... invalid command line')
    else:
        ACLogger.log_and_print_error('CheckTableAndEmail: Exiting ... invalid config')
        ac_check_table.set_container_status(CONTAINER_STATUS_ERROR)
    ac_check_table.write_log()
    ac_check_table.write_progress()


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description="Welcome to the CheckTableAndEmail Command Line Program")
    main(cmdline_parser)
