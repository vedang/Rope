def cacheit(func):
    name = '_' + func.__name__
    def _wrapper(self, *args, **kwds):
        if not hasattr(self, name):
            setattr(self, name, func(self, *args, **kwds))
        return getattr(self, name)
    return _wrapper


class prevent_recursion(object):

    def __init__(self, default):
        self.default = default

    def __call__(self, func):
        name = '_calling_%s_' % func.__name__
        def newfunc(host, *args, **kwds):
            if getattr(host, name, False):
                return self.default()
            setattr(host, name, True)
            try:
                return func(host, *args, **kwds)
            finally:
                setattr(host, name, False)
        return newfunc
