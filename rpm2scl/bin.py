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

    args = parser.parse_args()

    if len(args.specfiles) > 1 and not args.i:
        parser.error('You can only convert more specfiles using -i (in place) mode.')

    converted = []
    for specfile in args.specfiles:
        try:
            f = open(specfile)
            spec = f.readlines()
        except IOError as e:
            print('Could not open file: {0}'.format(e))
            sys.exit(1)
        else:
            f.close()

        convertor = Convertor(spec = spec)
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
