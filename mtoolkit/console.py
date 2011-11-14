# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright (c) 2010-2011, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# only, as published by the Free Software Foundation.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License version 3 for more details
# (a copy is included in the LICENSE file that accompanied this code).
#
# You should have received a copy of the GNU Lesser General Public License
# version 3 along with OpenQuake. If not, see
# <http://www.gnu.org/licenses/lgpl-3.0.txt> for a copy of the LGPLv3 License.

"""
A set of utility functions for cmdline
"""

import os
import sys
import argparse


class LogAction(argparse.Action):
    """
    Custom action defined for the log cmdline option
    which receives no args
    """
    def __call__(self, parser, namespace, values, option_string=None):
        namespace.log = True


def build_cmd_parser():
    """
    Create a simple parser for cmdline
    """

    parser = argparse.ArgumentParser(prog='MToolkit')
    parser.add_argument('-i', '--input-file',
                        dest='input_file',
                        nargs=1,
                        metavar='input file',
                        help="""Specify the configuration
                        file (i.e. config.yml)""")

    parser.add_argument('-l', '--log',
                        metavar='',
                        action=LogAction,
                        nargs=0,
                        help="-l, --log: activate logging info")

    parser.add_argument('-v', '--version',
                        action='version',
                        version="%(prog)s 0.0.1")
    return parser


def cmd_line():
    """
    Return cmdline input argument
    after checking the proper input
    has been given.
    """

    parser = build_cmd_parser()
    input_filename = None
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        if os.path.exists(args.input_file[0]):
            input_filename = args.input_file[0]
        else:
            print 'Error: non existent input file\n'
            parser.print_help()

    return input_filename, args.log
