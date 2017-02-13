#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from spec2scl.version import version

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test as TestCommand
except:
    from distutils.core import setup, find_packages

if sys.version_info < (2, 7):
    install_requires = ['jinja2', 'argparse']
else:
    install_requires = ['jinja2']


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

description = """spec2scl is a tool to convert RPM specfiles to SCL-style specfiles."""

setup(
    name='spec2scl',
    version=version,
    description="Convert RPM specfiles to SCL-style.",
    long_description=description,
    keywords='rpm, spec, specfile, convert, scl, dsc',
    author='Slavek Kabrda, Robert Kuska, Iryna Shcherbina',
    author_email='slavek@redhat.com, rkuska@redhat.com, ishcherb@redhat.com',
    url='https://bitbucket.org/bkabrda/spec2scl/',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    package_data={'spec2scl': ['templates/*.spec']},
    setup_requires=['pytest',
                    'flexmock >= 0.9.3'
                    ] + install_requires,
    install_requires=install_requires,
    cmdclass={'test': PyTest},
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
