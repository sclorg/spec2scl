import argparse
import os
import sys

from rpm2scl.convertor import Convertor

def main():
    parser = argparse.ArgumentParser(description = 'Convert RPM specfile to be SCL ready.')
    parser.add_argument('specfiles',
                        help = 'Paths to the specfiles.',
                        metavar = 'SPECFILE_PATH',
                        nargs = '+',
                       )
    parser.add_argument('-i',
                        help = 'Convert in place (replaces old specfiles with the new generated ones). Mandatory when multiple specfiles are to be converted.',
                        required = False,
                        action = 'store_true'
                       )
    parser.add_argument('-l', '--list-file',
                        required = False,
                        help = 'List of the packages/provides, that will be in the SCL (to convert Requires/BuildRequires properly).',
                        metavar = 'SCL_CONTENTS_LIST'
                       )

    args = parser.parse_args()

    if len(args.specfiles) > 1 and not args.i:
        parser.error('You can only convert more specfiles using -i (in place) mode.')

    scl_list = []

    if args.list_file:
        try:
            with open(args.list_file) as l:
                for i in l.readlines():
                    scl_list.append(i.strip())
        except IOError as e:
            print('Could not open file: {0}'.format(e))
            sys.exit(1)

    converted = []
    for specfile in args.specfiles:
        try:
            with open(specfile) as f:
                spec = f.readlines()
        except IOError as e:
            print('Could not open file: {0}'.format(e))
            sys.exit(1)

        convertor = Convertor(spec = spec, options = {'scl_list': scl_list})
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


main()
