#!/usr/bin/env python
from __future__ import print_function, absolute_import

import argparse

import parhelion.generators
import parhelion.models
import parhelion.parsers

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', '-t', type=data_type, required=True, help='data type to read/generate')
    parser.add_argument('--files', '-f', nargs='+', default=[], help='files to parse for generating the data models')
    read_grp = parser.add_argument_group('read actions')
    read_grp.add_argument('-l', '--load', action='store_true', help='load and read the files only')
    read_grp.add_argument('-u', '--update', action='store_true', help='update existing models with new data')
    write_grp = parser.add_argument_group('write actions')
    write_grp.add_argument('-g', '--generate', type=int, help='generate data based ')
    parser.add_argument('--verbose', action='store_true', help="be extra chatty")
    parser.add_argument('--debug', action='store_true', help="run in debug mode")
    args = parser.parse_args()

    if args.debug:
        setattr(args, 'verbose', True)

    if (args.load or args.update) and not args.files:
        raise argparse.ArgumentError("You must specify --files when loading data or updating models")

    if args.type == 'xml':
        parser = parhelion.parsers.XMLParser(files=args.files)
    else:
        raise NotImplemented("{} parser not yet implemented".format(args.type))

    parser.load()



def data_type(type_str):
    allowed_types = ['json', 'xml', 'csv']
    if type_str.lower() not in allowed_types:
        raise argparse.ArgumentTypeError('{0} is not a valid data type. Allowed: {}'.format(string, ', '.join(allowed_types)))
    return type_str.lower()


###


if __name__ == '__main__':
    main()
