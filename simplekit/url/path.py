from posixpath import normpath

import six
from six.moves.urllib.parse import quote, unquote

__author__ = 'benjamin.c.yan'


def remove_path_segments(segments, removes):
    """Removes the removes from the tail of segments.

    Examples::
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
        removes2 = list(removes)
        if len(removes) > 1 and removes[0] == '':
            removes2.pop(0)

        if removes2 and removes2 == segments[-1 * len(removes2):]:
            ret = segments[:len(segments) - len(removes2)]
            if removes[0] != '' and ret:
                ret.append('')
        else:
            ret = segments
    return ret


# TODO(benjamin): incomplete
def join_path_segments(*args):
    """Join multiple list of path segments

    This function is not encoding aware, it does not test for, or changed the
    encoding of the path segments it's passed.

    Example::
        >>> assert join_path_segments(['a'], ['b']) == ['a','b']
        >>> assert join_path_segments(['a',''], ['b']) == ['a','b']
        >>> assert join_path_segments(['a'], ['','b']) == ['a','b']
        >>> assert join_path_segments(['a',''], ['','b']) == ['a','','b']
        >>> assert join_path_segments(['a','b'], ['c','d']) == ['a','b','c','d']

    :param args: optional  arguments
    :return: :class:`list`, the segment list of the result path
    """
    finals = []
    for segments in args:
        if not segments or segments[0] == ['']:
            continue
        elif not finals:
            finals.extend(segments)
        else:
            # Example #1: ['a',''] + ['b'] == ['a','b']
            # Example #2: ['a',''] + ['','b'] == ['a','','b']
            if finals[-1] == '' and (segments[0] != '' or len(segments) > 1):
                finals.pop(-1)
            # Example: ['a'] + ['','b'] == ['a','b']
            elif finals[-1] != '' and segments[0] == '' and len(segments) > 1:
                segments.pop(0)
            finals.extend(segments)
    return finals


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

            base = ([''] if self.is_absolute else []) + self.segments
            self.load(remove_path_segments(base, segments))
        return self

    def add(self, path):
        new_segments = path
        if isinstance(path, six.string_types):
            new_segments = self._segment_from_path(path)

        if self.segments == [''] and new_segments and new_segments[0] != '':
            new_segments.insert(0, '')

        segments = self.segments
        if self.is_absolute and segments and segments[0] != '':
            segments.insert(0, '')

        self.load(join_path_segments(segments, new_segments))
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
