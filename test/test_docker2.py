import httplib
import unittest

import mock
from mock import MagicMock

from simplekit import ContainerNotFound
from simplekit import GeneralError
from simplekit import ImageConflict
from simplekit import ImageNotFound
from simplekit.docker import Docker


class Bunch(dict):
    def __init__(self, *args, **kwargs):
        super(Bunch, self).__init__(*args, **kwargs)
        self.__dict__ = self


class Docker2Tests(unittest.TestCase):
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

    @mock.patch('simplekit.docker.docker.repo')
    def test_update_image(self, repo):
        client = Docker("mock")

        # container don't exists
        client.get_container = MagicMock(return_value=(httplib.NOT_FOUND, None))
        self.assertFalse(client.update_image(None, None))
        client.get_container.assert_called_with(None)

        # image without 'docker.neg' prefix
        client.get_container = MagicMock(return_value=(httplib.OK, Bunch(image="docker.neg/demo1")))
        self.assertFalse(client.update_image(None, "demo"))

        # image do not location docker.neg repository
        repo.image_exists = MagicMock(return_value=False)
        self.assertFalse(client.update_image(None, "docker.neg/demo"))
        repo.image_exists.assert_called_with("demo", tag="latest")

        # image is different
        repo.image_exists = MagicMock(return_value=True)
        self.assertFalse(client.update_image("container_name", "docker.neg/demo"))

        # call update api failure
        client.get_container = MagicMock(return_value=(httplib.OK, Bunch(image="docker.neg/demo")))
        repo.image_exists = MagicMock(return_value=True)
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

    @mock.patch('simplekit.docker.docker.repo')
    @mock.patch.object(Docker, 'get_container')
    def test_upload_image2_image_not_exists(self, get_container, repo):
        client = Docker("mock")
        container_name = 'Stub_Container'
        image_name = 'docker.neg/demo'
        get_container.return_value = (httplib.OK, MagicMock(image=image_name))
        repo.image_exists.return_value = False
        self.assertRaises(ImageNotFound, client.update_image_2, container_name, image_name)
        repo.image_exists.assert_called_with('demo', tag='latest')

    @mock.patch('simplekit.docker.docker.repo')
    @mock.patch.object(Docker, 'get_container')
    def test_upload_image2_image_mismatch(self, get_container, repo):
        client = Docker("mock")
        container_name = 'Stub_Container'
        image_name = 'docker.neg/demo'
        old_image_name = 'docker.neg/demo2'
        get_container.return_value = (httplib.OK, MagicMock(image=old_image_name))
        repo.image_exists.return_value = True
        self.assertRaises(ImageConflict, client.update_image_2, container_name, image_name)
        repo.image_exists.assert_called_with('demo', tag='latest')

    @mock.patch('simplekit.docker.docker.repo')
    @mock.patch.object(Docker, 'pull_image')
    @mock.patch.object(Docker, 'get_container')
    def test_upload_image2_pull_image_exception(self, get_container, pull_image, repo):
        client = Docker('mock')
        container_name = 'Stub_Container'
        image_name = 'docker.neg/demo'
        get_container.return_value = (httplib.OK, MagicMock(image=image_name))
        repo.image_exists.return_value = True
        pull_image.return_value = (httplib.INTERNAL_SERVER_ERROR, None)

        # Assertion
        self.assertRaises(GeneralError, client.update_image_2, container_name, image_name)
        get_container.assert_called_with(container_name)
        repo.image_exists.assert_called_with('demo', tag='latest')
        pull_image.assert_called_with('demo', 'latest')

    @mock.patch.object(Docker, 'update')
    @mock.patch('simplekit.docker.docker.repo')
    @mock.patch.object(Docker, 'pull_image')
    @mock.patch.object(Docker, 'get_container')
    def test_upload_image2_update_exception(self, get_container, pull_image, repo, update):
        client = Docker('mock')
        container_name = 'Stub_Container'
        image_name = 'docker.neg/demo'
        get_container.return_value = (httplib.OK, MagicMock(image=image_name))
        repo.image_exists.return_value = True
        pull_image.return_value = (httplib.OK, None)
        update.return_value = (httplib.INTERNAL_SERVER_ERROR, None)

        # Assertion
        self.assertRaises(GeneralError, client.update_image_2, container_name, image_name)
        get_container.assert_called_with(container_name)
        repo.image_exists.assert_called_with('demo', tag='latest')
        pull_image.assert_called_with('demo', 'latest')
        update.assert_called_with(container_name, tag='latest')

    @mock.patch.object(Docker, 'update')
    @mock.patch('simplekit.docker.docker.repo')
    @mock.patch.object(Docker, 'pull_image')
    @mock.patch.object(Docker, 'get_container')
    def test_upload_image2_normal(self, get_container, pull_image, repo, update):
        client = Docker('mock')
        container_name = 'Stub_Container'
        image_name = 'docker.neg1/demo'
        get_container.return_value = (httplib.OK, MagicMock(image=image_name))
        repo.image_exists.return_value = True
        pull_image.return_value = (httplib.OK, None)
        update.return_value = (httplib.OK, None)

        # Assertion
        self.assertTrue(client.update_image_2(container_name, image_name))
        get_container.assert_called_with(container_name)
        repo.image_exists.assert_called_with('demo', tag='latest')
        pull_image.assert_called_with('demo', 'latest')
        update.assert_called_with(container_name, tag='latest')
