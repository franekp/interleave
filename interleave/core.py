import threading
import functools

import mock
from decorator import decorator
import greenlet

from interleave.concurrency import Scheduler

'''
test method decorator names:
test_full, test_random, test_patterns
'''

class GeneratorScheduler(Scheduler):
    def __init__(self, generator):
        super(GeneratorScheduler, self).__init__()
        self.generator = generator

    def choose_thread(self, threads):
        return threads[next(self.generator) % len(threads)]
