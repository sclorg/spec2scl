#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from spec2scl.version import version

try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup, find_packages

if sys.version_info < (2, 7):
    install_requires = ['argparse']
else:
    install_requires = []

description = """spec2scl is a tool to convert RPM specfiles to SCL-style specfiles."""

setup(
    name = 'spec2scl',
    version = version,
    description = "Convert RPM specfiles to be SCL ready",
    long_description = description,
    keywords = 'rpm, spec, specfile, convert, scl, dsc',
    author = 'Bohuslav "Slavek" Kabrda',
    author_email = 'bkabrda@redhat.com',
    url = 'https://bitbucket.org/bkabrda/spec2scl/',
    license = 'MIT',
    packages = find_packages(exclude = ['tests']),
    setup_requires = ['pytest',
                      'flexmock >= 0.9.3'
                     ] + install_requires,
    install_requires = install_requires,
    entry_points={'console_scripts':['spec2scl = spec2scl.bin:main']},
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Build Tools',
                   'Topic :: System :: Software Distribution',
                  ]
)
