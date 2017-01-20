__author__ = 'Chris Bergh'
import sys
import json
import argparse
from datetime import datetime
from collections import OrderedDict
import traceback
import shutil

from AnalyticContainer.AnalyticContainerLibrary.ACSingletons import ACLogger,ACHelpers
from AnalyticContainer.AnalyticContainerLibrary.ACSettings import *


# ---------------------------------------------------------------------------------------------------------------------
# ACBase  container class:
# ---------------------------------------------------------------------------------------------------------------------
class ACBase(object):
    def __init__(self):
        self.valid_configuration = True
        self.env_vars = dict()
        self.inside_progess_file = None
        self.inside_log_file = None
        self.inside_config_file = None
        self.configuration = None
        self.inside_docker_share_dir = None
        self.progress = OrderedDict()
        self.return_status = CONTAINER_STATUS_ERROR

        for var in CONTAINER_REQUIRED_ENVIRONMENT_VARS:
            the_var_value = os.environ.get(var)
            if the_var_value is None:
                ACLogger.log_and_print_error('ACBase:  unable to open access env variable: %s' % var)
                self.valid_configuration = False
            self.env_vars[var] = the_var_value

        if self.valid_configuration is True:
            self.inside_progess_file = os.path.join(self.env_vars[INSIDE_CONTAINER_FILE_MOUNT],
                                                    self.env_vars[INSIDE_CONTAINER_FILE_DIRECTORY],
                                                    self.env_vars[CONTAINER_OUTPUT_PROGRESS_FILE])

            self.inside_log_file = os.path.join(self.env_vars[INSIDE_CONTAINER_FILE_MOUNT],
                                                self.env_vars[INSIDE_CONTAINER_FILE_DIRECTORY],
                                                self.env_vars[CONTAINER_OUTPUT_LOG_FILE])

            self.inside_config_file = os.path.join(self.env_vars[INSIDE_CONTAINER_FILE_MOUNT],
                                                   self.env_vars[INSIDE_CONTAINER_FILE_DIRECTORY],
                                                   self.env_vars[CONTAINER_INPUT_CONFIG_FILE_NAME])
            self.inside_docker_share_dir = os.path.join(self.env_vars[INSIDE_CONTAINER_FILE_MOUNT],
                                                   self.env_vars[INSIDE_CONTAINER_FILE_DIRECTORY])
            try:
                with open(self.inside_config_file) as the_file:
                    self.configuration = json.load(the_file, object_pairs_hook=OrderedDict)
                    ACHelpers.resolve_secrets(self.configuration)
            except (IOError, ValueError), e:
                s = 'ACBase:  unable to load config.json  %s %s' % (type(e), e.args)
                self.valid_configuration = False
                ACLogger.log_and_print_error(s)

        if os.path.isdir(self.inside_docker_share_dir) is False:
            s = 'ACBase:  docker share dir does not exist %s' % self.inside_docker_share_dir
            self.valid_configuration = False
            ACLogger.log_and_print_error(s)

    def __str__(self):
        s = 'ACBase: \n' + ' '
        for var in CONTAINER_REQUIRED_ENVIRONMENT_VARS:
            s += 'env_var[%s]=%s \n' % (var, self.env_vars[var]) + ' '
        s += 'input config_file_path = %s \n' % str(self.inside_config_file) + ' '
        s += 'input file(s) share dir = %s \n' % str(self.inside_docker_share_dir) + ' '
        s += 'output progess_file_path = %s \n' % str(self.inside_progess_file) + ' '
        s += 'output log_file_path = %s \n' % str(self.inside_log_file) + ' '
        s += 'the input config file = %s \n' % self.configuration
        return s

    def vaild_config(self):
        return self.valid_configuration

    def print_config(self):
        print self.__str__()

    def get_progress(self):
        return self.progress

    def set_progress(self, key, value):
        self.progress[key] = value

    def write_progress(self):
        try:
            with open(self.inside_progess_file, 'w') as the_file:
                the_file.write(json.dumps(self.get_progress(), indent=4))
        except (IOError, ValueError), e:
            s = 'ACBase:  unable to write_progress.json  %s %s' % (type(e), e.args)
            ACLogger.log_and_print_error(s)

    def write_log(self):
        try:
            shutil.copyfile(AC_LOG_FILE_LOCATION, self.inside_log_file)
        except IOError:
            ACLogger.log_and_print_error('ACBAse: unable to move log file from %s to %s' %
                                         (AC_LOG_FILE_LOCATION, self.inside_log_file))

    def parse_command_line(self, parser):
        try:
            if parser is not None:
                mutually_exclusive_group = parser.add_mutually_exclusive_group()
                mutually_exclusive_group.add_argument('--rude', '-rude', action='store_true', default=False, dest='rude',
                                                      help='Return something rude')
                results = parser.parse_args()
                if results.rude is True:
                    ACLogger.log_and_print("ACBase ... print rude words")
        except argparse.ArgumentError as e:
            s = 'ACBase:  During processing, caught an unknown exception. type: %s ; args: %s ; message: %s' % (
            type(e), repr(e.args), e.message)
            ACLogger.log_and_print_error(s)
            self.set_container_status(CONTAINER_STATUS_ERROR)
            return False
        except Exception as e:
            s = 'ACBase:  During processing, caught an unknown exception:  %s %s' % (type(e), e.args)
            ACLogger.log_and_print_error(s)
            self.set_container_status(CONTAINER_STATUS_ERROR)
            return False

        return True

    def set_test_results(self, test_key, test_action, test_result, test_logic_str):
        """
        Set the test value in the progress.json dictionary

        @param test_key: the test name
        @param test_action: Result of the test: ALLOWED_CONTAINER_TEST_RESULTS
        @param test_result: What the test is supposed to do with the result: ALLOWED_CONTAINER_TEST_ACTIONS
        @param test_logic_str: string explaining the test logic

        @return: True/False
       """
        if test_key is None:
            return False
        if test_action not in ALLOWED_CONTAINER_TEST_ACTIONS:
            return False
        if test_result not in ALLOWED_CONTAINER_TEST_RESULTS:
            return False

        if CONTAINER_TEST_DATA not in self.progress:
            self.progress[CONTAINER_TEST_DATA] = OrderedDict()

        if test_key not in self.progress[CONTAINER_TEST_DATA]:
            self.progress[CONTAINER_TEST_DATA][test_key] = OrderedDict()

        self.progress[CONTAINER_TEST_DATA][test_key][CONTAINER_TEST_ACTION] = test_action
        self.progress[CONTAINER_TEST_DATA][test_key][CONTAINER_TEST_RESULT] = test_result
        self.progress[CONTAINER_TEST_DATA][test_key][CONTAINER_TEST_LOGIC] = test_logic_str
        self.progress[CONTAINER_TEST_DATA][test_key][CONTAINER_TEST_DATETIME] = \
            datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        return True

    def add_test_result_value(self, test_key, test_variable_value_type, test_variable_name, test_variable_value):
        """
        Set the test value in the progress.json dictionary

        @param test_key: the test name
        @param test_variable_value_type: The type of the data: ALLOWED_CONTAINER_TEST_TYPES
        @param test_variable_name: name of test variable
        @param test_variable_value:value of test variable (of type ALLOWED_CONTAINER_TEST_TYPES)

        @return: True/False
       """
        if test_key is None:
            return False
        if test_variable_value_type not in ALLOWED_CONTAINER_TEST_TYPES:
            return False
        if test_variable_name is None:
            return False
        if CONTAINER_TEST_DATA not in self.progress or \
                        test_key not in self.progress[CONTAINER_TEST_DATA] or \
                        isinstance(self.progress[CONTAINER_TEST_DATA][test_key], dict) is False:
            return False

        self.progress[CONTAINER_TEST_DATA][test_key][CONTAINER_TEST_VALUE_TYPE] = test_variable_value_type
        if CONTAINER_TEST_VALUE not in self.progress[CONTAINER_TEST_DATA][test_key]:
            self.progress[CONTAINER_TEST_DATA][test_key][CONTAINER_TEST_VALUE] = OrderedDict()
        if test_variable_name not in self.progress[CONTAINER_TEST_DATA][test_key][CONTAINER_TEST_VALUE]:
            self.progress[CONTAINER_TEST_DATA][test_key][CONTAINER_TEST_VALUE] = OrderedDict()
            self.progress[CONTAINER_TEST_DATA][test_key][CONTAINER_TEST_VALUE][test_variable_name] = list()
        self.progress[CONTAINER_TEST_DATA][test_key][CONTAINER_TEST_VALUE][test_variable_name].append(
            test_variable_value)

        return True

    def set_container_status(self, result_status):
        if result_status not in ALLOWED_CONTAINER_RETURN_STATUSES:
            self.progress[CONTAINER_RETURN_STATUS] = CONTAINER_STATUS_ERROR
        else:
            self.progress[CONTAINER_RETURN_STATUS] = result_status

    def execute(self):
        if self.valid_configuration is True:
            ACLogger.log_and_print('ACBase: Executing ....')
        else:
            ACLogger.log_and_print('ACBase: Invalid Config')
        self.write_progress()




