import os
import logging

# ---------------------------------------------------------------------------------------------------------------------
# logging
# ---------------------------------------------------------------------------------------------------------------------
#AC_LOGGING = logging.DEBUG
AC_LOGGING = logging.INFO
AC_LOG_FILE_LOCATION = './ac_logger.log'
AC_APPEND_MODE = 'a+'
AC_WRITE_MODE = 'w'

# ---------------------------------------------------------------------------------------------------------------------
# Input environment variables
# ---------------------------------------------------------------------------------------------------------------------
CONTAINER_INPUT_CONFIG_FILE_PATH = 'CONTAINER_INPUT_CONFIG_FILE_PATH'
CONTAINER_INPUT_CONFIG_FILE_NAME = 'CONTAINER_INPUT_CONFIG_FILE_NAME'
CONTAINER_INPUT_CONFIG_FILE_NAME = 'CONTAINER_INPUT_CONFIG_FILE_NAME'
CONTAINER_OUTPUT_PROGRESS_FILE = 'CONTAINER_OUTPUT_PROGRESS_FILE'
CONTAINER_OUTPUT_LOG_FILE = 'CONTAINER_OUTPUT_LOG_FILE'
CONTAINER_OUTPUT_FILE = 'CONTAINER_OUTPUT_FILE'
INSIDE_CONTAINER_FILE_MOUNT = 'INSIDE_CONTAINER_FILE_MOUNT'
INSIDE_CONTAINER_FILE_DIRECTORY = 'INSIDE_CONTAINER_FILE_DIRECTORY'

CONTAINER_REQUIRED_ENVIRONMENT_VARS = [INSIDE_CONTAINER_FILE_MOUNT, INSIDE_CONTAINER_FILE_DIRECTORY,
                                       CONTAINER_INPUT_CONFIG_FILE_PATH, CONTAINER_INPUT_CONFIG_FILE_NAME,
                                       CONTAINER_OUTPUT_PROGRESS_FILE, CONTAINER_OUTPUT_LOG_FILE]
# ENV Variable                      command line	                                        command line in container	    DKContainer Node
# ---------------------------------------------------------------------------------------------------------------------------------------------------------
# CONTAINER_INPUT_CONFIG_FILE_PATH	/vagrant/AnalyticContainers/ACBase/docker-share	docker-share	                /container-node/docker-share
# CONTAINER_INPUT_CONFIG_FILE_NAME	config.json	                                            config.json	                    config.json
# CONTAINER_OUTPUT_PROGRESS_FILE	progress.json	                                        progress.json	                progress.json
# CONTAINER_OUTPUT_LOG_FILE	        ams_logger.log	                                        ams_logger.log	                ams_logger.log
# INSIDE_CONTAINER_FILE_MOUNT	    /vagrant/AnalyticContainers/ACBase	            /ACBase	                /ACBase
# INSIDE_CONTAINER_FILE_DIRECTORY	docker-share	                                        docker-share	                docker-share

# ---------------------------------------------------------------------------------------------------------------------
# Return Status of Execution (place in progress.json at top level)
# ---------------------------------------------------------------------------------------------------------------------
CONTAINER_RETURN_STATUS = 'container-return-status'
CONTAINER_STATUS_SUCCESS = 'completed_success'  # -- all complete, go on to data sinks
CONTAINER_STATUS_ERROR = 'error'  # -- somethings wrong, stop processing
CONTAINER_STATUS_CONTINUE = 'continue_production'  # -- all good, but need to try again later
ALLOWED_CONTAINER_RETURN_STATUSES = [CONTAINER_STATUS_SUCCESS, CONTAINER_STATUS_ERROR, CONTAINER_STATUS_CONTINUE]

# ---------------------------------------------------------------------------------------------------------------------
# Tests (place in progress.json at top level)
# ---------------------------------------------------------------------------------------------------------------------
# for each test, below is how to add them to the progress.json
#  test_key (i.e. the test name
#  test data is a dict() containing several items for each test_key
#       CONTAINER_TEST_RESULT = Result of the test: ALLOWED_CONTAINER_TEST_RESULTS
#       CONTAINER_TEST_DATETIME = string datetime (always of last time this dict was set)
#       CONTAINER_TEST_LOGIC  = (string explaining test logic)
#       CONTAINER_TEST_ACTION = What the test is supposed to do -- desired action: ALLOWED_CONTAINER_TEST_ACTIONS
#       CONTAINER_TEST_VALUE_TYPE = The type of the data: ALLOWED_CONTAINER_TEST_TYPES
#       CONTAINER_TEST_VALUE = dict containing all the test variable names and values
#                   test variable name   (e.g. 'sql-data01-size'): list of values (of type ALLOWED_CONTAINER_TEST_TYPES)
#                   test variable name 2 (e.g. 'ftp-data02-size'): list of values (of type ALLOWED_CONTAINER_TEST_TYPES)
# ---------------------------------------------------------------------------------------------------------------------

CONTAINER_TEST_DATA = 'test-data'
# per test data
CONTAINER_TEST_RESULT = 'test-result'
CONTAINER_TEST_DATETIME = 'test-datetime'
CONTAINER_TEST_LOGIC = 'test-logic'
CONTAINER_TEST_ACTION = 'test-action'
CONTAINER_TEST_VALUE_TYPE = 'test-value-type'
CONTAINER_TEST_VALUE = 'test-value'
# Test Results
CONTAINER_TEST_RESULT_FAILED = 'TestFailed'
CONTAINER_TEST_RESULT_PASSED = 'TestPassed'
CONTAINER_TEST_RESULT_WARNING = 'TestWarning'
ALLOWED_CONTAINER_TEST_RESULTS = [CONTAINER_TEST_RESULT_FAILED, CONTAINER_TEST_RESULT_PASSED,
                                  CONTAINER_TEST_RESULT_WARNING]
# Desired Action for each test
CONTAINER_TEST_ACTION_LOG = 'log'
CONTAINER_TEST_ACTION_WARNING = 'warning'
CONTAINER_TEST_ACTION_STOP_ON_ERROR = 'stop-on-error'
ALLOWED_CONTAINER_TEST_ACTIONS = [CONTAINER_TEST_ACTION_LOG, CONTAINER_TEST_ACTION_WARNING,
                                  CONTAINER_TEST_ACTION_STOP_ON_ERROR]
# test data types
CONTAINER_TEST_VALUE_INT = 'type-int'
CONTAINER_TEST_VALUE_STRING = 'type-string'
CONTAINER_TEST_VALUE_FLOAT = 'type-float'
CONTAINER_TEST_VALUE_DATE = 'type-date'
CONTAINER_TEST_VALUE_UNKNOWN_TYPE = 'type-unknown'
ALLOWED_CONTAINER_TEST_TYPES = [CONTAINER_TEST_VALUE_INT, CONTAINER_TEST_VALUE_STRING, CONTAINER_TEST_VALUE_FLOAT,
                                CONTAINER_TEST_VALUE_DATE, CONTAINER_TEST_VALUE_UNKNOWN_TYPE]

# ---------------------------------------------------------------------------------------------------------------------
# posrgres settings
# ---------------------------------------------------------------------------------------------------------------------
# this is just a copy from DKDataPostrges
# DKData PostgreSQL (Redshift)
DKDATA_TYPE = 'type'
DKDATA_NAME = 'name'
DKDATA_KEY = 'keys'
MSSQL_SCHEMA_COMPLETE_CHECK_KEY = 'complete'
MSSQL_TYPE_EXECUTE_SCALAR = 'execute_scalar'
MSSQL_TYPE_EXECUTE_ROW = 'execute_row'
MSSQL_TYPE_EXECUTE_QUERY = 'execute_query'
MSSQL_TYPE_EXECUTE_NON_QUERY = 'execute_non_query'
MSSQL_TYPE = 'query-type'
POSTGRESQL_SCHEMA_USERNAME = 'username'
POSTGRESQL_SCHEMA_PASSWORD = 'password'
POSTGRESQL_SCHEMA_HOSTNAME = 'hostname'
POSTGRESQL_SCHEMA_DATABASE = 'database'
POSTGRESQL_TYPE = MSSQL_TYPE
POSTGRESQL_SCHEMA_PORT = 'port'
POSTGRESQL_SCHEMA_KEY = DKDATA_KEY
POSTGRESQL_STATEMENTS = DKDATA_KEY
POSTGRESQL_SQL_STRING = 'sql'
POSTGRESQL_FETCH_ROWS = 'fetch-rows'
POSTGRESQL_DEFAULT_FETCH_ROWS = 1000
POSTGRESQL_IGNORE_EXCEPTIONS = 'ignore-errors'
POSTGRESQL_INSERT_COLUMN_NAMES = 'insert-column-names'
POSTGRESQL_SQL_PARSER = 'parser'
POSTGRESQL_SQL_TO_JSON_PARSER = 'to-json-parser'
# for returning an integer value form a query
# calls cur.execute() with cur.statusmessage
POSTGRESQL_TYPE_EXECUTE_SCALAR = MSSQL_TYPE_EXECUTE_SCALAR
# for sql that work or not without a return value
# (e.g. INSERT INTO TEST01 (col01, col02, col03) VALUES $value_list;
#   CREATE TABLE )
# uses cur.execute
POSTGRESQL_TYPE_EXECUTE_NON_QUERY = MSSQL_TYPE_EXECUTE_NON_QUERY
# for query based sql that returns a results set
# (e.g. SELECT * FROM persons WHERE ... )
POSTGRESQL_TYPE_EXECUTE_QUERY = MSSQL_TYPE_EXECUTE_QUERY
# for query based sql that returns a single row result
# (e.g. "SELECT * FROM employees WHERE id=%d", 13)
POSTGRESQL_TYPE_EXECUTE_ROW = MSSQL_TYPE_EXECUTE_ROW
# for an autocommit=true query (like VACUUM)
# and sql that work or not without a return value
# http://stackoverflow.com/questions/1017463/postgresql-how-to-run-vacuum-from-code-outside-transaction-block
POSTGRESQL_TYPE_EXECUTE_LOW_ISOLATION_QUERY = 'execute_low_isolation_non_query'
# used to insert data from a file into the database
POSTGRESQL_TYPE_COPY_FROM = 'execute_copy_from'
POSTGRESQL_COPY_DELIMITER = 'delimiter'
POSTGRESQL_COPY_DELIMITER_DEFAULT = ','
POSTGRESQL_COPY_NULL = 'null'
POSTGRESQL_COPY_BUFFER_SIZE = 'buffer-size'
POSTGRESQL_COPY_BUFFER_SIZE_DEFAULT = 8192
POSTGRE_EXEC_TYPES = [POSTGRESQL_TYPE_EXECUTE_SCALAR, POSTGRESQL_TYPE_EXECUTE_NON_QUERY,
                      POSTGRESQL_TYPE_EXECUTE_QUERY, POSTGRESQL_TYPE_EXECUTE_ROW,
                      POSTGRESQL_TYPE_COPY_FROM, POSTGRESQL_TYPE_EXECUTE_LOW_ISOLATION_QUERY]

# ----------------------------------------------------------------------------------------------------
# email
# ---------------------------------------------------------------------------------------------------------------------
AC_EMAIL_FROM = 'ac-test<cbergh@datakitchen.io>'
AC_EMAIL_ASCII_SENDER = 'Ascii Sender <no_reply@datakitchen.io>'

S3_SCHEMA_ACCESS_KEY = 's3-access-key'
S3_SCHEMA_SECRET_KEY = 's3-secret-key'
AC_EMAIL_SUBJECT = 'emailsubject'
AC_EMAIL_LIST = 'email-recipient-list'
AC_EMAIL_TEMPLATE_LOCATION = 'email-template'
AC_EMAIL_TEST_GT = 'greater-than'
AC_EMAIL_TEST_LT = 'less-than'
AC_EMAIL_TEST_EQUAL_TO = 'equal-to'
AC_EMAIL_TEST_TYPES = [AC_EMAIL_TEST_GT, AC_EMAIL_TEST_LT, AC_EMAIL_TEST_EQUAL_TO]
AC_EMAIL_SEND_TEST = 'send-email-test'
AC_EMAIL_COUNT_KEY = 'count-key'
AC_EMAIL_TEST_LOGIC = 'test-logic'
AC_EMAIL_TEST_VALUE = 'test-value'
AC_EMAIL_TEST_RESULTS = 'testresults'

# ----------------------------------------------------------------------------------------------------
# tableau
# ----------------------------------------------------------------------------------------------------
TABLEAU_TYPE = DKDATA_TYPE
TABLEAU_SERVER_USERNAME = 'username'
TABLEAU_SERVER_PASSWORD = 'password'
TABLEAU_SERVER_URL = 'url'
TABLEAU_SERVER_SCHEMA_PORT = 'port'
TABLEAU_SERVER_KEYS = DKDATA_KEY
TABLEAU_UPSERT = 'upsert-workbook'
TABLEAU_PROJECT_NAME = 'project-name'
TABLEAU_CONTENT_NAME = 'twb-content-name'
TABLEAU_WORKBOOK_NAME = 'twb-filename'
TABLEAU_DATASOURCE_WORKBOOK_NAME = 'project-datasource-twb'
TABLEAU_VIEW_NAME = 'twb-view-name'
TABLEAU_DOWNLOAD_CSV = 'download-crosstab-csv'
TABLEAU_SELENIUM_URL = 'selenium-url'

# ----------------------------------------------------------------------------------------------------
# PentahoDI
# ----------------------------------------------------------------------------------------------------
PENTAHODI_TYPE = DKDATA_TYPE
PENTAHODI_LOGLEVEL = 'loglevel'
PENTAHODI_FILENAME = 'filename'
PENTAHODI_FILE_PARAMETERS = 'file-parameters'
PENTAHODI_KEYS = DKDATA_KEY
PENTAHODI_INTEGRATION_OUTPUT_FILENAME = 'integration-output-filename'
# ----------------------------------------------------------------------------------------------------
# Python Anaconda
# ----------------------------------------------------------------------------------------------------
PYTHON_ANACONDA_TYPE = DKDATA_TYPE
PYTHON_ANACONDA_FILENAME = 'filename'
PYTHON_ANACONDA_FILE_PARAMETERS = 'file-parameters'
PYTHON_ANACONDA_NOTEBOOK_OUTPUT_FILENAME = 'notebook-output-filename'
PYTHON_ANACONDA_KEYS = DKDATA_KEY