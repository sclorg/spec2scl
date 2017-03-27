========
spec2scl
========

.. image:: https://img.shields.io/pypi/v/spec2scl.svg
    :target: https://pypi.python.org/pypi/spec2scl

.. image:: https://travis-ci.org/sclorg/spec2scl.svg?branch=master
    :target: https://travis-ci.org/sclorg/spec2scl

.. image:: https://img.shields.io/github/license/sclorg/spec2scl.svg?style=flat
    :target: https://opensource.org/licenses/MIT

spec2scl is a tool to convert RPM specfiles to SCL-style specfiles.

To get more info about Software Collections, see:

- https://fedorahosted.org/SoftwareCollections/
- http://docs.fedoraproject.org/en-US/Fedora_Contributor_Documentation/1/html/Software_Collections_Guide

Usage (print this by running spec2scl -h)::


    usage: mybin.py [-h] [-i] [-r] [-b] [-k SKIP_FUNCTIONS]
                    [-n | -l SCL_CONTENTS_LIST] [--meta-specfile METAPACKAGE_NAME]
                    [-v VARIABLES]
                    [ARGUMENT [ARGUMENT ...]]

    Convert RPM specfile to be SCL ready.

    positional arguments:
      ARGUMENT              Path(s) to the specfile(s).

    optional arguments:
      -h, --help            show this help message and exit
      -i                    Convert in place (replace old specfiles with the new
                            generated ones). Mandatory when multiple specfiles are
                            to be converted.
      -r, --no-meta-runtime-dep
                            Don't add the runtime dependency on the scl runtime
                            package.
      -b, --no-meta-buildtime-dep
                            Don't add the buildtime dependency on the scl runtime
                            package.
      -k SKIP_FUNCTIONS, --skip-functions SKIP_FUNCTIONS
                            Comma separated list of transformer functions to skip.
      -n, --no-deps-convert
                            Don't convert dependency tags (mutually exclusive with
                            -l).
      -l SCL_CONTENTS_LIST, --list-file SCL_CONTENTS_LIST
                            List of the packages/provides, that will be in the SCL
                            (to convert Requires/BuildRequires properly). Lines in
                            the file are in form of "pkg-name %{?custom_prefix}",
                            where the prefix part is optional.

    metapackage arguments:
      --meta-specfile METAPACKAGE_NAME
                            Produce metapackage specfile based on the metapackage
                            name provided, see SCL docs for metapackage naming.
      -v VARIABLES, --variables VARIABLES
                            List of variables separated with comma (used only with
                            --meta-specfile option).

spec2scl is licensed under MIT license.
