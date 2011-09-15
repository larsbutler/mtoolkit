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

""" Unit Tests for the eqcatalog module """

import os
import unittest
from mtoolkit.eqcatalog import CsvParser

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))


def get_data_path(file_name):
    """ Returns the data path of files used in test """
    return os.path.join(DATA_DIR, file_name)


class CsvParserTestCase(unittest.TestCase):
    """
    Unit tests for the CsvParser class, which parses
    csv files
    """

    def setUp(self):
        self.incorrect_filename = 'data/example.csv'
        self.correct_filename = get_data_path('ISC_small_data.csv')
        self.csv_parser = CsvParser(self.correct_filename)
        self.fieldnames = ['eventID', 'Agency', 'Identifier',
                            'year', 'month', 'day',
                            'hour', 'minute', 'second',
                            'timeError', 'longitude', 'latitude',
                            'SemiMajor90', 'SemiMinor90', 'ErrorStrike',
                            'depth', 'depthError', 'Mw',
                            'sigmaMw', 'Ms', 'sigmaMs',
                            'mb', 'sigmamb', 'ML',
                            'sigmaML']

    def test_an_incorrect_csv_filename_raise_exception(self):
        self.assertRaises(IOError, CsvParser, self.incorrect_filename)

    def test_get_csv_fieldnames(self):
        self.assertEqual(self.fieldnames, self.csv_parser.fieldnames)

    def test_number_data_rows_equals_number_genereted_dict(self):
        number_data_rows = -1  # First line with fieldnames
        with open(self.correct_filename) as csv_file:
            for line in csv_file:
                number_data_rows = number_data_rows + 1
        number_generated_dict = 0
        for data_dict in self.csv_parser.parse():
            number_generated_dict = number_generated_dict + 1
        self.assertEqual(number_data_rows, number_generated_dict)

    def test_parse_line(self):
        with open(self.correct_filename) as csvfile:
            csvfile.readline()  # Skip first line with fieldnames
            first_data_row = csvfile.readline().strip('\r\n').split(',')
            second_data_row = csvfile.readline().strip('\r\n').split(',')
            third_data_row = csvfile.readline().strip('\r\n').split(',')

        first_dict = dict(zip(self.fieldnames, first_data_row))
        second_dict = dict(zip(self.fieldnames, second_data_row))
        third_dict = dict(zip(self.fieldnames, third_data_row))
        gen_dict = self.csv_parser.parse()
        parsed_first_dict = gen_dict.next()
        parsed_second_dict = gen_dict.next()
        parsed_third_dict = gen_dict.next()
        self.assertEqual(first_dict, parsed_first_dict)
        self.assertEqual(second_dict, parsed_second_dict)
        self.assertEqual(third_dict, parsed_third_dict)
