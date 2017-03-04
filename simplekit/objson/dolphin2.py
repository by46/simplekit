import functools
import json
import re
from keyword import iskeyword

__author__ = 'benjamin.c.yan'

_re_encode = re.compile('[^a-zA-Z0-9]', re.MULTILINE)


def object2dict(obj):
    return obj.__dict__


def object_hook(obj):
    return Dolphin(obj)


def empty(other=None):
    """
    new an empty object
    basic usage ::
    >>> from simplekit import objson
    >>> obj = objson.empty()
    >>> obj2 = objson.empty(dict(name='benjamin', sex='male'))
    >>> assert obj2.name == 'benjamin'
    >>> assert obj2.sex == 'male'

    :param other: :class:``dict``, initialize properties
    :return: an instance of :class:``Dolphin``
    """
    return Dolphin(other)


class Dolphin(object):
    def __init__(self, other=None):
        if other:
            if isinstance(other, Dolphin):
                other = other.__dict__

            self.__dict__.update(other)

    def __iter__(self):
        return iter(self.__dict__)

    def __getitem__(self, key):
        key = str(key)
        if not key.startswith('_'):
            return self.__dict__.get(key)

    def __setitem__(self, key, value):
        key = str(key)
        if not key.startswith('_'):
            self.__dict__[key] = value

    def __getattr__(self, name):
        name = str(name)
        if not name.startswith('_'):
            if name in self:
                return self[name]
            elif name.startswith('m') and (iskeyword(name[1:]) or len(name) > 1 and name[1].isdigit()):
                return self[name[1:]]
            elif '_' in name:
                return self[_re_encode.sub('-', name)]

    def __str__(self):
        return '%s (%s)' % (self.__class__.__name__, repr(self))

    def __repr__(self):
        keys = sorted(self.__dict__.keys())
        text = ', '.join('%s=%r' % (key, self[key]) for key in keys)
        return '{%s}' % text

    def __eq__(self, other):
        return str(self) == str(other)


def dumps(obj, *args, **kwargs):
    """Serialize a object to string

    Basic Usage:

    >>> import simplekit.objson
    >>> obj = {'name':'wendy'}
    >>> simplekit.objson.dumps(obj)
    '{"name": "wendy"}'

    :param obj: a object which need to dump
    :param args: Optional arguments that :func:`json.dumps` takes.
    :param kwargs: Keys arguments that :py:func:`json.dumps` takes.
    :return: string
    """
    kwargs['default'] = object2dict

    return json.dumps(obj, *args, **kwargs)


def dump(obj, fp, *args, **kwargs):
    """Serialize a object to a file object.

    Basic Usage:

    >>> import simplekit.objson
    >>> from cStringIO import StringIO
    >>> obj = {'name': 'wendy'}
    >>> io = StringIO()
    >>> simplekit.objson.dump(obj, io)
    >>> io.getvalue()
    '{"name": "wendy"}'

    :param obj: a object which need to dump
    :param fp: a instance of file object
    :param args: Optional arguments that :func:`json.dump` takes.
    :param kwargs: Keys arguments that :func:`json.dump` takes.
    :return: None
    """
    kwargs['default'] = object2dict

    json.dump(obj, fp, *args, **kwargs)


def _load(fn):
    @functools.wraps(fn)
    def tmp(src, *args, **kwargs):
        """Deserialize json string to a object

        Provide a brief way to represent a object,  Can use ``.`` operate access
        Json object property

        Basic Usage:

        >>> from simplekit import objson
        >>> text = r'{"Name":"wendy"}'
        >>> objson.loads(text)
        {"name": "wendy"}

        :param src: string or file object
        :param args: Optional arguments that :func:`json.load` takes.
        :param kwargs: Keys arguments that :func:`json.loads` takes.
        :return: :class:`object` or :class:`list`
        """
        try:
            kwargs['object_hook'] = object_hook
            return fn(src, *args, **kwargs)
        except ValueError:
            return None

    return tmp


load = _load(json.load)
loads = _load(json.loads)


if __name__ == '__main__':
    import doctest
    doctest.testmod()