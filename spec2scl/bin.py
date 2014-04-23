import argparse
import sys

from spec2scl.convertor import Convertor


def handle_scl_deps(no_deps_convert, args_list_file):
    scl_deps = True
    if no_deps_convert:
        scl_deps = False
    elif args_list_file:
        scl_deps = []
        with open(args_list_file) as l:
            for i in l.readlines():
                scl_deps.append(i.strip())

    return scl_deps


def main():
    parser = argparse.ArgumentParser(description='Convert RPM specfile to be SCL ready.')
    parser.add_argument('specfiles',
                        help='Paths to the specfiles or name of the meta package, see --meta-specfile.',
                        metavar='ARGUMENT',
                        nargs='*',
                        )
    parser.add_argument('--meta-specfile',
                        required=False,
                        action='store_true',
                        help='If used, spec2scl will produce metapackage specfile based on ARGUMENT, ARGUMENT must be the metapackage name, see SCL docs for metapackage naming.',
                        )
    parser.add_argument('-i',
                        help='Convert in place (replaces old specfiles with the new generated ones). Mandatory when multiple specfiles are to be converted.',
                        required=False,
                        action='store_true'
                        )
    parser.add_argument('-m', '--meta-runtime-dep',
                        required=False,
                        help='If used, runtime dependency on the scl runtime package will be added. The dependency is not added by default.',
                        action='store_true'
                        )
    parser.add_argument('-k', '--skip-functions',
                        required=False,
                        default="",
                        help='Comma separated list of transformer functions to skip',
                        )
    parser.add_argument('-v', '--variables',
                        required=False,
                        default="",
                        help='List of variables separated with comma, used only with --meta-specfile option',
                        )

    grp = parser.add_mutually_exclusive_group(required=False)
    grp.add_argument('-n', '--no-deps-convert',
                     required=False,
                     help='Don\'t convert dependency tags (mutually exclusive with -l).',
                     action='store_true',
                     )
    grp.add_argument('-l', '--list-file',
                     required=False,
                     help='List of the packages/provides, that will be in the SCL (to convert Requires/BuildRequires properly).',
                     metavar='SCL_CONTENTS_LIST'
                     )

    args = parser.parse_args()

    if len(args.specfiles) > 1 and not args.i:
        parser.error('You can only convert more specfiles using -i (in place) mode.')

    if len(args.specfiles) == 0 and sys.stdin.isatty():
        parser.error('You must either specify specfile(s) or reading from stdin.')

    if len(args.specfiles) > 0 and not sys.stdin.isatty():
        parser.error(
            'You must either specify specfile(s) or reading from stdin, not both.')

    try:
        scl_deps = handle_scl_deps(args.no_deps_convert, args.list_file)
    except IOError as e:
        print('Could not open file: {0}'.format(e))
        sys.exit(1)

    specs = []
    converted = []
    if args.meta_specfile:
        specs.append(args.specfiles)
    else:
        for specfile in args.specfiles:
            try:
                with open(specfile) as f:
                    specs.append(f.readlines())
            except IOError as e:
                print('Could not open file: {0}'.format(e))
                sys.exit(1)

    if not sys.stdin.isatty():
        specs.append(sys.stdin.readlines())

    for spec in specs:
        options = {'scl_deps': scl_deps,
                   'meta_runtime_dep': args.meta_runtime_dep,
                   'skip_functions': args.skip_functions.split(','),
                   'variables': args.variables,
                   'meta_spec': args.meta_specfile}

        convertor = Convertor(spec=spec, options=options)
        converted.append(convertor.convert())

    for i, conv in enumerate(converted):
        if not args.i:
            print(conv)
        else:
            try:
                f = open(args.specfiles[i], 'w')
                f.write(str(conv))
            except IOError as e:
                print('Could not open file: {0}'.format(e))
            else:
                f.close()
