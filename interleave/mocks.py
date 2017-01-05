import greenlet
import decorator
import contextlib2
import thread
import time

from interleave import concurrency
import patch_c_func


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


class mock_thread(contextlib2.ContextDecorator):
    nesting_level = 0

    def __init__(self, scheduler):
        super(mock_thread, self).__init__()
        if not isinstance(scheduler, concurrency.BaseScheduler):
            # support classes and factory functions as arguments
            scheduler = scheduler()
        if not isinstance(scheduler, concurrency.BaseScheduler):
            raise TypeError('scheduler must be a subclass of BaseScheduler')
        self.scheduler = scheduler

    def __enter__(self):
        self.scheduler.__enter__()
        if mock_thread.nesting_level == 0:
            patch_c_func.patch(thread.start_new_thread, _start_new_thread)
            patch_c_func.patch(thread.interrupt_main, _interrupt_main)
            patch_c_func.patch(thread.exit, _exit)
            patch_c_func.patch(thread.allocate_lock, _allocate_lock)
            patch_c_func.patch(thread.get_ident, _get_ident)
            patch_c_func.patch(time.sleep, _sleep)
        mock_thread.nesting_level += 1

    def __exit__(self, *args, **kwargs):
        mock_thread.nesting_level -= 1
        if mock_thread.nesting_level == 0:
            patch_c_func.unpatch(thread.start_new_thread)
            patch_c_func.unpatch(thread.interrupt_main)
            patch_c_func.unpatch(thread.exit)
            patch_c_func.unpatch(thread.allocate_lock)
            patch_c_func.unpatch(thread.get_ident)
            patch_c_func.unpatch(time.sleep)
        return self.scheduler.__exit__(*args, **kwargs)
