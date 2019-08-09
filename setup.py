#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys

from spec2scl.version import version

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

if sys.version_info < (2, 7):
    install_requires = ['jinja2', 'argparse']
else:
    install_requires = ['jinja2']


description = "spec2scl is a tool to convert RPM specfiles to SCL-style specfiles."


setup(
    name='spec2scl',
    version=version,
    description="Convert RPM specfiles to SCL-style.",
    long_description=description,
    keywords='rpm, spec, specfile, convert, scl, dsc',
    author='Slavek Kabrda, Robert Kuska, Iryna Shcherbina',
    author_email='slavek@redhat.com, rkuska@redhat.com, ishcherb@redhat.com',
    maintainer='Jan Staněk',
    maintainer_email='jstanek@redhat.com',
    url='https://bitbucket.org/bkabrda/spec2scl/',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    package_data={'spec2scl': ['templates/*.spec']},
    setup_requires=['pytest-runner',
                    'flexmock >= 0.9.3'
                    ] + install_requires,
    install_requires=install_requires,
    tests_require=['pytest'],
    entry_points={'console_scripts': ['spec2scl = spec2scl.bin:main']},
    classifiers=['Development Status :: 4 - Beta',
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
