#!/usr/bin/env python

import os
from setuptools import setup, Extension
from pip.req import parse_requirements


patchbuiltins = Extension(
    'patch_c_func',
    sources=['patch_c_func.c'],
)

req_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "requirements.txt"
)
install_reqs = parse_requirements(req_file , session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='interleave',
    version='0.1',
    description=('Library for testing thread-safety in a repeatable-deterministic way.'),
    ext_modules=[patchbuiltins],
    packages=[
        'interleave',
    ],
    package_data={},
    install_requires=reqs,
)
