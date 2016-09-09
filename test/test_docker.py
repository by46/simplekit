import httplib
import json
import unittest

import httpretty
from mock import MagicMock
from mock import patch

from simplekit import objson
from simplekit.docker import Docker

__author__ = 'benjamin.c.yan'


class Bunch(dict):
    def __init__(self, *args, **kwargs):
        super(Bunch, self).__init__(*args, **kwargs)
        self.__dict__ = self


class DockerTests(unittest.TestCase):
    def __init__(self, method_name):
        super(DockerTests, self).__init__(method_name)
        self.base = 'http://mock:8500'
        self.server = 'mock'

    @httpretty.activate
    def test_get_container(self):
        name = 'creb_session_1'
        url = '{base}/dockerapi/v2/containers/{name}'.format(base=self.base, name=name)
        body = dict()
        httpretty.register_uri(httpretty.GET, url, body=json.dumps(body))

        client = Docker(self.server)
        code, container = client.get_container(name)
        self.assertEqual(httplib.OK, code)
        self.assertDictEqual(body, json.loads(objson.dumps(container)))

    @patch('simplekit.docker.utils.send_rest')
    def test_get_container_2(self, send_rest):
        send_rest.return_value = (httplib.OK, None)
        client = Docker('mock')
        status_code, container = client.get_container('stub_container_name', return_original_data=True)
        self.assertEqual(httplib.OK, status_code)
        send_rest.assert_called_with('http://mock:8500/dockerapi/v2/containers/stub_container_name?originaldata=True',
                                     body=None,
                                     headers={},
                                     method='GET',
                                     session=client.session)

    @httpretty.activate
    def test_get_containers(self):
        url = '{base}/dockerapi/v2/containers?all=True'.format(base=self.base)
        body = dict()
        httpretty.register_uri(httpretty.GET, url, body=json.dumps(body))

        client = Docker(self.server)

        code, containers = client.get_containers(list_all=True)
        self.assertEqual(httplib.OK, code)
        self.assertDictEqual(body, json.loads(objson.dumps(containers)))

        url = '{base}/dockerapi/v2/containers?all=False'.format(base=self.base)
        httpretty.register_uri(httpretty.GET, url, body=json.dumps(body))
        code, containers = client.get_containers(list_all=False)
        self.assertEqual(httplib.OK, code)
        self.assertDictEqual(body, json.loads(objson.dumps(containers)))

        httpretty.register_uri(httpretty.GET, url, status=httplib.NOT_FOUND)
        code, _ = client.get_containers(list_all=False)
        self.assertEqual(httplib.NOT_FOUND, code)

    @httpretty.activate
    def test_create_container(self):
        url = '{base}/dockerapi/v2/containers'.format(base=self.base)
        body = dict()
        httpretty.register_uri(httpretty.POST, url, body=body)
        client = Docker(self.server)

        code, _ = client.create_container(name='testing', image='dfis:creb')
        self.assertEqual(httplib.OK, code)
        container = objson.loads(httpretty.last_request().body)
        self.assertEqual(container.name, 'testing')
        self.assertEqual(container.image, 'docker.neg/dfis:creb')
        self.assertEqual(container.hostname, 'dfis')
        self.assertEqual(container.networkmode, 'bridge')

    @httpretty.activate
    def test_change_container(self):
        url = '{base}/dockerapi/v2/containers'.format(base=self.base)
        body = dict()
        httpretty.register_uri(httpretty.PUT, url, body=body)
        client = Docker(self.server)

        code, _ = client.change_container(name='testing')
        self.assertEqual(httplib.OK, code)
        container = objson.loads(httpretty.last_request().body)
        self.assertEqual(container.container, 'testing')
        self.assertEqual(container.action, 'stop')

    @httpretty.activate
    def test_delete_container(self):
        url = '{base}/dockerapi/v2/containers/{name}'.format(base=self.base, name='testing')
        body = dict()
        httpretty.register_uri(httpretty.DELETE, url, body=body)
        client = Docker(self.server)

        code, _ = client.delete_container(name='testing')
        self.assertEqual(httplib.OK, code)

    @httpretty.activate
    def test_get_containers_by_name(self):
        url = '{base}/dockerapi/v2/containers'.format(base=self.base)
        body = [{"Names": ["/creb_session_1"], "Id": 1},
                {"Names": ["/creb_session_2"], "Id": 2},
                {"Names": ["/image_creb_session_3"], "Id": 3},
                {"Names": ["/cabinet"], "Id": 4}]
        httpretty.register_uri(httpretty.GET, url, status=httplib.INTERNAL_SERVER_ERROR)

        client = Docker(self.server)

        containers = client.get_containers_by_name('session')
        self.assertFalse(bool(containers))

        httpretty.register_uri(httpretty.GET, url, body=json.dumps(body))
        name = "/creb_session_"
        containers = client.get_containers_by_name(name)

        self.assertEqual(2, len(containers))
        self.assertListEqual([1, 2], [container.Id for container in containers])

    @httpretty.activate
    def test_delete_container_2(self):
        name = 'creb_session_1'
        url = '{base}/dockerapi/v2/containers/{name}'.format(base=self.base, name=name)
        change_url = '{base}/dockerapi/v2/containers'.format(base=self.base)
        client = Docker(self.server)
        logger = client.logger = MagicMock()

        # container not exist
        httpretty.register_uri(httpretty.GET, url, status=httplib.NOT_FOUND)
        self.assertTrue(client.delete_container_2(name))

        # get container information error
        httpretty.register_uri(httpretty.GET, url, status=httplib.FORBIDDEN)
        logger.error = MagicMock()
        self.assertFalse(client.delete_container_2(name))
        logger.error.assert_called_with("Container %s on %s not exists. %d", name, self.server, httplib.FORBIDDEN)

        # stop container error
        body = dict(status=dict(Running=True))
        httpretty.register_uri(httpretty.GET, url, body=json.dumps(body))
        httpretty.register_uri(httpretty.PUT, change_url, status=httplib.FORBIDDEN, body='{}')
        logger.error = MagicMock()
        self.assertFalse(client.delete_container_2(name))
        model = objson.loads(httpretty.last_request().body)
        self.assertEqual(name, model.container)
        self.assertEqual('stop', model.action)
        logger.error.assert_called_with("Stop container %s on %s error, status code %d, message %s", name, self.server,
                                        httplib.FORBIDDEN, '{}')

        # delete container error
        httpretty.register_uri(httpretty.PUT, change_url, status=httplib.OK)
        httpretty.register_uri(httpretty.DELETE, url, status=httplib.FORBIDDEN, body='{}')
        logger.error = MagicMock()
        self.assertFalse(client.delete_container_2(name))
        logger.error.assert_called_with("Delete container %s on %s error, status code %d, message %s", name,
                                        self.server, httplib.FORBIDDEN, '{}')

        httpretty.register_uri(httpretty.PUT, change_url, status=httplib.OK)
        httpretty.register_uri(httpretty.DELETE, url, status=httplib.OK)
        self.assertTrue(client.delete_container_2(name))
