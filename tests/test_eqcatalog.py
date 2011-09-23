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

import unittest

from mtoolkit.eqcatalog import CsvReader

from tests.test_utils import get_data_path, DATA_DIR, FILE_NAME_ERROR


class CsvReaderTestCase(unittest.TestCase):

    def setUp(self):
        self.correct_filename = get_data_path('ISC_small_data.csv', DATA_DIR)
        self.csv_reader = CsvReader(self.correct_filename)
        self.fieldnames = ['eventID', 'Agency', 'Identifier',
                            'year', 'month', 'day',
                            'hour', 'minute', 'second',
                            'timeError', 'longitude', 'latitude',
                            'SemiMajor90', 'SemiMinor90', 'ErrorStrike',
                            'depth', 'depthError', 'Mw',
                            'sigmaMw', 'Ms', 'sigmaMs',
                            'mb', 'sigmamb', 'ML',
                            'sigmaML']
        with open(self.correct_filename) as csvfile:
            csvfile.readline()  # Skip first line with fieldnames
            first_data_row = csvfile.readline().strip('\r\n').split(',')
            second_data_row = csvfile.readline().strip('\r\n').split(',')
            third_data_row = csvfile.readline().strip('\r\n').split(',')
        self.eq_entry_1 = dict(zip(self.fieldnames, first_data_row))
        self.eq_entry_2 = dict(zip(self.fieldnames, second_data_row))
        self.eq_entry_3 = dict(zip(self.fieldnames, third_data_row))

    def test_an_incorrect_csv_filename_raise_exception(self):
        self.assertRaises(IOError, CsvReader, FILE_NAME_ERROR)

    def test_get_csv_fieldnames(self):
        self.assertEqual(self.fieldnames, self.csv_reader.fieldnames)

    def test_number_data_rows_equals_number_gen_entries(self):
        expected_entries = 10
        read_eq_entries = 0
        for _ in self.csv_reader.read():
            read_eq_entries += 1
        self.assertEqual(expected_entries, read_eq_entries)

    def test_read_entries(self):
        """
        Test if the EQ definitions built by CsvReader
        contain proper values.
        """
        eqcatalog = self.csv_reader.read()
        self.assertEqual(self.eq_entry_1, eqcatalog.next())
        self.assertEqual(self.eq_entry_2, eqcatalog.next())
        self.assertEqual(self.eq_entry_3, eqcatalog.next())
