import unittest
import threading

import interleave


class Increment(object):
    def __init__(self):
        self.cnt = 0
        self.lock = threading.Lock()

    def increment(self):
        interleave.breakpoint()
        with lock:
            interleave.breakpoint()
            new = self.cnt + 1
            interleave.breakpoint()
            self.cnt = new
            interleave.breakpoint()
        interleave.breakpoint()

    def get(self):
        return self.cnt


class TestIncrement(object): #unittest.TestCase):
    patterns1 = ('0',)
    patterns2 = ('10', '100', '101', '10101', '101001', '10110101')
    patterns3 = ('012', '0120', '012102')

    @interleave.test_patterns(patterns1)
    def test_increment_1(self):
        inc = Increment()
        threads = [threading.Thread(target=inc.increment) for i in range(1)]
        for t in threads:
            t.join()
        interleave.run([inc.increment] * 1)
        self.assertEqual(inc.get(), 1)

    @interleave.test_patterns(patterns2)
    def test_increment_2(self):
        inc = Increment()
        interleave.run([inc.increment] * 2)
        self.assertEqual(inc.get(), 2)

    @interleave.test_patterns(patterns3)
    def test_increment_3(self):
        inc = Increment()
        interleave.run([inc.increment] * 3)
        self.assertEqual(inc.get(), 3)
