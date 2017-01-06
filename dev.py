#!/usr/bin/env python

import sys
import os
import subprocess

import bpython
from bpython.curtsies import FullCurtsiesRepl

def amend_path():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path = filter(lambda x: x not in ['', THIS_DIR], sys.path)

subprocess.check_call("python setup.py build > /dev/null", shell=True)
subprocess.check_call("python setup.py install > /dev/null", shell=True)

def new(cls, *args, **kwargs):
    amend_path()
    return object.__new__(cls, *args, **kwargs)
FullCurtsiesRepl.__new__ = classmethod(new)

bpython.embed()
