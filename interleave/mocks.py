import greenlet
import decorator
import contextlib2

from interleave import concurrency
from interleave.monkeypatch import PatchEverywhere


_LockType = concurrency.Lock

def _start_new_thread(function, args, kwargs=None):
    if kwargs is None:
        kwargs = {}
    scheduler = greenlet.getcurrent().scheduler
    return scheduler.create_thread(lambda: function(*args, **kwargs))

def _interrupt_main():
    thread = greenlet.getcurrent()
    while thread.parent:
        thread = thread.parent
    thread.throw(KeyboardInterrupt)

def _exit():
    raise greenlet.GreenletExit

_allocate_lock = concurrency.Lock

def _get_ident():
    return id(greenlet.getcurrent())

def _sleep(_):
    scheduler = greenlet.getcurrent().scheduler
    scheduler.switch()


def get_patchers():
    import thread
    import time
    names = [
        'LockType', 'start_new_thread', 'interrupt_main', 'exit',
        'allocate_lock', 'get_ident'
    ]
    return [
        PatchEverywhere(getattr(thread, name), globals()['_' + name])
        for name in names
    ] + [PatchEverywhere(time.sleep, _sleep)]


class mock_thread(contextlib2.ExitStack):
    def __init__(self, scheduler):
        super(mock_thread, self).__init__()
        if not isinstance(scheduler, concurrency.BaseScheduler):
            # support classes and factory functions as arguments
            scheduler = scheduler()
        if not isinstance(scheduler, concurrency.BaseScheduler):
            raise TypeError('scheduler must be a subclass of BaseScheduler')
        self.scheduler = scheduler

    def __enter__(self):
        for patcher in get_patchers():
            self.enter_context(patcher)
        self.enter_context(self.scheduler)
