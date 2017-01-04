import greenlet
import decorator

from interleave import concurrency
from interleave.monkeypatch import PatchEverywhere


LockType = concurrency.Lock

def start_new_thread(function, args, kwargs=None):
    if kwargs is None:
        kwargs = {}
    scheduler = greenlet.getcurrent().scheduler
    return scheduler.create_thread(lambda: function(*args, **kwargs))

def interrupt_main():
    thread = greenlet.getcurrent()
    while thread.parent:
        thread = thread.parent
    thread.throw(KeyboardInterrupt)

def exit():
    raise greenlet.GreenletExit

allocate_lock = concurrency.Lock

def get_ident():
    return id(greenlet.getcurrent())

def sleep(_):
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
        PatchEverywhere(getattr(thread, name), globals()[name])
        for name in names
    ] + [PatchEverywhere(time.sleep, sleep)]


def decorate(f):
    for patcher in get_patchers:
        f = patcher(f)
    return f
