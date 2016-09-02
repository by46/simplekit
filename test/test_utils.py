import unittest

from simplekit.docker import utils


class UitlsTest(unittest.TestCase):
    def test_parse_image_name(self):
        image_name = "demo"
        repo, name, tag = utils.parse_image_name(image_name)
        self.assertIsNone(repo)
        self.assertEqual('demo', name)
        self.assertEqual('latest', tag)

        image_name = "demo:0.0.1"
        repo, name, tag = utils.parse_image_name(image_name)
        self.assertIsNone(repo)
        self.assertEqual('demo', name)
        self.assertEqual('0.0.1', tag)

        image_name = "docker.io/demo"
        repo, name, tag = utils.parse_image_name(image_name)
        self.assertEqual('docker.io', repo)
        self.assertEqual('demo', name)
        self.assertEqual('latest', tag)

        image_name = "docker.io/demo:0.0.1"
        repo, name, tag = utils.parse_image_name(image_name)
        self.assertEqual('docker.io', repo)
        self.assertEqual('demo', name)
        self.assertEqual('0.0.1', tag)
