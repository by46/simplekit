"""Provide a brief way to threading

"""

import threading

__author__ = 'benjamin.c.yan'


class StoppableThread(threading.Thread):
    def __init__(self, daemon=True, group=None, target=None, name=None, args=(), kwargs={}):
        super(StoppableThread, self).__init__(group, target, name, args, kwargs)
        self.daemon = daemon
        self.__stop_event = threading.Event()

    def run(self):
        while not self.__stop_event.is_set():
            self.process()

    def process(self):
        raise NotImplementedError("please override it")

    def stop(self):
        self.__stop_event.set()


class LockMixin(object):
    def __init__(self):
        self.__lock = threading.Lock()

    @property
    def lock(self):
        return self.__lock

    def __enter__(self):
        self.lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()

    @staticmethod
    def method_lock(fn):
        def tmp(self, *args, **kwargs):
            try:
                self.lock.acquire()
                fn(self, *args, **kwargs)
            finally:
                self.lock.release()

        return tmp
