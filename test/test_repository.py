import json
import unittest

import httpretty

from simplekit.docker import Repository


class RepositoryTest(unittest.TestCase):
    @httpretty.activate
    def test_image_exists(self):
        url = "http://mock:80/v2"
        repo = Repository(url)
        httpretty.register_uri(httpretty.GET, url + "/demo/tags/list",
                               body=json.dumps(dict(name="demo", tags=["0.0.1", "0.0.2"])))

        self.assertTrue(repo.image_exists("demo", "0.0.1"))
        self.assertTrue(repo.image_exists("demo", "0.0.2"))
        self.assertFalse(repo.image_exists("demo"))

        self.assertFalse(repo.image_exists("demo1"))
