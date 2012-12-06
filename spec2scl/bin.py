import argparse
import os
import sys

from spec2scl.convertor import Convertor

def handle_scl_requires(args_requires, args_list_file):
    scl_requires = None
    if args_requires != 'f':
        scl_requires = args_requires
    else:
        scl_requires = []
        with open(args_list_file) as l:
            for i in l.readlines():
                scl_requires.append(i.strip())

    return scl_requires

def main():
    parser = argparse.ArgumentParser(description = 'Convert RPM specfile to be SCL ready.')
    parser.add_argument('specfiles',
                        help = 'Paths to the specfiles.',
                        metavar = 'SPECFILE_PATH',
                        nargs = '*',
                       )
    parser.add_argument('-i',
                        help = 'Convert in place (replaces old specfiles with the new generated ones). Mandatory when multiple specfiles are to be converted.',
                        required = False,
                        action = 'store_true'
                       )
    parser.add_argument('-r', '--requires',
                        required = False,
                        help = 'Convert a(ll)/n(one)/f(rom file) Requires and BuildRequires to scl. Defaults to all. If all or none is selected, this will negate effect of -l.',
                        default = 'a',
                        choices = 'anf',
                        metavar = 'CONVERT_REQUIRES'
                       )
    parser.add_argument('-l', '--list-file',
                        required = False,
                        help = 'List of the packages/provides, that will be in the SCL (to convert Requires/BuildRequires properly).',
                        metavar = 'SCL_CONTENTS_LIST'
                       )
    parser.add_argument('-m', '--meta-runtime-dep',
                        required = False,
                        help = 'If used, runtime dependency on the scl runtime package will be added. The dependency is not added by default.',
                        action = 'store_true'
                       )
    parser.add_argument('-s', '--stdin',
                        required = False,
                        help = 'Read specfile from stdin',
                        action = 'store_true'
                       )

    args = parser.parse_args()

    if len(args.specfiles) > 1 and not args.i:
        parser.error('You can only convert more specfiles using -i (in place) mode.')

    if len(args.specfiles) == 0 and not args.stdin:
        parser.error('You must either specify specfile(s) or reading from stdin.')

    if len(args.specfiles) > 0 and args.stdin:
        parser.error('You must either specify specfile(s) or reading from stdin, not both.')

    if args.requires == 'f' and not args.list_file:
        parser.error('You must specify the file with provides list if you want to use "-r f".')

    try:
        scl_requires = handle_scl_requires(args.requires, args.list_file)
    except IOError as e:
        print('Could not open file: {0}'.format(e))
        sys.exit(1)

    specs = []
    converted = []
    for specfile in args.specfiles:
        try:
            with open(specfile) as f:
                specs.append(f.readlines())
        except IOError as e:
            print('Could not open file: {0}'.format(e))
            sys.exit(1)

    if args.stdin:
        specs.append(sys.stdin.readlines())

    for spec in specs:
        convertor = Convertor(spec = spec, options = {'scl_requires': scl_requires, 'meta_runtime_dep': args.meta_runtime_dep})
        converted.append(convertor.convert())

    for i, conv in enumerate(converted):
        if not args.i:
            print(conv)
        else:
            try:
                f = open(args.specfiles[i], 'w')
                f.write(conv)
            except IOError as e:
                print('Could not open file: {0}'.format(e))
            else:
                f.close()
