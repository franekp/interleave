import gc
import inspect

import contextlib2
from decorator import decorator


class PatchEverywhere(contextlib2.ContextDecorator):
    # FIXME:
    # - this does not yet work for class attributes
    # - this does not yet work for staticmethods, namedtuples etc. - patching
    #   attributes directly on objects instead of their __dict__
    # - this does not work for stack frames (locals()) and probably never will
    DEBUG = False

    def __init__(self, old, new):
        self.old = old
        self.new = new
        self.places = None

    def is_active(self):
        # used only in testing
        refs = gc.get_referrers(self.old)
        refs = [ref for ref in refs if not self.can_ignore_referrer(ref)]
        return (refs[0] is self.__dict__) and (len(refs) == 1)

    def can_ignore_referrer(self, ref):
        # used only in testing
        return inspect.isframe(ref) or isinstance(ref, staticmethod)

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
        else:
            if self.DEBUG and not self.can_ignore_referrer(m):
                msg = 'unknown type of referrer: '
                msg += str(type(m)) + '\n'
                msg += 'result of calling dir() on it: ' + str(dir(m)) + '\n'
                raise RuntimeError(msg)

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
