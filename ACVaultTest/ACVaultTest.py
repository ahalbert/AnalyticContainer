__author__ = 'Chris Bergh'
import os
import sys
import shutil
import argparse

from AnalyticContainer.AnalyticContainerLibrary.ACBase import *

# ---------------------------------------------------------------------------------------------------------------------
# ACVaultTest example container class:
# ---------------------------------------------------------------------------------------------------------------------
class ACVaultTest(ACBase):
    def __init__(self):
        ACBase.__init__(self)

    def execute(self):
        self.set_progress('vault-config',self.configuration['secret'])
        self.set_progress('vault-value',ACHelpers.secret_resolve(self.configuration['secret']))

def main(parser=None):
    ac_example1 = ACVaultTest()
    if ac_example1.vaild_config() is True:
        if ac_example1.set_test_results('example-test-name-1', CONTAINER_TEST_ACTION_WARNING,
                                     CONTAINER_TEST_RESULT_PASSED, "example-test-1 != 0") is False or \
            ac_example1.add_test_result_value('example-test-name-1',
                                              CONTAINER_TEST_VALUE_INT, 'example-test-1', 0) is False:
            ACLogger.log_and_print_error('unable to set test results')
            ac_example1.set_container_status(CONTAINER_STATUS_ERROR)

        ac_example1.execute()

        if ac_example1.parse_command_line(parser) is True:
            ac_example1.set_container_status(CONTAINER_STATUS_SUCCESS)
            ACLogger.log_and_print('...ACVaultTest:  Completed command, exiting')
        else:
            ACLogger.log_and_print_error('ACVaultTest: Exiting ... invalid command line')
    else:
        ACLogger.log_and_print_error('ACVaultTest: Exiting ... invalid config')
        ac_example1.set_container_status(CONTAINER_STATUS_ERROR)
    ac_example1.write_log()
    ac_example1.write_progress()


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description="Welcome to the ACVaultTest Command Line Program")
    main(cmdline_parser)
