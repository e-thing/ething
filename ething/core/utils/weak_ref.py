# coding: utf-8

import weakref

__all__ = ['weak_ref', 'proxy_method', 'LostReferenceException']


class BoundMethodWeakref:
    def __init__(self, func):
        self.func_name = func.__name__
        self.wref = weakref.ref(func.__self__)  # __self__ returns the instance

    def __call__(self):
        func_cls = self.wref()
        if func_cls is None:  # lost reference
            return None
        else:
            func = getattr(func_cls, self.func_name)
            return func


def weak_ref(callback):
    if getattr(callback, '__self__', None) is not None:  # is a bound method?
        return BoundMethodWeakref(callback)
    else:
        return weakref.ref(callback)


class LostReferenceException(Exception):
    pass


class BoundMethodWeakProxy:
    def __init__(self, func):
        self.func_name = func.__name__
        self.wref = weakref.ref(func.__self__)  # __self__ returns the instance

    def get_func(self, silent=False):
        func_cls = self.wref()
        if func_cls is None:  # lost reference
            if not silent:
                raise LostReferenceException('lost reference')
        else:
            return getattr(func_cls, self.func_name)

    def __call__(self, *args, **kwargs):
        return self.get_func()(*args, **kwargs)

    def __eq__(self, other):
        return self.get_func(True) == other


def proxy_method(func):
  if getattr(func, '__self__', None) is not None:
    return BoundMethodWeakProxy(func)
  else:
    return func