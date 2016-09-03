import unittest

from mock import call
from mock import patch

from simplekit.docker import factory


class DockerFactoryTest(unittest.TestCase):
    @patch('simplekit.docker.docker.Docker')
    def test_get(self, docker_class):
        factory.get('mock')
        docker_class.assert_called_with('mock')

        factory.get('mock')
        docker_class.assert_has_calls([call('mock')])

        factory.get('mock2')
        docker_class.assert_has_calls([call('mock'), call('mock2')])
