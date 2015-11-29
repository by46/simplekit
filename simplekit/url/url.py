from posixpath import normpath
from urlparse import urlsplit

import six
from six.moves.urllib.parse import quote, unquote

__author__ = 'benjamin.c.yan'

SAFE_SEGMENT_CHARS = ":@-._~!$&'()*+,;="


class Path(object):
    def __init__(self, path):
        self.segments = []
        self.is_absolute = True
        self.load(path)

    @property
    def is_dir(self):
        return (self.segments == [] or
                (self.segments and self.segments[-1] == ''))

    @property
    def is_file(self):
        return not self.is_dir

    def load(self, path):
        if not path:
            segments = []
        elif isinstance(path, six.string_types):
            segments = self._segment_from_path(path)
        else:  # list interface
            segments = path

        if len(segments) > 1 and segments[0] == '':
            segments.pop(0)

        self.segments = [unquote(segment) for segment in segments]
        return self

    def normalize(self):
        """
        Normalize the path. Turn /file/title/../author to /file/author

        :return: <self>
        """
        if str(self):
            normalized = normpath(str(self)) + ('/' * self.is_dir)
            if normalized.startswith('//'):  # http://bugs.python.org/636648
                normalized = '/' + normalized.lstrip('/')
            self.load(normalized)
        return self

    def set(self, path):
        self.load(path)
        return self

    def remove(self, path=None):
        if path is None:
            self.load('')
        else:
            segments = path
            if isinstance(path, six.string_types):
                segments = self._segment_from_path(path)
        return self

    def __str__(self):
        segments = list(self.segments)
        if self.is_absolute:
            if not segments:
                segments = ['', '']
            else:
                segments.insert(0, '')

        return self._path_from_segments(segments)

    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, str(self))

    def __bool__(self):
        return len(self.segments) > 0

    __nonzero__ = __bool__

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self == other

    # TODO(benjamin): incomplete
    @staticmethod
    def _segment_from_path(path):
        return [unquote(segment) for segment in path.split('/')]

    # TODO(benjamin): incomplete
    @staticmethod
    def _path_from_segments(segments):
        if '%' not in '/'.join(segments):
            segments = [quote(segment) for segment in segments]
        return '/'.join(segments)


class Query(object):
    def __init__(self, query):
        pass


class URL(object):
    def __init__(self, url):
        self.scheme, self.netloc, path, query, fragment = urlsplit(url)
        self._path = Path(path)
        self._query = Query(query)


def remove_path_segments(segments, removes):
    """Removes the removes from the tail of segments.

    Examples:
        >>> # '/a/b/c' - 'b/c' == '/a/'
        >>> assert remove_path_segments(['', 'a', 'b', 'c'], ['b', 'c']) == ['', 'a', '']
        >>> # '/a/b/c' - '/b/c' == '/a
        >>> assert remove_path_segments(['', 'a', 'b', 'c'], ['', 'b', 'c']) == ['', 'a']

    :param segments:  :class:`list`, a list of the path segment
    :param removes:  :class:`list`, a list of the path segment
    :return:  :class:`list`, The list of all remaining path segments after all segments
        in ``removes`` have been removed from the end of ``segments``. If no segment
        from ``removes`` were removed from the ``segments``, the ``segments`` is
        return unmodified.

    """

    if segments == ['']:
        segments.append('')
    if removes == ['']:
        removes.append('')

    if segments == removes:
        ret = []
    elif len(removes) > len(segments):
        ret = segments
    else:
        # TODO(benjamin): incomplete
        pass
    return ret