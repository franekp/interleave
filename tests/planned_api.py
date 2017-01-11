import unittest
import threading
# FIXME TODO 'threadmock' is a better name for this project!
from interleave import backtrack_test, whitebox_test, random_test


@interleave.defaults(max_depth=10, runs=1000)
class PlannedAPIExamples(unittest.TestCase):
    @random_test(runs=5000)
    def test_random(self):
        SUT = SystemUnderTest()
        SUT.start_bunch_of_threads()
        SUT.wait()

        self.assertSomething(SUT)

    @random_test  # default value of 'runs' argument is used
    def test_random_with_defaults(self):
        SUT = SystemUnderTest()
        SUT.start_bunch_of_threads()
        SUT.wait()

        self.assertSomething(SUT)

    # to consider: also have a possiblity of switch_when for random tests

    @backtrack_test(max_depth=8)
    def test_backtrack_catch_all(self, s):
        s.switch_when(...)
        s.switch_when(...)
        s.switch_when(...)
        s.switch_when(...)

        SUT = SystemUnderTest()
        SUT.start_bunch_of_threads()

        SUT.wait()
        self.assertSomething(SUT)

    @backtrack_test  # default value of 'max_depth' argument is used
    def test_backtrack_capture(self, s):
        # breakpoint constructor takes a predicate as arguments
        b1 = Breakpoint(...)
        b2 = Breakpoint(...)

        SUT = SystemUnderTest()
        SUT.start_bunch_of_threads()

        # t1, t2 are instances of threading.Thread
        # Breakpoint.capture_thread() is a context manager equivalent to
        # executing Breakpoint.acquire() and Breakpoint.release()
        with b1.capture_thread() as t1:
            t1.switch_when(...)
            # Thread.switch_when(...) takes a predicate as arguments. When the
            # thread on which switch_when() was called has processor and given
            # predicate is true, a context switch from this thread is allowed
            # to occur.
            # @backtrack_test decorator checks all possible thread interleavings
            # given that context switches are only allowed in moments specified
            # by previous switch_when calls.
            t1.switch_when(...)

        t2 = b2.acquire()
        t2.switch_when(...)
        t2.switch_when(...)
        t2.switch_when(...)
        # Breakpoint.acquire() waits until any of running threads match
        # breakpoint predicate/specification and pauses this thread.
        # For the thread to continue execution,
        # Breakpoint.release() has to be called

        # NOTE: if any of running threads match breakpoint condition _before_
        # Breakpoint.acquire() (or Breakpoint.capture_thread()) is called,
        # the thread is paused anyway
        b2.release()

        # s is an instance of interleave.State
        # s.switch_when(...) is equivalent to calling this method on every
        # thread (including threads that will be created in the future - this of
        # course applies only to the end of function currently decorated with
        # @backtrack_test)
        s.switch_when(...)

        SUT.wait()
        self.assertSomething(SUT)

    @backtrack_test
    def test_backtrack_create(self, s):
        SUT = SystemUnderTest()
        t1 = threading.Thread(target=SUT.do_work)
        t2 = threading.Thread(target=SUT.do_work)

        # NOTE: the switch_when stuff has to be called before the threads
        # are started; calling it on a running thread will raise an exception
        # this applies to [switch_when, run_until, run_while, throw] methods
        # they can only be called on a thread that is not yet started or
        # on a thread that is blocked on some breakpoint.
        # calling switch_when on a non-started thread will not change thread's
        # status; calling run_until, run_while or throw on a non-started thread
        # will change it's status to waiting-on-breakpoint
        t1.switch_when(...)
        t1.switch_when(...)
        t2.switch_when(...)
        t2.switch_when(...)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        self.assertSomething(SUT)

    @whitebox_test
    def test_whitebox_capture(self, s):
        b1 = Breakpoint(...)
        b2 = Breakpoint(...)

        SUT = SystemUnderTest()
        SUT.start_bunch_of_threads()

        t1 = b1.acquire()
        t2 = b2.acquire()

        t1.run_until(...)
        self.assertSomething(SUT)
        t2.run_until(...)
        # s.locals, s.func, s.cls, s.line are available here and store
        # state of the last non-main thread that had the processor
        # here it would be t2
        self.assertSomething(s.locals.some_variable)
        self.assertSomething(s.func)
        self.assertSomething(s.line)
        t1.run_while(...)
        self.assertSomething(SUT)
        t2.run_until(...)

        b1.release()
        b2.release()
        t1.join()
        t2.join()

        self.assertSomething(SUT)

    @whitebox_test
    def test_whitebox_create(self, s):
        SUT = SystemUnderTest()
        t1 = threading.Thread(target=SUT.do_work)
        t2 = threading.Thread(target=SUT.do_work)

        # NOTE: do not invoke Thread.start() in here!
        # because if you do so, control will reach these run_until() methods
        # after these (already started) threads were running for a while
        # probably already been in these points which conditions given to
        # run_until(...) were supposed to catch
        # this is why any invocation of run_until or run_while on a running
        # thread will raise an exception; they can only be invoked on a
        # non-started or waiting-on-breakpoint threads.

        # IMPLEMENTATION NOTE: calling run_until() on a non-started thread
        # places an implicit helper breakpoint on that thread and then starts it
        # so that to allow threading.Thread.start() code to execute
        # threading.Thread.start() waits for some threading.Event that is
        # signalled when the new thread has finished it's initialization
        # so run_until or run_while or throw on a non-started thread changes
        # it's status to waiting-on-breakpoint where breakpoint is not known to
        # the user so that user is left with run_until stuff.
        # TO CONSIDER: some way for the user to access this internal breakpoint
        t1.run_until(...)
        self.assertSomething(SUT)
        t2.run_until(...)
        t1.run_until(...)
        self.assertSomething(SUT)
        t1.run_until(...)
        t2.run_while(...)

        # instead of .join() - these threads not running, so cannot join()
        t1.run_until(is_alive=False)
        t2.run_until(is_alive=False)

        self.assertSomething(SUT)
