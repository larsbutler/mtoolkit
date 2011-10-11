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

from mtoolkit.eqcatalog import CsvReader, EqEntryReader, \
EqEntryValidationError

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

        self.first_data_row = [
        '1', 'AAA', '20000102034913',
        '2000', '01', '02',
        '03', '49', '13',
        '0.02', '7.282', '44.368',
        '2.43', '1.01', '298',
        '9.3', '0.5', '1.71',
        '0.355', '   ', '   ',
        '   ', '   ', '1.7',
        '0.1']

    def test_an_incorrect_csv_filename_raise_exception(self):
        self.assertRaises(IOError, CsvReader, FILE_NAME_ERROR)

    def test_get_csv_fieldnames(self):
        self.assertEqual(self.fieldnames, self.csv_reader.fieldnames)

    def test_number_read_lines(self):
        expected_num_lines = 10
        read_num_lines = 0
        for _ in self.csv_reader.read():
            read_num_lines += 1
        self.assertEqual(expected_num_lines, read_num_lines)

    def test_read_line(self):
        self.assertEqual(self.first_data_row, self.csv_reader.read().next())


class EqEntryReaderTestCase(unittest.TestCase):

    def setUp(self):
        self.fieldnames = ['eventID', 'Agency', 'Identifier',
                            'year', 'month', 'day',
                            'hour', 'minute', 'second',
                            'timeError', 'longitude', 'latitude',
                            'SemiMajor90', 'SemiMinor90', 'ErrorStrike',
                            'depth', 'depthError', 'Mw',
                            'sigmaMw', 'Ms', 'sigmaMs',
                            'mb', 'sigmamb', 'ML', 'sigmaML']

        self.first_data_row = [1, 'AAA', 20000102034913,
                                2000, 01, 02,
                                03, 49, 13,
                                0.02, 7.282, 44.368,
                                2.43, 1.01, 298,
                                9.3, 0.5, 1.71,
                                0.355, '', '',
                                '', '', 1.7, 0.1]

        self.data_row_to_convert = ['2', 'AAA', '20000105132157',
                                    '2000', '01', '05',
                                    '13', '21', '57',
                                    '0.10', '11.988', '44.318',
                                    '0.77', '0.25', '315',
                                    '7.9', '0.5', '3.89',
                                    '0.199', '   ', '   ',
                                    '3.8', '0.1', '   ', '   ']

        self.eq_reader = EqEntryReader(get_data_path('ISC_small_data.csv',
                    DATA_DIR))

        self.to_int = ['eventID', 'Identifier', 'year', 'month',
                'day', 'hour', 'minute']

        self.to_float = ['second', 'timeError', 'longitude',
                'latitude', 'SemiMajor90', 'SemiMinor90',
                'ErrorStrike', 'depth', 'depthError',
                'Mw', 'sigmaMw', 'Ms',
                'sigmaMs',  'mb', 'sigmamb',
                'ML', 'sigmaML']

    def test_generated_eq_entry(self):
        first_eq_entry = dict(zip(self.fieldnames, self.first_data_row))

        self.assertEqual(first_eq_entry,
            self.eq_reader.read().next())

    def test_convert_eq_values(self):
        eq_entry_to_convert = dict(zip(self.fieldnames,
            self.data_row_to_convert))

        eq_entry_converted = {'eventID': 2, 'Agency': 'AAA',
                             'Identifier': 20000105132157, 'year': 2000,
                             'month': 1, 'day': 5,
                             'hour': 13, 'minute': 21,
                             'second': 57.0, 'timeError': 0.10,
                             'longitude': 11.988, 'latitude': 44.318,
                             'SemiMajor90': 0.77, 'SemiMinor90': 0.25,
                             'ErrorStrike': 315.0, 'depth': 7.9,
                             'depthError': 0.5, 'Mw': 3.89,
                             'sigmaMw': 0.199, 'Ms':
                                EqEntryReader.EMPTY_STRING,
                             'sigmaMs': EqEntryReader.EMPTY_STRING, 'mb': 3.8,
                             'sigmamb': 0.1, 'ML': EqEntryReader.EMPTY_STRING,
                             'sigmaML': EqEntryReader.EMPTY_STRING}

        self.assertEqual(eq_entry_converted,
                self.eq_reader.convert_values(eq_entry_to_convert))

    def test_an_incorrect_conversion_raise_exception(self):
        dict_bad_eventid_value = {'eventID': 'a'}
        dict_bad_year_value = {'year': '45os'}
        dict_bad_semimajor_value = {'SemiMajor90': '45as'}

        dict_good_event_id_value = {'eventID': '1234'}
        dict_good_year_value = {'year': '3000'}

        converted_id_value = self.eq_reader.convert_values(
            dict_good_event_id_value)['eventID']
        converted_year_value = self.eq_reader.convert_values(
            dict_good_year_value)['year']
        converted_semimajor_value = self.eq_reader.convert_values(
            dict_bad_semimajor_value)['SemiMajor90']

        self.assertRaises(EqEntryValidationError,
            self.eq_reader.convert_values, dict_bad_eventid_value)
        self.assertRaises(EqEntryValidationError,
            self.eq_reader.convert_values, dict_bad_year_value)

        self.assertEqual(converted_id_value, 1234)
        self.assertEqual(converted_year_value, 3000)
        # A non compulsory value when invalid is replaced by an empty string
        self.assertEqual(converted_semimajor_value, EqEntryReader.EMPTY_STRING)

    def test_check_positive_value(self):
        eq_entry = {}
        compulsory_field_name = 'depth'
        non_compulsory_field_name = 'sigmaMs'
        compulsory_field_value = -5
        non_compulsory_field_value = -2
        checked_eq_entry = self.eq_reader.check_positive_value(
        non_compulsory_field_name, non_compulsory_field_value, eq_entry)

        self.assertRaises(EqEntryValidationError,
            self.eq_reader.check_positive_value, compulsory_field_name,
            compulsory_field_value, eq_entry)
        self.assertEqual(EqEntryReader.EMPTY_STRING, checked_eq_entry['sigmaMs'])


