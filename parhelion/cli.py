#!/usr/bin/env python
from __future__ import print_function, absolute_import

import argparse
import json
from pprint import pprint as pp

from parhelion.models import XMLModel
from parhelion.parsers import XMLParser
from parhelion.utils import ParhelionJSONEncoder

MODELS = {
    'xml': XMLModel
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', type=data_type, required=True, help='data type to read/generate')
    parser.add_argument('-f', '--files', dest='data_files', nargs='+', default=[], help='files to parse for generating the data models')
    parser.add_argument('-m', '--model-files', nargs='+', metavar='MODEL_FILE', dest='model_files', help='model files, if updating models or generating data')
    read_grp = parser.add_argument_group('read actions')
    read_grp.add_argument('-c', '--create-models', action='store_true', help='read in the content from --files to create and write new models')
    read_grp.add_argument('-u', '--update-models', action='store_true', help='update existing models with additional data in --files')
    write_grp = parser.add_argument_group('write actions')
    write_grp.add_argument('-g', '--generate', metavar='N', type=int, help='generate N instances of the desired model data')
    write_grp.add_argument('-o', '--output-name', dest='output_name', help="basename for output files (models and generated data)")
    parser.add_argument('--verbose', action='store_true', help="be extra chatty")
    parser.add_argument('--debug', action='store_true', help="run in debug mode")
    args = parser.parse_args()

    if args.debug:
        setattr(args, 'verbose', True)

    if (args.create_models or args.update_models) and not args.data_files:
        raise argparse.ArgumentError("You must specify --files when loading data or updating models")

    if args.type == 'xml':
        parser = XMLParser(files=args.data_files)
    else:
        raise NotImplemented("{} parser not yet implemented".format(args.type))

    if args.update_models:
        for mfile in args.model_files:
            new_model = MODELS[args.type].load(mfile)
            parser.models[new_model.name] = new_model

    if args.create_models or args.update_models:
        parser.load().analyze().dump()


def data_type(type_str):
    allowed_types = ['json', 'xml', 'csv']
    if type_str.lower() not in allowed_types:
        raise argparse.ArgumentTypeError('{0} is not a valid data type. Allowed: {}'.format(string, ', '.join(allowed_types)))
    return type_str.lower()


###


if __name__ == '__main__':
    main()
