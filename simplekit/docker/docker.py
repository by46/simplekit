# coding=utf-8
""" docker api sdk

"""
import functools
import httplib
import itertools
import logging

import requests

from simplekit import objson
from simplekit.exceptions import ContainerNotFound
from simplekit.exceptions import GeneralError
from simplekit.exceptions import ImageConflict
from simplekit.exceptions import ImageNotFound
from . import utils
from .repository import repo
from .utils import request

__author__ = 'benjamin.c.yan'

DOCKER_NEG = "docker.neg"


def name_start_with(name, container):
    return any([True for x in container.Names if x.startswith(name)])


class Docker(object):
    """Docker client
    """
    LoggerName = 'Docker'

    def __init__(self, server, port=8500):
        self.logger = logging.getLogger(__name__)
        self._session = requests.session()
        self._host = server
        self._port = port
        self._server = 'http://{host}:{port}'.format(host=server, port=port)
        self._headers = {}

    # --------------------------------------------------
    # properties methods
    # --------------------------------------------------
    @property
    def server(self):
        return self._server

    @property
    def session(self):
        return self._session

    @property
    def headers(self):
        return self._headers

    # --------------------------------------------------
    # public methods
    # --------------------------------------------------
    @request(method='get')
    def version(self):
        return '/dockerapi/v2/ping', None

    @request(method='get')
    def get_containers(self, list_all=False):
        return ("/dockerapi/v2/containers", dict(all=list_all)), None

    @request(method='get')
    def get_container(self, name, return_original_data=False):
        return ("/dockerapi/v2/containers/" + name, dict(originaldata=return_original_data)), None

    @request(method='post')
    def pull_image(self, name, tag='latest'):
        """pull the image from repository

        :param name: `class`:`str`, without docker.neg prefix, invalid like: 'centos'
        :param tag: `class`:`str`, special the image's version
        :return: (`class`:`int`, `class`:`object`)
        """
        name = "{0}/{1}:{2}".format(DOCKER_NEG, name, tag)
        return "/dockerapi/v2/images", dict(image=name)

    @request(method='post')
    def create_container(self, name, image, hostname='dfis', networkmode='bridge', ports=None, volumes=None, env=None,
                         restartpolicy='always', restartretrycount='2', command=""):
        """testing

        :param name:
        :param image:
        :param hostname:
        :param networkmode: `class`:`str`, host | bridge
        :param ports: `class`:`list`,
            [{'type':'tcp', 'publicport':8080, 'privateport':80, 'ip':'0.0.0.0}]
        :param volumes: `class`:`list`,
            [{"containervolume":"/app-conf", "hostvolume":"/opt/app/app-conf"}]
        :param env: `class`:`list`, ["var=value", "var1=value1"]
        :param restartpolicy: `class`:`str`, always | on-failure | no(default)
        :param restartretrycount: 仅当 restartpolicy 是 on-failure 时才有用
        :param command:
        :return:
        """
        restartpolicy = restartpolicy.lower()
        _, image_name, version = utils.parse_image_name(image)
        image = '{0}/{1}:{2}'.format(DOCKER_NEG, image_name, version)
        body = dict(name=name, image=image, hostname=hostname, networkmode=networkmode,
                    ports=ports or [],
                    volumes=volumes or [],
                    env=env or [],
                    restartpolicy=restartpolicy,
                    command=command)
        if restartpolicy == 'on-failure':
            body['restartretrycount'] = restartretrycount

        return "/dockerapi/v2/containers", body

    @request(method='put')
    def change_container(self, name, action='stop'):
        """
        action: "[start|stop|restart|kill|pause|unpause]",

        :param name: container name
        :param action: status which need to switch
        :return:
        """
        return "/dockerapi/v2/containers", dict(container=name, action=action)

    @request(method='delete')
    def delete_container(self, name):
        return "/dockerapi/v2/containers/{name}".format(name=name), None

    @request(method='PUT')
    def update(self, container, tag='latest'):
        return '/dockerapi/v2/containers', dict(action='upgrade', container=container, imagetag=tag)

    def get_containers_by_name(self, name):
        """
        get all task which relative with task name
        :param name: :class:`str`, task name
        :return: :class:`list`, container list
        """
        code, containers = self.get_containers()

        if code != httplib.OK:
            return []

        return list(itertools.ifilter(functools.partial(name_start_with, name), containers))

    def get_containers_count(self, name):
        return len(self.get_containers_by_name(name))

    def delete_container_2(self, name):
        """

        :param name: `class`:`str`, container name
        :return: `class`:`bool`, return True if delete success, otherwise return False
        """
        code, container = self.get_container(name)
        if code == httplib.NOT_FOUND:
            return True
        elif code != httplib.OK:
            self.logger.error("Container %s on %s not exists. %d", name, self._host, code)
            return False

        if container.status.Running:
            code, message = self.change_container(name)
            if code != httplib.OK:
                self.logger.error("Stop container %s on %s error, status code %d, message %s", name, self._host, code,
                                  objson.dumps(message))
                return False

        code, message = self.delete_container(name)
        if code != httplib.OK:
            self.logger.error("Delete container %s on %s error, status code %d, message %s", name, self._host, code,
                              objson.dumps(message))
            return False
        return True

    def search(self, name, search_all=False):
        name = name.lower()

        code, containers = self.get_containers(list_all=search_all)
        if code == httplib.OK:
            containers = [x for x in containers if name in x.Names[0].lower()]
        return code, containers

    def update_image(self, container_name, image_name):
        """
        update a container's image,
        :param container_name: `class`:`str`, container name
        :param image_name: `class`:`str`, the full image name, like alpine:3.3
        :return: `class`:`bool`, True if success, otherwise False.
        """
        code, container = self.get_container(container_name)
        if code != httplib.OK:
            self.logger.error("Container %s is not exists"
                              ". error code %s, error message %s", container_name, code,
                              container)
            return False

        _, old_image_name, _ = utils.parse_image_name(container.image)
        repository, name, version = utils.parse_image_name(image_name)
        if not repository or repository.lower() != DOCKER_NEG:
            self.logger.error("You image %s must have"
                              "a 'docker.neg/' prefix string", image_name)
            return False

        if not repo.image_exists(name, tag=version):
            self.logger.error("You image %s must be location "
                              "in docker.neg repository.", image_name)
            return False

        if old_image_name.lower() != name.lower():
            self.logger.error("You image %s must be same "
                              "with container's Image %s.", image_name, container.image)
            return False

        code, result = self.update(container_name, tag=version)
        if code != httplib.OK:
            self.logger.error("Update container %s with image "
                              "failure, code %s, result %s", container_name, code,
                              result)
            return False

        return True

    def update_image_2(self, container_name, image_name):
        """
        update a container's image,
        :param container_name: `class`:`str`, container name
        :param image_name: `class`:`str`, the full image name, like alpine:3.3
        :return: `class`:`bool`, True if success, otherwise False.
        """
        code, container = self.get_container(container_name)
        if code == httplib.NOT_FOUND:
            raise ContainerNotFound(container_name)
        elif code != httplib.OK:
            raise GeneralError(code)

        _, old_image_name, _ = utils.parse_image_name(container.image)
        repository, name, version = utils.parse_image_name(image_name)
        if not repository or repository.lower() != DOCKER_NEG:
            image_name = '{0}/{1}:{2}'.format(DOCKER_NEG, name, version)

        if not repo.image_exists(name, tag=version):
            raise ImageNotFound("{0} do not location in docker.neg repository.".format(image_name))

        if old_image_name.lower() != name.lower():
            raise ImageConflict("{0} is not be same with container's Image.".format(image_name))

        code, result = self.pull_image(name, version)
        if code != httplib.OK:
            raise GeneralError(
                'pull image {0}:{1} failure, status code {2}, result: {3}'.format(name, version, code, result))

        code, result = self.update(container_name, tag=version)
        if code != httplib.OK:
            raise GeneralError(
                'Update container {0} failure, status code {1}, result: {2}'.format(container_name, code, result))

        return True


class DockerFactory(object):
    def __init__(self):
        self._dockers = {}

    def get(self, server_name):
        server_name = server_name.lower()
        if server_name not in self._dockers:
            self._dockers[server_name] = Docker(server_name)
        return self._dockers[server_name]
