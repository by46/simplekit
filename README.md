simplekit
============

A simple and brief utility tools framework

[![Build Status](https://travis-ci.org/by46/simplekit.svg)](https://travis-ci.org/by46/simplekit)
[![Coverage Status](https://coveralls.io/repos/by46/simplekit/badge.svg?branch=master&service=github)](https://coveralls.io/github/by46/simplekit?branch=master)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/simplekit.svg)](https://pypi.python.org/pypi/simplekit/)
[![Latest Version](	https://img.shields.io/pypi/v/simplekit.svg)](https://pypi.python.org/pypi/simplekit/)
[![License](https://img.shields.io/pypi/l/simplekit.svg)](https://pypi.python.org/pypi/simplekit/)
[![Documentation Status](https://readthedocs.org/projects/simplekit/badge/?version=latest)](http://simplekit.readthedocs.org/en/latest/?badge=latest)


Documents
-----------
Document is available at [http://simplekit.readthedocs.org/en/latest/](http://simplekit.readthedocs.org/en/latest/)

simplekit is a simple and brief utility tools framework, include:

1. Objson - a json serialize and deserialize tool.

 
 Dynamic class template
 ----------------------------
 ```python
 
 def _item_setter(key):
    def _setter(item, value):
        item[key] = value

    return _setter


def _item_getter(key):
    def _getter(item):
        return item[key]

    return _getter
    
class JsonObject(object):
    __identifier__ = "dolphin"

    __slots__ = ('name', 'age')

    _data = dict()

    def __init__(self, kv):
        self._data.update(kv)

    def __getitem__(self, key):
        return self._data.get(key)

    def __setitem__(self, key, value):
        self._data[key] = value

    def __iter__(self):
        return self._data.__iter__()

    def __repr__(self):
        keys = sorted(self._data.keys())
        text = ', '.join(["%s=%r" % (key, self[key]) for key in keys])
        return '{%s}' % text

    name = property(_item_getter('name'), _item_setter('name'))
    age = property(_item_getter('age'), _item_setter('age'))
 ```


