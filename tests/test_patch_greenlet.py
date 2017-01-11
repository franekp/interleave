import unittest
import sys
import greenlet
import inspect

from interleave import patch_greenlet


class BaseTestPatchGreenlet(object):
    def test_main(self):
        self.assert_does_not_work()
        patch_greenlet.activate()
        self.assert_works()
        patch_greenlet.deactivate()
        self.assert_does_not_work()


class TestUsageScenario1(BaseTestPatchGreenlet, unittest.TestCase):
    def assert_stack_looked_like(self, res, expected):
        self.assertEqual(res['call'], expected)
        self.assertEqual(res['return'], list(reversed(expected)))
        for f in expected:
            self.assertIn(f, res['line'])

    def assert_works(self):
        res = self.usage_scenario_1()
        self.assert_stack_looked_like(
            res, ['no_op', 'func_A', 'func_B', 'func_C']
        )

    def assert_does_not_work(self):
        res = self.usage_scenario_1()
        self.assert_stack_looked_like(res, ['no_op'])

    def usage_scenario_1(self):
        func_log = {'call': [], 'return': [], 'line': []}
        def func_C():
            pass
        def func_B():
            return func_C()
        def func_A():
            return func_B()
        thread = greenlet.greenlet(func_A)

        def no_op():
            pass

        def trace(frame, event, arg):
            fname = inspect.getframeinfo(frame)[2]
            if event in func_log:
                func_log[event].append(fname)
            if not thread.dead:
                thread.switch()
            return trace

        sys.settrace(trace)
        no_op()
        sys.settrace(None)
        return func_log


class TestIsActive(BaseTestPatchGreenlet, unittest.TestCase):
    def assert_works(self):
        self.assertTrue(patch_greenlet.is_active())

    def assert_does_not_work(self):
        self.assertFalse(patch_greenlet.is_active())
