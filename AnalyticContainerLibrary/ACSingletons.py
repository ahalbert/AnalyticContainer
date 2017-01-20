__author__ = 'Chris Bergh'
import os
import sys
import json
import base64
import zlib
from collections import OrderedDict
from datetime import datetime, timedelta
from ACSettings import *
import traceback

## using borg pattern for singletons
class ACLogger:
    __shared_state = {}
    def __init__(self, log_filename=AC_LOG_FILE_LOCATION):
        self.__dict__ = self.__shared_state
        logging.basicConfig(level=AC_LOGGING,
                        format='AC: %(asctime)s %(levelname)s : %(message)s',
                        filename=log_filename, filemode=AC_APPEND_MODE)

        if logging.getLogger("requests") is not None:
            logging.getLogger("requests").setLevel(logging.WARNING)
        self.logger = logging.getLogger('ACLogger')
        self.log_filename = log_filename

    def get_logger(self):
        return self.logger

    def get_log_filename(self):
        return self.log_filename

    @staticmethod
    def log_and_print(msg):
        print msg
        ACLogger().get_logger().info(msg)

    @staticmethod
    def log_and_print_error(msg):
        print msg
        ACLogger().get_logger().error(msg)

    @staticmethod
    def log(msg, error=False, print_msg=False):
        if print_msg:
            print msg
        if error:
            ACLogger().get_logger().error(msg)
        else:
            ACLogger().get_logger().info(msg)
    
class ACAppConfig:
    __shared_state = {}
    _config_dict = None
    _config_attrs = None

    def __init__(self):
        self.__dict__ = self.__shared_state
        if self._config_dict is None:
            self._config_dict = dict()
        self._config_attributes = []

    def __str__(self):
        return str(self._config_dict)

    def get(self, attribute):
        if attribute is None:
            return None

        if attribute in self._config_dict:
            return self._config_dict[attribute]
        else:
            return None

    def set(self, attribute, value):
        if attribute is None:
            return
        self._config_dict[attribute] = value

    def init_from_dict(self, set_dict):
        self._config_dict = set_dict
        return self.validate_config()

    def init_from_string(self, jstr):
        try:
            self._config_dict = json.loads(jstr)
        except ValueError, e:
            ACLogger.log_and_print_error('ACAppConfig: failed json.load check syntax %s. %s' % (jstr, e))
            return False
        return self.validate_config()

    def init_from_file(self, file_json):
        if file_json is None:
            ACLogger.log_and_print_error('ACAppConfig file path cannot be null')
            rv = False
        else:
            try:
                statinfo = os.stat(file_json)
            except Exception:
                pass
                rv = False
            else:
                if statinfo.st_size > 0:
                    with open(file_json) as data_file:
                        try:
                            self._config_dict = json.load(data_file)
                        except ValueError, e:
                            ACLogger.log_and_print_error('ACAppConfig: failed json.load check syntax %s. %s' % (file_json, e))
                            rv = False
                        else:
                            rv = True
                else:
                    rv = False
        if rv is False:
            return False
        else:
            return self.validate_config()

    def validate_config(self):
        for v in self._config_attributes:
            if v not in self._config_dict:
                ACLogger.log_and_print_error("ACAppConfig: failed to find %s in ACAppConfig.json" % v)
                return False
        return True


class ACHelpers:
    
    def __init__(self):
        pass

    @staticmethod
    def convert(the_input):
        if isinstance(the_input, dict) is True:
            rd = OrderedDict()
            for key, value in the_input.iteritems():
                rd[key.encode('utf-8')] = ACHelpers.convert(value)
            return rd
        elif isinstance(the_input, list):
            return [ACHelpers.convert(element) for element in the_input]
        elif isinstance(the_input, unicode):
            return the_input.encode('utf-8')
        else:
            return the_input

    @staticmethod
    def string_is_true(test_str):
        if test_str is None:
            return False
        if test_str is True:
            return True
        if test_str == 'True' or test_str == 'TRUE' or test_str == 'T':
            return True
        if test_str == 'true' or test_str == 't':
            return True

    @staticmethod
    def string_is_false(test_str):
        if test_str is None:
            return False
        if test_str is False:
            return True
        if test_str == 'False' or test_str == 'FALSE' or test_str == 'F':
            return True
        if test_str == 'true' or test_str == 'f':
            return True

    @staticmethod
    def string_timedelta(s):
        if isinstance(s, timedelta) is False:
            return "Error, not a timedelta"
        else:
            int_sec = s.total_seconds()
            hours, remainder = divmod(int_sec, 3600)
            minutes, seconds = divmod(remainder, 60)
            if s.days > 0:
                st_val = '%i %i:%i:%s' % (s.days, hours, minutes, seconds)
            elif s.days == 0:
                st_val = '%i:%i:%s' % (hours, minutes, seconds)
            else:
                st_val = '%i %i:%i:%s' % (abs(s.days), hours, minutes, seconds)
            return st_val

    @staticmethod
    def create_timedelta_none(td_str):
        have_error = False

        if td_str is None or isinstance(td_str, basestring) is False:
            ACLogger().get_logger().error('create_timedelta: unable to get timedelta string %s' % td_str)
            return None

        hour_str = td_str.split(":")[0]
        days = hours = 0
        if hour_str is not None:
            try:
                hours = int(hour_str)
            except ValueError:
                day_str = hour_str.split(" ")[0]
                if day_str is not None:
                    try:
                        days = int(day_str)
                    except ValueError:
                        ACLogger().get_logger().error('create_timedelta: unable to get timedelta days %s' % td_str)
                        return None
                    if len(hour_str.split(" ")) != 2:
                        ACLogger().get_logger().error('create_timedelta: unable to get timedelta space %s' % td_str)
                        return None
                    else:
                        hs = hour_str.split(" ")[1]
                        try:
                            hours = int(hs)
                        except ValueError:
                            ACLogger().get_logger().error('create_timedelta: unable to get timedelta hours %s' % td_str)
                            return None
            if hours > 23:
                days_divmod, remainder_hours = divmod(hours, 24)
                days += days_divmod
                if len(td_str.split(":")) == 3:
                    td_s = '%i:%s:%s' % (remainder_hours, td_str.split(":")[1], td_str.split(":")[2])
                else:
                    td_s = td_str
            else:
                td_s = td_str
        else:
            td_s = td_str
        t = None
        if len(td_s) < 5:
            have_error = True
        elif td_s.find('.') == -1:
            try:
                t = datetime.strptime(td_s, "%H:%M:%S")
                if days > 0:
                    t = t.replace(day=days)
            except ValueError:
                have_error = True
        else:
            try:
                t = datetime.strptime(td_s, "%H:%M:%S.%f")
                if days > 0:
                    t = t.replace(day=days)
            except ValueError:
                micro_str = td_s.split(".")[1]
                if len(micro_str) > 5:
                    micro_str = micro_str[0:5]
                    new_str = td_s.split(".")[0] + '.' + micro_str
                    try:
                        t = datetime.strptime(new_str, "%H:%M:%S.%f")
                        if days > 0:
                            t = t.replace(day=days)
                    except ValueError:
                        have_error = True
                else:
                    new_str = td_s.split(".")[0]
                    try:
                        t = datetime.strptime(new_str, "%H:%M:%S")
                        if days > 0:
                            t = t.replace(day=days)
                    except ValueError:
                        have_error = True

        if have_error is True:
            ACLogger().get_logger().error('create_timedelta: unable to parse timedelta string %s' % td_str)
            return None
        else:
            return t

    @staticmethod
    def create_timedelta(td_str):
        t = ACHelpers().create_timedelta_none(td_str)
        if t is None:
            return timedelta()
        if t.day > 0:
            return timedelta(days=t.day, hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
        else:
            return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)

    @staticmethod
    def create_datetime_none(t_str):
        have_error = False
        ## datetime.strptime(last_duration, "%Y-%m-%d %H:%M:%S.%f")
        t = None
        if t_str is None or len(t_str) < 5:
            have_error = True
        elif t_str.find('.') == -1:
            try:
                t = datetime.strptime(t_str, "%H:%M:%S")
            except ValueError:
                try:
                    t = datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        t = datetime.strptime(t_str, "%Y-%m-%d")
                    except ValueError:
                        have_error = True
        else:
            try:
                t = datetime.strptime(t_str, "%H:%M:%S.%f")
            except ValueError:
                try:
                    t = datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    have_error = True

        if have_error is True:
            td = ACHelpers().create_timedelta_none(t_str) ## returns datetime
            if td is not None:
                return td
            else:
                return None
        else:
            return t

    @staticmethod
    def split_one(path):
        """
        Utility function for splitting off the very first part of a path.
        """
        s = path.split('/', 1)
        if len(s) == 1:
            return s[0], ''
        else:
            return tuple(s)

    @staticmethod
    def split_one_end(path):
        """
        Utility function for splitting off the very end part of a path.
        """
        s = path.rsplit('/', 1)
        if len(s) == 1:
            return s[0], ''
        else:
            return tuple(s)

    @staticmethod
    def create_datetime(t_str):
        if t_str is None:
            t = datetime.now()
        else:
            t = ACHelpers().create_datetime_none(t_str)
            if t is None:
                t = datetime.now()
        return t


    @staticmethod
    def get_datetime_string():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


    @staticmethod
    def compress(the_input):
        if isinstance(the_input, basestring):
            return base64.b64encode(zlib.compress(the_input, 9))
        else:
            raise ValueError('compress requires string input')


    @staticmethod
    def decompress(the_input):
        if isinstance(the_input, basestring):
            return zlib.decompress(base64.b64decode(the_input))
        else:
            raise ValueError('decompress requires string input')

    @staticmethod
    def resolve_secrets(input_dict):

        for key in input_dict.keys():
            val = input_dict[key]
            if isinstance(val,basestring):
                input_dict[key] = ACHelpers.resolve_vault_references(val)
            elif isinstance(val,dict):
                ACHelpers.resolve_secrets(val)
            elif isinstance(val,list):
                for i,e in enumerate(val):
                    val[i] = ACHelpers.resolve_vault_references(val[i])


    @staticmethod
    def resolve_vault_references(some_string):
        if isinstance(some_string,basestring):
            some_string2 = some_string.replace('${', '').replace('}', '')
            try:
                value = ACHelpers.secret_resolve(some_string2)
                return value
            except Exception as e:
                ACLogger.log_and_print_error('Failed to resolve: %s, %s' % (str(e), traceback.format_exc()))

        return some_string

    @staticmethod
    def secret_resolve(uri):
        if uri and isinstance(uri,basestring):
            if uri.startswith('vault://'):
                env_var = 'SECRET_'+uri[8:].replace('/','_').upper()
                try:
                    rv = os.environ[env_var]
                    #ACLogger.log_and_print('found vault key: %s, val = %s' % (env_var, rv))
                    return rv
                except KeyError:
                    #ACLogger.log_and_print('unable to find vault key: %s' % env_var)
                    return None
        return uri

    @staticmethod
    def dump_env(de):
        if de is True:
            print("DUMPING ENV ...........")
            for key in os.environ.keys():
                print "%s: %s \n" % (key, os.environ[key])
            print("sys.path: %s \n" % sys.path)
            print("os.cwd: %s \n" % os.getcwd())