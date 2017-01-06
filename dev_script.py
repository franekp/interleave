import sys
import os
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path = filter(lambda x: x not in ['', THIS_DIR], sys.path)

from interleave import patch_greenlet
from sys import settrace

import inspect


def metatrace(frame, event, arg):
    print("metatrace!")
    print("%s::%s(%s)" % (inspect.getframeinfo(frame)[2], event, str(arg)))
    return metatrace

def g1():
    x = 5
    return g2()

def g2():
    a = 3
    return "g2 output"

def g():
    return g1()


import greenlet
thread = greenlet.greenlet(g)
def mytrace(frame, event, arg):
    print("%s::%s(%s)" % (inspect.getframeinfo(frame)[2], event, repr(arg)))
    #print(inspect.currentframe().f_back.f_code.co_name)
    if not thread.dead:
        thread.switch()
    return mytrace

patch_greenlet.activate()
settrace(mytrace)
print('x')
