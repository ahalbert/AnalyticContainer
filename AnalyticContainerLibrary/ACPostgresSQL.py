
__author__ = 'Chris Bergh'
import sys
import json
from datetime import datetime
from collections import OrderedDict
import psycopg2
from AnalyticContainer.AnalyticContainerLibrary.ACSingletons import ACLogger, ACHelpers
from AnalyticContainer.AnalyticContainerLibrary.ACSettings import *

class ACPostgreSQLUtils(object):
    def __init__(self):
        pass
    @staticmethod
    def flatten(tlist):
        """Flattens list of tuples l."""
        return map(lambda x: x[0], tlist)

    #http://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable-in-python
    @staticmethod
    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, datetime):
            serial = obj.isoformat()
            return serial

class ACPostgreSQL(object):
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
            ACLogger().get_logger().error('invalid json loaded to ACPostgreSQL %s', ex.message)
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
        if self.is_valid_postgres_schema() is False:
            return False

        if self.conn is not None and self.conn.closed == 0:
            return True
        try:
            svr = ACHelpers.resolve_vault_references(self.config_dict[POSTGRESQL_SCHEMA_HOSTNAME])
            prt = ACHelpers.resolve_vault_references(self.config_dict[POSTGRESQL_SCHEMA_PORT])
            usr = ACHelpers.resolve_vault_references(self.config_dict[POSTGRESQL_SCHEMA_USERNAME])
            pwd = ACHelpers.resolve_vault_references(self.config_dict[POSTGRESQL_SCHEMA_PASSWORD])
            db = ACHelpers.resolve_vault_references(self.config_dict[POSTGRESQL_SCHEMA_DATABASE])
            self.conn = psycopg2.connect(host=svr, port=prt,
                                         user=usr, password=pwd, database=db)
        except Exception, e:
            self.conn = None
            ACLogger().get_logger().error('Failed PostgreSQL login: %s' % str(e))
            return False

        if self.conn.closed == 0:
            return True
        else:
            return False

    def _complete_creation(self):
        if self.is_valid_postgres_schema() is False:
            ACLogger().get_logger().error('invalid PostgreSQL json schema %s', self.config_dict)
            return False
        return True

    def is_valid_postgres_schema(self):
        if self.config_dict is None:
            return False
        error_list = list()
        if POSTGRESQL_SCHEMA_USERNAME not in self.config_dict:
            error_list.append(POSTGRESQL_SCHEMA_USERNAME)
        if POSTGRESQL_SCHEMA_PASSWORD not in self.config_dict:
            error_list.append(POSTGRESQL_SCHEMA_PASSWORD)
        if POSTGRESQL_SCHEMA_HOSTNAME not in self.config_dict:
            error_list.append(POSTGRESQL_SCHEMA_HOSTNAME)
        if POSTGRESQL_SCHEMA_DATABASE not in self.config_dict:
            error_list.append(POSTGRESQL_SCHEMA_DATABASE)
        if POSTGRESQL_SCHEMA_PORT not in self.config_dict:
            error_list.append(POSTGRESQL_SCHEMA_PORT)
        if POSTGRESQL_SCHEMA_KEY not in self.config_dict:
            error_list.append(POSTGRESQL_SCHEMA_KEY)
        if POSTGRESQL_STATEMENTS not in self.config_dict:
            error_list.append(POSTGRESQL_STATEMENTS)
        else:
            query_dict = self.config_dict[POSTGRESQL_STATEMENTS]
            if isinstance(query_dict, dict) is False:
                error_list.append(POSTGRESQL_STATEMENTS)
            else:
                for key, val in query_dict.iteritems():
                    if POSTGRESQL_SQL_STRING not in val:
                        error_list.append(key + ':' + POSTGRESQL_SQL_STRING)
                    if POSTGRESQL_TYPE not in val:
                        error_list.append(key + ':' + POSTGRESQL_TYPE)
                    else:
                        query_type = val[POSTGRESQL_TYPE]
                        if query_type not in POSTGRE_EXEC_TYPES:
                            error_list.append(key + ':' + POSTGRESQL_TYPE)

        if len(error_list) > 0:
            ACLogger().get_logger().error('invalid PostgreSQL json, errors in: %s' % error_list)
            return False
        else:
            return True


    # Case 1
    # for returning an integer value form a query
    # calls cur.execute() with cur.statusmessage
    # POSTGRESQL_TYPE_EXECUTE_SCALAR = 'execute_scalar'
    #
    # Case 2
    # for sql that work or not without a return value
    # (e.g. INSERT INTO TEST01 (col01, col02, col03) VALUES $value_list;
    #   CREATE TABLE )
    # uses cur.execute
    # POSTGRESQL_TYPE_EXECUTE_NON_QUERY = 'execute_non_query'
    #
    # Case 3
    # for query based sql that returns a results set
    # (e.g. SELECT * FROM persons WHERE ... )
    # POSTGRESQL_TYPE_EXECUTE_QUERY = 'execute_query'
    #
    # Case 4
    # for query based sql that returns a single row result
    # (e.g. "SELECT * FROM employees WHERE id=%d", 13)
    # POSTGRESQL_TYPE_EXECUTE_ROW = "execute_row"
    #
    # Case 5:
    # used to insert data from a file into the database
    # POSTGRESQL_TYPE_COPY_FROM = 'execute_copy_from'
    #
    # ALL RESULTS ARE PUT INTO THE  the_file
    # the_file MUST be an OPEN File pointer
    #
    def postgres_execute(self, key_name, the_file):
        if self.config_dict is None or key_name is None or self.connect() is False or the_file is None:
            return False
        if isinstance(the_file, file) is False or the_file.closed is True:
            ACLogger().get_logger().error('ACPostgreSQL: must have open file object')
            return False
        try:
            stmnts = self.config_dict[POSTGRESQL_STATEMENTS]
            query_set = stmnts[key_name]
            sql = query_set[POSTGRESQL_SQL_STRING]
            sql = ACHelpers.resolve_vault_references(sql)
            query_type = query_set[POSTGRESQL_TYPE]
        except KeyError:
            ACLogger().get_logger().error('ACPostgreSQL: cannot get statements from config for key %s', key_name)
            return False
        insert_column_names = False
        try:
            if ACHelpers.string_is_true(query_set[POSTGRESQL_INSERT_COLUMN_NAMES]) is True:
                insert_column_names = True
        except KeyError:
            pass

        to_json_parser = False
        try:
            if POSTGRESQL_SQL_PARSER in query_set:
                if POSTGRESQL_SQL_TO_JSON_PARSER in query_set[POSTGRESQL_SQL_PARSER]:
                    to_json_parser = True
                    if insert_column_names is False:
                        ACLogger().get_logger().error('ACPostgreSQL:  key %s must be true when %s present, resetting'
                                                  % (POSTGRESQL_INSERT_COLUMN_NAMES, POSTGRESQL_SQL_TO_JSON_PARSER))
                        insert_column_names = True
        except KeyError:
            pass

        def handle_exceptions(cursor, the_key_name, ee, the_query_set, commit=False):
            if POSTGRESQL_IGNORE_EXCEPTIONS in query_set:
                ignore_exceptions = ACHelpers.string_is_true(the_query_set[POSTGRESQL_IGNORE_EXCEPTIONS])
            else:
                ignore_exceptions = False

            if ignore_exceptions is False:
                ACLogger().get_logger().error('PostgreSql exception for key %s (%s)' % (the_key_name, ee))
                if commit is True:
                    try:
                        self.conn.commit()
                    except Exception, exe:
                         ACLogger().get_logger().info('PostgreSql unable to commit post exception for key %s (%s)' %
                                                      (the_key_name, exe))
                cursor.close()
                return False
            else:
                #ACLogger().get_logger().info('PostgreSql ignored exception for key %s (%s)' % (key_name, e))
                if commit is True:
                    try:
                        self.conn.commit()
                    except Exception, exe:
                         ACLogger().get_logger().info('PostgreSql unable to commit post exception for key %s (%s)' %
                                                      (key_name, exe))
                cursor.close()
                return True

        if query_type == POSTGRESQL_TYPE_EXECUTE_SCALAR:
            curs = self.conn.cursor()
            try:
                curs.execute(sql)
                result = curs.fetchone()
                self.conn.commit()
                if isinstance(result, tuple):
                    the_file.write(str(result[0]))
                else:
                    the_file.write('ERROR')
            except Exception, e:
                return handle_exceptions(curs, key_name, e, query_set)
            the_file.flush()
            curs.close()
        elif query_type == POSTGRESQL_TYPE_EXECUTE_NON_QUERY:
            curs = self.conn.cursor()
            try:
                curs.execute(sql)
                self.conn.commit()
            except Exception, e:
                return handle_exceptions(curs, key_name, e, query_set, True)
            curs.close()
        # for an autocommit=true query (like VACUUM)
        # and sql that work or not without a return value
        # http://stackoverflow.com/questions/1017463/postgresql-how-to-run-vacuum-from-code-outside-transaction-block
        elif query_type == POSTGRESQL_TYPE_EXECUTE_LOW_ISOLATION_QUERY:
            old_isolation_level = self.conn.isolation_level
            self.conn.set_isolation_level(0)
            curs = self.conn.cursor()
            try:
                curs.execute(sql)
            except Exception, e:
                return handle_exceptions(curs, key_name, e, query_set, True)
            curs.close()
            self.conn.set_isolation_level(old_isolation_level)
        elif query_type == POSTGRESQL_TYPE_EXECUTE_QUERY:
            fetch_rows = POSTGRESQL_DEFAULT_FETCH_ROWS
            if POSTGRESQL_FETCH_ROWS in query_set:
                try:
                    fetch_rows = int(query_set[POSTGRESQL_FETCH_ROWS])
                except ValueError:
                    fetch_rows = POSTGRESQL_DEFAULT_FETCH_ROWS
            now = datetime.now()
            cursor_name='dkcursor%i' % ((now - datetime.utcfromtimestamp(0)).total_seconds() * 1000)
            curs = self.conn.cursor(name=cursor_name, withhold=False)
            curs.arraysize = fetch_rows ## redundant with below??
            try:
                curs.execute(sql)
                out_dict = OrderedDict()
                row_number = 0
                data_exists = True
                inserted_column_name = False
                while data_exists is True:
                    fetch = curs.fetchmany(fetch_rows)
                    if len(fetch) == 0:
                        data_exists = False
                    else:
                        if to_json_parser is True and insert_column_names is True:
                            if inserted_column_name is False:
                                inserted_column_name = True
                                columns = [desc[0] for desc in curs.description]
                                for row in fetch:
                                    if len(row) == len(columns):
                                        out_dict[row_number] = OrderedDict()
                                        for i in range (0, len(row)):
                                            if i <= len(columns):
                                                out_dict[row_number][columns[i]] = row[i]
                                        row_number += 1
                                    else:
                                        ACLogger().get_logger().info('PostgreSql bad row returned (sql=%s)(row=%s)' % (sql, str(row)))
                        else:
                            if insert_column_names is True and inserted_column_name is False:
                                inserted_column_name = True
                                columns = [desc[0] for desc in curs.description]
                                if len(columns) > 0:
                                    the_file.write(str(columns))
                                    the_file.write('\n')
                            for row in fetch:
                                the_file.write(str(row))
                                the_file.write('\n')
            except Exception, e:
                return handle_exceptions(curs, key_name, e, query_set)
            if to_json_parser is True and insert_column_names is True:
                try:
                    the_file.write(json.dumps(out_dict, default=ACPostgreSQLUtils.json_serial))
                except Exception:
                    ACLogger().get_logger().info('PostgreSql unable to write to file (sql=%s)' % sql)

            the_file.flush()
            curs.close()
        elif query_type == POSTGRESQL_TYPE_EXECUTE_ROW:
            curs = self.conn.cursor()
            try:
                curs.execute(sql)
                fetch = curs.fetchone()
                the_file.write(str(fetch))
                self.conn.commit()
            except Exception, e:
                return handle_exceptions(curs, key_name, e, query_set, True)
            the_file.flush()
            curs.close()
        elif query_type == POSTGRESQL_TYPE_COPY_FROM:
            buffer_size = POSTGRESQL_COPY_BUFFER_SIZE_DEFAULT
            delim = POSTGRESQL_COPY_DELIMITER_DEFAULT
            null_delim = None
            table_name = sql
            if POSTGRESQL_COPY_BUFFER_SIZE in query_set:
                try:
                    buffer_size = int(query_set[POSTGRESQL_COPY_BUFFER_SIZE])
                except ValueError:
                    buffer_size = POSTGRESQL_COPY_BUFFER_SIZE_DEFAULT
            if POSTGRESQL_COPY_DELIMITER in query_set:
                delim = query_set[POSTGRESQL_COPY_DELIMITER]
            if POSTGRESQL_COPY_NULL in query_set:
                null_delim = query_set[POSTGRESQL_COPY_NULL]
            curs = self.conn.cursor()
            
            try:
                if null_delim is None:
                    curs.copy_from(the_file, table_name, sep=delim, size=buffer_size)
                else:
                    curs.copy_from(the_file, table_name, sep=delim, size=buffer_size, null=null_delim)
                self.conn.commit()
                opened = True
            except Exception, e:
                return handle_exceptions(curs, key_name, e, query_set, True)
            curs.close()
            if opened is False:
                return False
        else:
            return False

        return True
