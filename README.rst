=======
rpm2scl
=======

rpm2scl is a tool to convert RPM specfiles to SCL-style specfiles.

Usage (print this by running rpm2scl -h)::

   usage: rpm2scl [-h] [-i] SPECFILE_PATH [SPECFILE_PATH ...]

   Convert RPM specfile to be SCL ready.

   positional arguments:
     SPECFILE_PATH  Paths to the specfiles.

     optional arguments:
       -h, --help     show this help message and exit
       -i             Convert in place (replaces old specfiles with the new
                      generated ones). Mandatory when multiple specfiles are to be
                      converted.

rpm2scl is licensed under MIT license.
