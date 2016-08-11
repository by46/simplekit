import json
import time

from simplekit import objson

__author__ = 'benjamin.c.yan'


def benchmark(fn):
    def mark(*args, **kwargs):
        now = time.time()
        result = fn(*args, **kwargs)
        print fn.__name__, 'time, ', time.time() - now
        return result

    return mark


@benchmark
def benchmark_objson(text, times=100000):
    for _ in xrange(times):
        objson.loads(text)


@benchmark
def benchmark_objson2(text, times=100000):
    for _ in xrange(times):
        objson.loads2(text)


@benchmark
def benchmark_json(text, times=100000):
    for _ in xrange(times):
        json.loads(text)


@benchmark
def benchmark_objson_get(text, times=1000000):
    obj = objson.loads(text)
    for _ in xrange(times):
        x = obj.name


@benchmark
def benchmark_objson2_get(text, times=1000000):
    obj = objson.loads2(text)
    for _ in xrange(times):
        x = obj.name


@benchmark
def benchmark_json_get(text, times=1000000):
    obj = json.loads(text)
    for _ in xrange(times):
        x = obj['name']


@benchmark
def benchmark_objson_set(text, times=1000000):
    obj = objson.loads(text)
    for _ in xrange(times):
        obj.name = 'benjamin2'


@benchmark
def benchmark_objson2_set(text, times=1000000):
    obj = objson.loads2(text)
    for _ in xrange(times):
        obj.name = 'benjamin2'


@benchmark
def benchmark_json_set(text, times=1000000):
    obj = json.loads(text)
    for _ in xrange(times):
        obj['name'] = 'benjamin2'


@benchmark
def benchmark_objson_set(text, times=1000000):
    obj = objson.loads(text)
    for _ in xrange(times):
        obj.name = 'benjamin2'


@benchmark
def benchmark_objson2_set(text, times=1000000):
    obj = objson.loads2(text)
    for _ in xrange(times):
        obj.name = 'benjamin2'


@benchmark
def benchmark_json_set(text, times=1000000):
    obj = json.loads(text)
    for _ in xrange(times):
        obj['name'] = 'benjamin2'


@benchmark
def benchmark_objson_dumps(text, times=100000):
    obj = objson.loads(text)
    for _ in xrange(times):
        objson.dumps(obj)


@benchmark
def benchmark_objson2_dumps(text, times=100000):
    obj = objson.loads2(text)
    for _ in xrange(times):
        objson.dumps2(obj)


@benchmark
def benchmark_json_dumps(text, times=100000):
    obj = json.loads(text)
    for _ in xrange(times):
        json.dumps(obj)


if __name__ == '__main__':
    text = '{"name": "benjamin.c.yan", "name2": "benjamin.c.yan",' \
           '"name3": "benjamin.c.yan", "name4": "benjamin.c.yan", ' \
           '"name5": "benjamin.c.yan", "name6": "benjamin.c.yan", ' \
           '"name7": "benjamin.c.yan", "name8": "benjamin.c.yan", ' \
           '"name9": "benjamin.c.yan", "name0": "benjamin.c.yan"}'

    benchmark_objson(text)
    # benchmark_objson2(text)
    benchmark_json(text)
    benchmark_objson_get(text)
    # benchmark_objson2_get(text)
    benchmark_json_get(text)
    benchmark_objson_set(text)
    # benchmark_objson2_set(text)
    benchmark_json_set(text)
    benchmark_objson_dumps(text)
    # benchmark_objson2_dumps(text)
    benchmark_json_dumps(text)
