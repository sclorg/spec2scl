#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rpm2scl.version import version

try:
    from setuptools import setup
except:
    from distutils.core import setup


description = """rpm2scl is a tool to convert RPM specfiles to SCL-style specfiles."""

setup(
    name = 'rpm2scl',
    version = version,
    description = "Convert RPM specfiles to be SCL ready",
    long_description = description,
    keywords = 'rpm, spec, specfile, convert, scl, dsc',
    author = 'Bohuslav "Slavek" Kabrda',
    author_email = 'bkabrda@redhat.com',
    url = 'https://bitbucket.org/bkabrda/rpm2scl/',
    license = 'MIT',
    packages = ['rpm2scl', ],
    setup_requires = ['pytest',
                      'flexmock >= 0.9.3'
                     ],
    entry_points={'console_scripts':['rpm2scl = rpm2scl.bin:main']},
    classifiers = ['Development Status :: 3 - Alpha',
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
