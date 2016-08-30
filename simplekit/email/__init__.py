import httplib
import os.path

import requests
import six

from simplekit import settings
from simplekit.exceptions import MailException

PRIORITY_NORMAL = 0
PRIORITY_LOW = 1
PRIORITY_HIGH = 2

CONTENT_TYPE_HTML = 0
CONTENT_TYPE_TEXT = 1

ENCODING_UTF8 = 0
ENCODING_ASCII = 1
ENCODING_UTF32 = 2
ENCODING_UNICODE = 3

MEDIA_TYPE_GIF = 0
MEDIA_TYPE_JPEG = 1
MEDIA_TYPE_TIFF = 2
MEDIA_TYPE_PDF = 3
MEDIA_TYPE_RTF = 4
MEDIA_TYPE_SOAP = 5
MEDIA_TYPE_ZIP = 6
MEDIA_TYPE_OTHER = 7

MAIL_TYPE_SMTP = 1
MAIL_TYPE_LONDON2 = 0


class SmtpSetting(dict):
    def __init__(self, subject_encoding, body_encoding, attachments=None):
        kwargs = dict(SubjectEncoding=subject_encoding,
                      BodyEncoding=body_encoding,
                      Attachments=attachments)
        super(SmtpSetting, self).__init__(**kwargs)
        self.__dict__ = self


class MailAttachment(dict):
    def __init__(self, filename, file_content, media_type=MEDIA_TYPE_OTHER):
        kwargs = dict(FileName=filename,
                      FileContent=file_content,
                      MediaType=media_type)
        super(MailAttachment, self).__init__(**kwargs)
        self.__dict__ = self


class LondonIISetting(dict):
    def __init__(self, company_code, country_code, language_code, system_id, template_id, mail_template_variables):
        kwargs = dict(CompanyCode=company_code,
                      CountryCode=country_code,
                      LanguageCode=language_code,
                      SystemID=system_id,
                      TemplateID=template_id,
                      MailTemplateVariables=mail_template_variables)
        super(LondonIISetting, self).__init__(**kwargs)
        self.__dict__ = self


class MailTemplateVariable(dict):
    def __init__(self, key, value):
        kwargs = dict(Key=key, Value=value)
        super(MailTemplateVariable, self).__init__(**kwargs)


def send_email_inner(sender, to, subject, body, cc=None, bcc=None, priority=PRIORITY_NORMAL,
                     content_type=CONTENT_TYPE_TEXT,
                     mail_type=None, smtp_setting=None, london_2_setting=None):
    if isinstance(to, (list, tuple)):
        to = ';'.join(to)
    body = dict(From=sender,
                To=to,
                CC=cc,
                BCC=bcc,
                Subject=subject,
                Body=body,
                Priority=priority,
                ContentType=content_type,
                MailType=mail_type,
                SmtpSetting=smtp_setting,
                LondonIISetting=london_2_setting)
    response = requests.post(settings.URL_EMAIL, json=body,
                             headers={'Content-Type': 'Application/json', 'accept': 'application/json'})
    if response.status_code != httplib.OK:
        del body['SmtpSetting']
        raise MailException("Send mail use api {0} status code: {1}\n body : {2}\n response content : {3}".format(
            settings.URL_EMAIL, response.status_code, body, response.content))


def send_email(sender, to, subject, body, cc=None, bcc=None, priority=PRIORITY_NORMAL,
               content_type=CONTENT_TYPE_TEXT,
               files=None):
    attachments = []
    import base64
    if files:
        for item in files:
            if isinstance(item, six.string_types):
                filename = os.path.basename(item)
                file_content = open(item, 'rb').read()
                file_content = base64.b64encode(file_content)
                media_type = MEDIA_TYPE_OTHER
                attachment = MailAttachment(filename, file_content, media_type)
                attachments.append(attachment)
            else:
                attachments.append(item)

    smtp_setting = SmtpSetting(ENCODING_UTF8, ENCODING_UTF8, attachments)
    send_email_inner(sender, to, subject, body, cc, bcc, priority, content_type, MAIL_TYPE_SMTP, smtp_setting)


if __name__ == '__main__':
    send_email('benjamin.c.yan@newegg.com', 'benjamin.c.yan@newegg.com', '(info) testing', 'testing body',
               files=['__init__.py'])
