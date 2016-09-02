import httplib
import unittest

import mock
import requests

from simplekit.email import MailException
from simplekit.email import send_email


class EmailTestCase(unittest.TestCase):
    @mock.patch.object(requests, 'post')
    def test_send_email(self, post):
        post.return_value.status_code = httplib.OK
        sender = 'testing@newgg.com'
        to = 'slug@newegg.com'
        subject = 'info'
        body = 'test'
        send_email(sender, to, subject, body)

        self.assertTrue(post.called)
        post.assert_called_with('http://apis.newegg.org/framework/v1/mail',
                                headers={'Content-Type': 'Application/json', 'accept': 'application/json'},
                                json={'Body': 'test', 'ContentType': 1,
                                      'SmtpSetting': {'SubjectEncoding': 0, 'Attachments': [], 'BodyEncoding': 0},
                                      'CC': None, 'LondonIISetting': None, 'MailType': 1, 'BCC': None, 'Priority': 0,
                                      'To': 'slug@newegg.com', 'From': 'testing@newgg.com', 'Subject': 'info'})

        to = ['slug@newegg.com', '1']
        send_email(sender, to, subject, body)

        self.assertTrue(post.called)
        post.assert_called_with('http://apis.newegg.org/framework/v1/mail',
                                headers={'Content-Type': 'Application/json', 'accept': 'application/json'},
                                json={'Body': 'test', 'ContentType': 1,
                                      'SmtpSetting': {'SubjectEncoding': 0, 'Attachments': [], 'BodyEncoding': 0},
                                      'CC': None, 'LondonIISetting': None, 'MailType': 1, 'BCC': None, 'Priority': 0,
                                      'To': 'slug@newegg.com;1', 'From': 'testing@newgg.com', 'Subject': 'info'})

    @mock.patch.object(requests, 'post')
    def test_send_email_exception(self, post):
        post.return_value.status_code = httplib.INTERNAL_SERVER_ERROR
        post.return_value.content = ''
        sender = 'testing@newgg.com'
        to = 'slug@newegg.com'
        subject = 'info'
        body = 'test'
        self.assertRaises(MailException, send_email, sender, to, subject, body)
        self.assertTrue(post.called)
        post.assert_called_with('http://apis.newegg.org/framework/v1/mail',
                                headers={'Content-Type': 'Application/json', 'accept': 'application/json'},
                                json={'Body': 'test', 'ContentType': 1, 'CC': None, 'LondonIISetting': None,
                                      'MailType': 1, 'BCC': None, 'Priority': 0, 'To': 'slug@newegg.com',
                                      'From': 'testing@newgg.com', 'Subject': 'info'})
