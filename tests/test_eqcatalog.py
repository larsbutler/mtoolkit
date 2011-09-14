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
        self.csv_parser = CsvParser()
        self.incorrect_filename = 'data/example.csv'
        self.correct_filename = get_data_path('ISC_small_data.csv')
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
        self.failUnlessRaises(IOError, self.csv_parser.parse,
                                    self.incorrect_filename)

    def test_a_correct_csv_filename_raise_no_exception(self):
        self.csv_parser.parse(self.correct_filename)

    def test_get_csv_fieldnames(self):
        self.csv_parser.parse(self.correct_filename)
        self.assertEqual(self.fieldnames, self.csv_parser.fieldnames)
