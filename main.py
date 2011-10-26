import sys
import os
import argparse

from mtoolkit.workflow import Context, PipeLineBuilder


def build_cmd_parser():
    """Create a simple parser for cmdline"""

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
    PARSER = build_cmd_parser()
    if len(sys.argv) == 1:
        PARSER.print_help()
    else:
        ARGS = PARSER.parse_args()
        if ARGS.input_file != None:
            if os.path.exists(ARGS.input_file[0]):
                CONTEXT = Context("config.yml")
                PIPELINE = PipeLineBuilder("test pipeline").build(
                            CONTEXT.config)
                PIPELINE.run(CONTEXT)
                print CONTEXT.vcl
                print CONTEXT.vmain_shock
                print CONTEXT.flag_vector
            else:
                print 'Error: non existent input file\n'
                PARSER.print_help()
