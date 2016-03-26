"""Provide a brief way to threading

"""

import threading

__author__ = 'benjamin.c.yan'


class StoppableThread(threading.Thread):
    def __init__(self, daemon=True, group=None, target=None, name=None, args=(), kwargs={}):
        super(StoppableThread, self).__init__(group, target, name, args, kwargs)
        self.daemon = daemon
        self._stopped_event = threading.Event()

    def start(self):
        self.on_thread_start()
        threading.Thread.start(self)

    def stop(self):
        self._stop_event.set()
        self.on_thread_stop()

    @property
    def stopped_event(self):
        return self._stopped_event

    def should_keep_running(self):
        return not self._stopped_event.is_set()

    def on_thread_stop(self):
        pass

    def on_thread_start(self):
        pass


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
