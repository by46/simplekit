import httplib
import unittest

import httpretty
import requests
from mock import patch

from simplekit.docker.rest import _default_session as session
from simplekit.docker.rest import send_rest


class RestTest(unittest.TestCase):
    @patch.object(session, 'request')
    def test_send_rest(self, request):
        request.side_effect = requests.Timeout()
        code, _ = send_rest('http://mock1:8080')
        self.assertEqual(httplib.SERVICE_UNAVAILABLE, code)
