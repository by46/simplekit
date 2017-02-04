import functools
import httplib

from furl import furl

from .rest import send_rest

__author__ = 'benjamin.c.yan'
SUFFIX = ['.com', '.neg', '.io']


def request(method='GET'):
    """send restful post http request decorator

    Provide a brief way to manipulate restful api,

    :param method: :class:`str`,

    :return: :class:`func`
    """

    def decorator(func):
        @functools.wraps(func)
        def action(self, *args, **kwargs):
            f = furl(self.server)
            path, body = func(self, *args, **kwargs)

            # deal with query string
            query = dict()
            if isinstance(path, tuple):
                path, query = path
            f.path.add(path)
            f.query.set(query)

            status_code, result = send_rest(f.url, method=method.upper(),
                                            body=body,
                                            session=self.session,
                                            headers=self.headers)
            if status_code != httplib.OK:
                self.logger.error("{impl} {url} headers: {headers}, code: {code}".format(
                    impl=method, url=f.url, headers=self.headers, code=status_code))
            return status_code, result

        return action

    return decorator


def parse_image_name(name):
    """
    parse the image name into three element tuple, like below:
    (repository, name, version)
    :param name: `class`:`str`, name
    :return: (repository, name, version)
    """
    name = name or ""
    if '/' in name:
        repository, other = name.split('/')
        if not is_docker_hub(repository):
            repository, other = None, name
    else:
        repository, other = None, name

    if ':' in other:
        name, version = other.split(':')
    else:
        name, version = other, 'latest'

    return repository, name, version


def is_docker_hub(repository):
    repository = repository.lower()
    return any([repository.endswith(suffix) for suffix in SUFFIX])
