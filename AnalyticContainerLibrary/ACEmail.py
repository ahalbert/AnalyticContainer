__author__ = 'Chris Bergh'

# clone of DKEMail.py
import sys
import types
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import Encoders
from boto.ses import SESConnection
from bs4 import BeautifulSoup
from AnalyticContainer.AnalyticContainerLibrary.ACSingletons import *
from AnalyticContainer.AnalyticContainerLibrary.ACSettings import *

class ACEmailSender(object):
    def __init__(self):
        self.config_dict = dict()

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
            ACLogger().get_logger().error('invalid ACEmailSender json schema %s', self.config_dict)
            return False
        return True

    def is_valid_config(self):
        if self.config_dict is None:
            return False
        if AC_EMAIL_SUBJECT not in self.config_dict:
            return False
        if AC_EMAIL_LIST not in self.config_dict:
            return False
        if AC_EMAIL_TEMPLATE_LOCATION not in self.config_dict:
            return False
        return True

    def send_email(self, sender,
                   to_addresses,
                   subject,
                   text,
                   html=None,
                   reply_addresses=None,
                   sender_ascii=None):
        return

    def send_email_with_attachments(self, sender,
                                    to_addresses,
                                    subject,
                                    text,
                                    html=None,
                                    reply_addresses=None,
                                    sender_ascii=None,
                                    attachment_dict=None):
        return

    def send_emails(self, template, send_list, sub_dict, subject_str, text_str):
        return False

    def apply_template_and_send_email(self, template, send_list, sub_dict, subject_str, text_str):
        return False

    def apply_template_and_send_email_with_attachments(self, template, send_list, sub_dict, subject_str, text_str,
                                                       attachment_dict):
        return False

    def verify_email(self, email):
        return False

    def get_client(self):
        return None


"""
    based on : http://amix.dk/blog/post/19619, https://groups.google.com/forum/#!topic/boto-users/25wrZzx0uAU
    ~~~~~~~~

    Python helper class that can send emails using Amazon SES and boto.
    The biggest feature of this class is that encodings are handled properly.
    It can send both text and html emails.
    This implementation is using Python's standard library

"""


class ACAWSEmailSender(ACEmailSender):
    client = None

    def __init__(self):
        ACEmailSender.__init__(self)
        self.aws_key = None
        self.aws_secret = None

    def is_valid_config(self):
        if super(ACAWSEmailSender, self).is_valid_config() is False:
            return False

        if self.config_dict is None:
            return False
        if S3_SCHEMA_ACCESS_KEY not in self.config_dict:
            return False
        if S3_SCHEMA_SECRET_KEY not in self.config_dict:
            return False
        return True

    def send_email(self, sender,
                   to_addresses,
                   subject,
                   text,
                   html=None,
                   reply_addresses=None,
                   sender_ascii=None):
        if not sender_ascii:
            sender_ascii = sender

        if self.is_valid_config() is False:
            return False
        else:
            self.aws_key = ACHelpers.resolve_vault_references(self.config_dict[S3_SCHEMA_ACCESS_KEY])
            self.aws_secret = ACHelpers.resolve_vault_references(self.config_dict[S3_SCHEMA_SECRET_KEY])
        client = self.get_client()

        message = MIMEMultipart('alternative')
        message.set_charset('UTF-8')

        message['Subject'] = _encode_str(subject)
        message['From'] = _encode_str(sender)
        message['To'] = _convert_to_strings(to_addresses)
        if reply_addresses:
            message['Reply-To'] = _convert_to_strings(reply_addresses)
        message.attach(MIMEText(_encode_str(text), 'plain'))
        if html:
            message.attach(MIMEText(_encode_str(html), 'html'))

        return client.send_raw_email(source=message['From'], raw_message=message.as_string(),
                                     destinations=message['To'])
        # return client.send_raw_email(sender_ascii, message.as_string(), to_addresses)

    # attachment dict contains a key, value where value is a file path or a dict
    def send_email_with_attachments(self, sender,
                                    to_addresses,
                                    subject,
                                    text,
                                    html=None,
                                    reply_addresses=None,
                                    sender_ascii=None,
                                    attachment_dict=None):
        if not sender_ascii:
            sender_ascii = sender

        client = self.get_client()

        message = MIMEMultipart('alternative')
        message.set_charset('UTF-8')

        message['Subject'] = _encode_str(subject)
        message['From'] = _encode_str(sender)
        message['To'] = _convert_to_strings(to_addresses)
        # what a recipient sees if they don't use an email reader
        message.preamble = 'Multipart message.\n'
        if reply_addresses:
            message['Reply-To'] = _convert_to_strings(reply_addresses)
        message.attach(MIMEText(_encode_str(text), 'plain'))
        if html:
            message.attach(MIMEText(_encode_str(html), 'html'))

        if attachment_dict is not None and len(attachment_dict) > 0:
            for name, value in attachment_dict.iteritems():
                if isinstance(value, str) or isinstance(value, unicode):
                    statinfo = os.stat(value)
                    # is the string a file?
                    if statinfo.st_size > 0:
                        part = MIMEBase('application', 'vnd.ms-excel')
                        part.set_payload(file(value).read())
                        Encoders.encode_base64(part)

                    # must be a plain old string
                    else:
                        part = MIMEText(_encode_str(value))
                elif isinstance(value, dict):
                    part = MIMEText(json.dumps(value, indent=4))
                else:
                    part = MIMEText(_encode_str(str(value)))
                part.add_header('Content-Disposition', 'attachment;filename=%s' % os.path.basename(value))
                message.attach(part)

        return client.send_raw_email(source=message['From'],
                                     raw_message=message.as_string(),
                                     destinations=message['To'])

    def apply_template_and_send_email(self, template, send_list, sub_dict, subject_str, text_str=None):
        if template is None or send_list is None or sub_dict is None or subject_str is None:
            return False
        if text_str is None:
            text_str = BeautifulSoup(template.safe_substitute(sub_dict), "html.parser").get_text()
        for email_address in send_list:
            error_str = ""
            try:
                send_response = self.send_email(sender=AC_EMAIL_FROM,
                                to_addresses=email_address,
                                subject=subject_str,
                                text=text_str,
                                html=template.safe_substitute(sub_dict),
                                reply_addresses=None,
                                sender_ascii=AC_EMAIL_ASCII_SENDER)
            except Exception, e:
                send_response = None
                error_str = str(e)
            if send_response is None:
                ACLogger.log_and_print_error('Unable to send emails to %s, error=%s' % (str(email_address), error_str))
                ACLogger.log_and_print_error('Continuing to try and send emails.')
                return False
        return True

    def apply_template_and_send_email_with_attachments(self, template, send_list, sub_dict, subject_str,
                                                       text_str=None, attachments=None):
        if template is None or send_list is None or sub_dict is None or subject_str is None:
            return False

        if text_str is None:
            text_str = BeautifulSoup(template.safe_substitute(sub_dict), "html.parser").get_text()

        for email_address in send_list:
            error_str = ""
            try:
                send_response = self.send_email_with_attachments(sender=AC_EMAIL_FROM,
                                                             to_addresses=email_address,
                                                             subject=subject_str,
                                                             text=text_str,
                                                             html=template.safe_substitute(sub_dict),
                                                             sender_ascii=AC_EMAIL_ASCII_SENDER,
                                                             reply_addresses=None,
                                                             attachment_dict=attachments)
            except Exception, e:
                send_response = None
                error_str = str(e)
            if send_response is None:
                ACLogger.log_and_print_error('Unable to send emails to %s, error=%s' % (str(email_address), error_str))
                ACLogger.log_and_print_error('Continuing to try and send emails.')
                return False
        return True

    def verify_email(self, email):
        client = self.get_client()
        return client.verify_email_address(email)

    def get_client(self):
        if not self.client:
            self.client = SESConnection(self.aws_key,
                                        self.aws_secret)
        return self.client


# --- Helpers ----------------------------------------------
def _convert_to_strings(list_of_strs):
    if isinstance(list_of_strs, (list, tuple)):
        result = COMMASPACE.join(list_of_strs)
    else:
        result = list_of_strs
    return _encode_str(result)


def _encode_str(s):
    if isinstance(s, types.UnicodeType):
        return s.encode('utf8')
    return s
