import threading
try:
    # python 2
    from thread import error as ThreadError
except:
    # python 3
    ThreadError = RuntimeError

import greenlet


class DeadLockError(Exception):
    pass


class Lock(object):
    def __init__(self):
        self._locked = False

    def acquire(self, blocking=True):
        thread = greenlet.getcurrent()
        scheduler = thread.scheduler
        assert thread.waiting_for is None

        scheduler.switch_before_acquire_lock()

        if self._locked:
            if blocking:
                thread.waiting_for = self
                scheduler.switch_after_blocking_on_locked_lock()
                return True
            else:
                return False
        else:
            self._locked = True
            return True

    def release(self):
        thread = greenlet.getcurrent()
        scheduler = thread.scheduler
        assert thread.waiting_for is None

        if self._locked:
            threads_waiting = scheduler.get_threads_waiting_for(self)
            if not threads_waiting:
                self._locked = False
                scheduler.switch_after_release_lock_when_no_threads_waiting()
            else:
                scheduler.choose_thread_to_acquire_lock(
                    threads_waiting
                ).waiting_for = None
                scheduler.switch_after_release_lock_to_another_thread()
        else:
            raise ThreadError('release unlocked lock')

    def locked(self):
        return self._locked

    def __enter__(self):
        self.acquire()

    def __exit__(self, *args, **kwargs):
        self.release()


class AbstractScheduler(object):
    def choose_thread(self, threads):
        raise NotImplementedError

    def choose_thread_to_awake(self, threads):
        return self.choose_thread(threads)

    def choose_thread_to_acquire_lock(self, threads):
        return self.choose_thread(threads)

    def switch(self):
        raise NotImplementedError

    def switch_on_breakpoint(self):
        self.switch()

    def switch_before_acquire_lock(self):
        """Context switch just before trying to acquire lock to catch bugs
        when locks are acquired too late.
        """
        self.switch()

    def switch_after_blocking_on_locked_lock(self):
        """It is crucially important that this method calls switch() because
        otherwise threads would not block on locks.
        """
        self.switch()

    def switch_after_release_lock(self):
        """Context switch just after releasing lock to catch bugs when locks
        are released too early.
        """
        self.switch()

    def switch_after_release_lock_to_another_thread(self):
        self.switch_after_release_lock()

    def switch_after_release_lock_when_no_threads_waiting(self):
        self.switch_after_release_lock()


class Scheduler(AbstractScheduler):
    def __init__(self):
        thread = greenlet.getcurrent()
        thread.scheduler = self
        thread.waiting_for = None
        self.threads = [thread]

    def create_thread(self, callable):
        thread = greenlet.greenlet(callable)
        thread.scheduler = self
        thread.waiting_for = None
        self.threads.append(thread)
        return id(thread)

    def get_threads_waiting_for(self, x):
        return [t for t in self.threads if t.waiting_for is x]

    def switch(self):
        thread = greenlet.getcurrent()
        # get threads that don't wait on any lock
        threads = self.get_threads_waiting_for(None)
        if not threads:
            raise DeadLockError
        self.choose_thread_to_awake(threads).switch()
        if thread.waiting_for is not None:
            self.switch()
