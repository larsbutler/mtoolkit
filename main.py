import sys
import os
import argparse

from mtoolkit.workflow import Context, PipeLineBuilder


def build_cmd_parser():
        parser = argparse.ArgumentParser(prog='MToolkit')
        parser.add_argument('-i', '--input-file',
                            dest='input_file',
                            nargs=1,
                            metavar='input file',
                            help="""Specify the configuration
                            file (i.e. config.yml)""")
        parser.add_argument('-v', '--version',
                            action='version',
                            version="%(prog)s 0.0.1")
        return parser


if __name__ == '__main__':
    parser = build_cmd_parser()
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        if args.input_file != None:
            if os.path.exists(args.input_file[0]):
                context = Context("config.yml")
                pipeline = PipeLineBuilder("test pipeline").build(context.config)
                pipeline.run(context)
                print context.vcl
                print context.vmain_shock
                print context.flag_vector
            else:
                print 'Error: nonexistent input file\n'
                parser.print_help()
