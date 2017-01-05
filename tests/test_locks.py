import threading
import thread
import functools

import interleave.mocks
import interleave.core
import interleave.monkeypatch
from .stdlib_suite import py2_lock_tests as lock_tests


LIMIT = 10
def decorate_method(m):
    @interleave.mocks.mock_thread(
        lambda: interleave.core.BoundedGeneratorScheduler(LIMIT)
    )
    @functools.wraps(m)
    def newm(self, *args, **kwargs):
        assert lock_tests.start_new_thread is interleave.mocks._start_new_thread
        assert lock_tests.get_ident is interleave.mocks._get_ident
        assert thread.start_new_thread is interleave.mocks._start_new_thread
        assert thread.allocate_lock is interleave.mocks._allocate_lock
        assert threading.Lock is interleave.mocks._allocate_lock
        assert threading._allocate_lock is interleave.mocks._allocate_lock
        assert threading._start_new_thread is interleave.mocks._start_new_thread
        if hasattr(self, 'locktype'):
            assert self.locktype is interleave.mocks._allocate_lock
        print m.__name__
        return m(self, *args, **kwargs)
    return newm
def decorate_class(cls):
    for method in cls.__dict__:
        if method.startswith('test_'):
            setattr(cls, method, decorate_method(cls.__dict__[method]))
def decorate_module(mod):
    for attr in dir(mod):
        if attr.endswith('Tests'):
            decorate_class(getattr(mod, attr))
decorate_module(lock_tests)


class LockTests(lock_tests.LockTests):
    locktype = staticmethod(threading.Lock)

class RLockTests(lock_tests.RLockTests):
    locktype = staticmethod(threading.RLock)

class EventTests(lock_tests.EventTests):
    eventtype = staticmethod(threading.Event)

class ConditionAsRLockTests(lock_tests.RLockTests):
    # An Condition uses an RLock by default and exports its API.
    locktype = staticmethod(threading.Condition)

class ConditionTests(lock_tests.ConditionTests):
    condtype = staticmethod(threading.Condition)

class SemaphoreTests(lock_tests.SemaphoreTests):
    semtype = staticmethod(threading.Semaphore)
