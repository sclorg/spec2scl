========
spec2scl
========

spec2scl is a tool to convert RPM specfiles to SCL-style specfiles.

To get more info about Software Collections, see:

- https://fedorahosted.org/SoftwareCollections/
- http://docs.fedoraproject.org/en-US/Fedora_Contributor_Documentation/1/html/Software_Collections_Guide

Usage (print this by running spec2scl -h)::

   usage: spec2scl [-h] [-i] [-r CONVERT_REQUIRES] [-l SCL_CONTENTS_LIST] [-m]
                   SPECFILE_PATH [SPECFILE_PATH ...]

   Convert RPM specfile to be SCL ready.

   positional arguments:
     SPECFILE_PATH         Paths to the specfiles.

   optional arguments:
     -h, --help            show this help message and exit
     -i                    Convert in place (replaces old specfiles with the new
                           generated ones). Mandatory when multiple specfiles are
                           to be converted.
     -r CONVERT_REQUIRES, --requires CONVERT_REQUIRES
                           Convert a(ll)/n(one)/f(rom file) Requires and
                           BuildRequires to scl. Defaults to all. If all or none
                           is selected, this will negate effect of -l.
     -l SCL_CONTENTS_LIST, --list-file SCL_CONTENTS_LIST
                           List of the packages/provides, that will be in the SCL
                           (to convert Requires/BuildRequires properly).
     -m, --meta-runtime-dep
                           If used, runtime dependency on the scl runtime package
                           will be added. The dependency is not added by default.

spec2scl is licensed under MIT license.
