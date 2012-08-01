========
spec2scl
========

spec2scl is a tool to convert RPM specfiles to SCL-style specfiles.

Usage (print this by running spec2scl -h)::

   usage: spec2scl [-h] [-i] [-l SCL_CONTENTS_LIST]
                  SPECFILE_PATH [SPECFILE_PATH ...]

   Convert RPM specfile to be SCL ready.

   positional arguments:
     SPECFILE_PATH         Paths to the specfiles.

   optional arguments:
     -h, --help            show this help message and exit
     -i                    Convert in place (replaces old specfiles with the new
                           generated ones). Mandatory when multiple specfiles are
                           to be converted.
     -l SCL_CONTENTS_LIST, --list-file SCL_CONTENTS_LIST
                           List of the packages/provides, that will be in the SCL
                           (to convert Requires/BuildRequires properly).

spec2scl is licensed under MIT license.
