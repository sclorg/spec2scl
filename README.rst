========
spec2scl
========

spec2scl is a tool to convert RPM specfiles to SCL-style specfiles.

To get more info about Software Collections, see:

- https://fedorahosted.org/SoftwareCollections/
- http://docs.fedoraproject.org/en-US/Fedora_Contributor_Documentation/1/html/Software_Collections_Guide

Usage (print this by running spec2scl -h)::


    usage: spec2scl [-h] [--meta-specfile] [-i] [-r] [-b] [-k SKIP_FUNCTIONS]
                    [-v VARIABLES] [-n | -l SCL_CONTENTS_LIST]
                    [ARGUMENT [ARGUMENT ...]]

    Convert RPM specfile to be SCL ready.

    positional arguments:
      ARGUMENT              Paths to the specfiles or name of the meta package,
                            see --meta-specfile.

    optional arguments:
      -h, --help            show this help message and exit
      --meta-specfile       If used, spec2scl will produce metapackage specfile
                            based on ARGUMENT, ARGUMENT must be the metapackage
                            name, see SCL docs for metapackage naming.
      -i                    Convert in place (replaces old specfiles with the new
                            generated ones). Mandatory when multiple specfiles are
                            to be converted.
      -r, --no-meta-runtime-dep
                            Don't add the runtime dependency on the scl runtime
                            package.
      -b, --no-meta-buildtime-dep
                            Don't add the buildtime dependency on the scl runtime
                            package.
      -k SKIP_FUNCTIONS, --skip-functions SKIP_FUNCTIONS
                            Comma separated list of transformer functions to skip
      -v VARIABLES, --variables VARIABLES
                            List of variables separated with comma, used only with
                            --meta-specfile option
      -n, --no-deps-convert
                            Don't convert dependency tags (mutually exclusive with
                            -l).
      -l SCL_CONTENTS_LIST, --list-file SCL_CONTENTS_LIST
                            List of the packages/provides, that will be in the SCL
                            (to convert Requires/BuildRequires properly). Lines in
                            the file are in form of "pkg-name %{?custom_prefix}",
                            where the prefix part is optional.



spec2scl is licensed under MIT license.
