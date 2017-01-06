#!/usr/bin/env python

import sys
import os
import subprocess

import unittest


def run_tests():
    loader = unittest.TestLoader()
    tests = loader.discover(
        '.', top_level_dir='.',
    )
    unittest.runner.TextTestRunner().run(tests)

subprocess.check_call("python setup.py build 2>&1 > /dev/null", shell=True)
subprocess.check_call("python setup.py install 2>&1 > /dev/null", shell=True)

os.chdir('tests') # chdir to tests/ so that local version of interleave module
# does not hide installed one (only installed one has c extensions available)
run_tests()
