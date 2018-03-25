#!/usr/bin/env python

import os
from distutils.core import setup, Extension
from pip.req import parse_requirements


patch_c_func = Extension(
    'threadmock.patch_c_func',
    sources=['threadmock/patch_c_func.c'],
)

patch_greenlet = Extension(
    'threadmock.patch_greenlet',
    sources=['threadmock/patch_greenlet.c'],
)

req_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "requirements.txt"
)
install_reqs = parse_requirements(req_file , session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='threadmock',
    version='0.1',
    description=('Library for testing thread-safety in a repeatable-deterministic way.'),
    ext_modules=[patch_c_func, patch_greenlet],
    packages=[
        'threadmock',
    ],
    package_data={},
    install_requires=reqs,
)
