__author__ = 'benjamin.c.yan'


class Bear(object):
    def __init__(self, other=None):
        if isinstance(other, (dict, Bear)):
            for key in other:
                self[key] = other[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __getitem__(self, key):
        if not key.startswith('_'):
            return self.__dict__.get(key)

    def __setitem__(self, key, value):
        if not key.startswith('_'):
            self.__dict__[key] = value

    def __getattr__(self, item):
        if not item.startswith('_'):
            return self[item]

    def __str__(self):
        return '%s (%s)' % (self.__class__.__name__, repr(self))

    def __repr__(self):
        keys = sorted(self.__dict__.keys())
        text = ', '.join('%s=%r' % (key, self[key]) for key in keys)
        return '{%s}' % text


if __name__ == '__main__':
    pass
    bear = Bear()
    bear.name = 'benjamin'
    print bear
    for key1 in bear:
        print key1, bear[key1], bear.name

    bear['sex'] = 21
    print 'sex', bear.sex, repr(bear), str(bear)

    other = dict(name='benjamin', sex='male', high=175)
    print Bear(other)

    import json
    import simplekit.objson
    print simplekit.objson.dumps2(object())