import threading
import functools

import mock
from decorator import decorator
import greenlet

from interleave.concurrency import BaseScheduler

'''
test method decorator names:
test_full, test_random, test_patterns
'''

class GeneratorScheduler(BaseScheduler):
    def __init__(self, generator):
        super(GeneratorScheduler, self).__init__()
        self.generator = generator

    def choose_thread(self, threads):
        return threads[next(self.generator) % len(threads)]


class SimpleGeneratorScheduler(GeneratorScheduler):
    def __init__(self):
        def gen():
            while True:
                for i in xrange(17):
                    yield i

        super(SimpleGeneratorScheduler, self).__init__(gen)
