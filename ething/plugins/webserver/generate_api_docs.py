# coding: utf-8
import argparse
import os


def main():

    parser = argparse.ArgumentParser(
        description='Generate EThing Webserver API documentations.')

    parser.add_argument('-o', '--output-dir', type=str, metavar="OUTPUT_DIRECTORY", help='the directory where the documentations will be genearated')

    args = parser.parse_args()

    if args.output_dir is None:
        output_dir = os.getcwd()
    else:
        output_dir = args.output_dir

    if output_dir and os.path.isdir(output_dir):

        print('output directory: %s' % output_dir)

        from ething.core import Core
        from ething.plugins.webserver.server import FlaskApp
        from ething.plugins.webserver.specification import generate

        app = FlaskApp(Core())

        generate(app, specification=os.path.join(output_dir, 'openapi.json'), documentation=os.path.join(output_dir, 'http_api.md'))

    else:
        raise Exception('the directory does not exist %s' % output_dir)


if __name__ == "__main__":
    main()
