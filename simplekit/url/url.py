import six
from six.moves import urllib

from .path import Path
from .query import Query

import util

__author__ = 'benjamin.c.yan'

SAFE_SEGMENT_CHARS = ":@-._~!$&'()*+,;="

DEFAULT_PORTS = {
    'ftp': 21,
    'ssh': 22,
    'http': 80,
    'https': 443,
}

class URL(object):
    def __init__(self, url):
        self._host = self._port = None
        self.username = self.password = None
        self._scheme, self._netloc, path, query, fragment = urllib.parse.urlsplit(url)
        self._path = Path(path)
        self._query = Query(query)
        self._fragment = fragment

        if not self.port:
            self._port = DEFAULT_PORTS.get(self._scheme)

    @property
    def path(self):
        return self._path

    @property
    def query(self):
        return self._query

    @property
    def scheme(self):
        return self._scheme

    @scheme.setter
    def scheme(self, scheme):
        if isinstance(scheme, six.string_types):
            self._scheme = scheme.lower()

    @property
    def netloc(self):
        return self._netloc

    @property
    def url(self):
        return str(self)

    @property
    def host(self):
        pass

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port):
        if port is None:
            self._port = DEFAULT_PORTS.get(self.scheme)
        elif util.is_valid_port(port):
            self._port = int(str(port))
        else:
            raise ValueError("Port is invalid port %s" % port)

    @property
    def fragment(self):
        return self._fragment

    def __str__(self):
        url = urllib.parse.urlunsplit((
            self.scheme,
            self.netloc,
            str(self.path),
            self.query.encode(),
            self.fragment
        ))
        return url
