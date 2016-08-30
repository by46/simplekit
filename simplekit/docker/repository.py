import httplib
import logging

import requests

from .utils import request


class Repository(object):
    """It's used to retrieve docker information from BTS's docker repository

    """
    def __init__(self, base):
        self.server = base.strip("/")
        self.session = requests.session()
        self.headers = {}
        self.logger = logging.getLogger("negowl")

    @request(method='GET')
    def image_tags(self, image_name):
        return "/{name}/tags/list".format(name=image_name), None

    @request(method="GET")
    def images(self):
        return "/_catalog", None

    def image_exists(self, image_name, tag='latest'):
        """

        :param image_name:
        :return: True the image_name location in docker.neg pos
        """
        code, image = self.image_tags(image_name)
        if code != httplib.OK:
            return False
        tag = tag.lower()
        return any(x.lower() == tag for x in image.tags)


repo = Repository("http://10.16.78.88/v2")
