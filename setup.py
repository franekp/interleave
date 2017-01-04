#!/usr/bin/env python

import os
from setuptools import setup
from pip.req import parse_requirements


req_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "requirements.txt"
)
install_reqs = parse_requirements(req_file , session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='interleave',
    version='0.1',
    description=('Mocks for deterministic unit tests for thread safety.'),
    packages=[
        'interleave',
    ],
    package_data={},
    install_requires=reqs,
)
