import gc
import inspect

from decorator import decorator


class PatchEverywhere(object):
    # FIXME:
    # - this does not yet work for class attributes
    # - this does not work for stack frames (locals()) and probably never will
    DEBUG = False

    def __init__(self, old, new):
        self.old = old
        self.new = new
        self.places = None

    def __call__(self, func):
        @decorator
        def decorate(func, *args, **kwargs):
            with self:
                res = func(*args, **kwargs)
            return res
        return decorate(func)

    def is_active(self):
        refs = gc.get_referrers(self.old)
        refs = [ref for ref in refs if not inspect.isframe(ref)]
        return (refs[0] is self.__dict__) and (len(refs) == 1)

    def add_dict(self, m):
        for key, val in m.items():
            if val is self.old:
                self.places.append((m, key))
                m[key] = self.new

    def add_list(self, m):
        for key, val in enumerate(m):
            if val is self.old:
                self.places.append((m, key))
                m[key] = self.new

    def add_referrer(self, m):
        if isinstance(m, dict):
            self.add_dict(m)
        elif isinstance(m, list):
            self.add_list(m)
        elif inspect.isframe(m):
            del m
        else:
            if self.DEBUG:
                print type(m)
                raise RuntimeError('unknown type of referrer')

    def __enter__(self):
        self.places = []
        refs = gc.get_referrers(self.old)
        for ref in refs:
            if ref is self.__dict__:
                continue
            self.add_referrer(ref)
        return self

    def __exit__(self, *args, **kwargs):
        for m, key in self.places:
            m[key] = self.old
        self.places = None
