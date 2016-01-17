__author__ = 'benjamin.c.yan'

_absent = object()


def callable_attr(obj, attr):
    return hasattr(obj, attr) and callable(getattr(obj, attr))


def utf8(o, default=_absent):
    try:
        return o.encode('utf8')
    except:
        return o if default is _absent else default


def is_valid_port(port):
    port = str(port)
    if not port.isdigit() or int(port) == 0 or int(port) > 65535:
        return False
    return True
