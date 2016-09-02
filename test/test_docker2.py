import httplib
import unittest

import mock
from mock import MagicMock

from simplekit import ContainerNotFound
from simplekit import GeneralError
from simplekit.docker import Docker
from simplekit.docker import docker


class Bunch(dict):
    def __init__(self, *args, **kwargs):
        super(Bunch, self).__init__(*args, **kwargs)
        self.__dict__ = self


class Docker2Tests(unittest.TestCase):
    def setUp(self):
        self._old_repo = docker.repo
        docker.repo = MagicMock()

    def tearDown(self):
        docker.repo = self._old_repo

    def test_search(self):
        client = Docker("mock")
        client.get_containers = MagicMock(return_value=(httplib.NOT_FOUND, None))

        code, containers = client.search('mock')
        self.assertEqual(httplib.NOT_FOUND, code)
        self.assertIsNone(containers)
        client.get_containers.assert_called_with(list_all=False)

        client.get_containers = MagicMock(return_value=(
            httplib.OK, [Bunch(Names=["filese"]), Bunch(Names=["file_Mock_11"]), Bunch(Names=["file_mock"])]))

        code, containers = client.search('mock')
        self.assertEqual(httplib.OK, code)
        self.assertEqual(2, len(containers))
        client.get_containers.assert_called_with(list_all=False)

    def test_update_image(self):
        client = Docker("mock")

        # container don't exists
        client.get_container = MagicMock(return_value=(httplib.NOT_FOUND, None))
        self.assertFalse(client.update_image(None, None))
        client.get_container.assert_called_with(None)

        # image without 'docker.neg' prefix
        client.get_container = MagicMock(return_value=(httplib.OK, Bunch(image="docker.neg/demo1")))
        self.assertFalse(client.update_image(None, "demo"))

        # image do not location docker.neg repository
        docker.repo.image_exists = MagicMock(return_value=False)
        self.assertFalse(client.update_image(None, "docker.neg/demo"))
        docker.repo.image_exists.assert_called_with("demo", tag="latest")

        # image is different
        docker.repo.image_exists = MagicMock(return_value=True)
        self.assertFalse(client.update_image("container_name", "docker.neg/demo"))

        # call update api failure
        client.get_container = MagicMock(return_value=(httplib.OK, Bunch(image="docker.neg/demo")))
        docker.repo.image_exists = MagicMock(return_value=True)
        client.update = MagicMock(return_value=(httplib.NOT_FOUND, None))
        self.assertFalse(client.update_image("container_name", "docker.neg/demo"))
        client.update.assert_called_with("container_name", tag="latest")

        # normal
        client.update = MagicMock(return_value=(httplib.OK, None))
        self.assertTrue(client.update_image("container_name", "docker.neg/demo"))
        client.update.assert_called_with("container_name", tag="latest")

    @mock.patch.object(Docker, 'get_container')
    def test_upload_image2(self, get_container):
        container_name = 'Stub_Container'
        image_name = None
        client = Docker("mock")

        # container not found
        get_container.return_value = (httplib.NOT_FOUND, None)
        self.assertRaises(ContainerNotFound, client.update_image_2, container_name, image_name)

        # api error
        get_container.return_value = (httplib.INTERNAL_SERVER_ERROR, None)
        self.assertRaises(GeneralError, client.update_image_2, container_name, image_name)

        pass
