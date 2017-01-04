import unittest

from interleave.monkeypatch import PatchEverywhere


PatchEverywhere.DEBUG = True


class TestPatchEverywhereContextManager(unittest.TestCase):
    def test_builtin(self):
        patched = lambda: None

        with PatchEverywhere(map, patched) as patcher:
            assert patcher.is_active()
            map()
            assert map is patched
        map(lambda x: x, [1, 2, 3])
        assert map is not patched

    def test_dict(self):
        patched = lambda x: x
        original = lambda: None
        dic = dict(entry=original)

        with PatchEverywhere(original, patched) as patcher:
            assert patcher.is_active()
            dic['entry']('spam')
            assert dic['entry'] is patched
        dic['entry']()
        assert dic['entry'] is not patched

    def test_list(self):
        patched = lambda x: x
        original = lambda: None
        li = [original]

        with PatchEverywhere(original, patched) as patcher:
            assert patcher.is_active()
            li[0]('spam')
            assert li[0] is patched
        li[0]()
        assert li[0] is not patched

    def test_globals(self):
        patched = lambda x: x
        original = lambda: None
        globals()['entry'] = original

        with PatchEverywhere(original, patched) as patcher:
            assert patcher.is_active()
            entry('spam')
            assert entry is patched
        entry()
        assert entry is not patched

    def test_module(self):
        patched = lambda x: 'patched'
        import threading
        from threading import Condition
        try:
            # PY3
            import queue
        except:
            # PY2
            import Queue as queue
        with PatchEverywhere(Condition, patched) as patcher:
            assert patcher.is_active()
            assert threading.Condition is patched
            from threading import Condition
            assert Condition is patched
            assert queue.Queue().not_empty == 'patched'
        from threading import Condition
        assert Condition is not patched
        assert threading.Condition is not patched


class TestPatchEverywhereDecorator(unittest.TestCase):
    def test_builtin(self):
        patched = lambda: None

        @PatchEverywhere(map, patched)
        def func():
            map()
            assert map is patched
        func()
        map(lambda x: x, [1, 2, 3])
        assert map is not patched

    def test_dict(self):
        patched = lambda x: x
        original = lambda: None
        dic = dict(entry=original)

        @PatchEverywhere(original, patched)
        def func():
            dic['entry']('spam')
            assert dic['entry'] is patched
        func()
        dic['entry']()
        assert dic['entry'] is not patched
