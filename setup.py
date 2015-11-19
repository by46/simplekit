#!/usr/bin/env python

__author__ = "benjamin.c.yan"

import os
import re
import sys

from codecs import open

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'dolphin'
]

requires = []

version = ''
with open('dolphin/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='dolphin',
    version=version,
    description='A simple JSON serialize and deserialize tools',
    long_description="A simple JSON serialize and deserialize tools",
    author='Benjamin Yan',
    author_email='ycs_ctbu_2010@126.com',
    url='https://github.com/by46/dolphin',
    packages=packages,
    package_data={'': ['LICENSE', 'NOTICE']},
    package_dir={'dolphin': 'dolphin'},
    include_package_data=True,
    install_requires=requires,
    license='The MIT License',
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)