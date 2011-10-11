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
The purpose of this module is to provide objects
to read EQCatalogs in different formats such as:
csv, nrml.
"""

import os
from datetime import datetime as time
import csv


class CsvReader(object):
    """
    CsvReader allows to read csv file in
    an iterative way.
    """

    def __init__(self, filename):
        file_exists = os.path.exists(filename)
        if not file_exists:
            raise IOError('File %s not found' % filename)
        self.filename = filename

    def read(self):
        """
        Return a generator that provides a list
        of field values for each line of the file.
        """
        with open(self.filename, 'rb') as csv_file:
            reader = csv.reader(csv_file)
            reader.next()  # Skip fieldnames line
            for line in reader:
                yield line

    @property
    def fieldnames(self):
        """Return the fieldnames inside the csv file."""
        with open(self.filename, 'rb') as csv_file:
            fieldnames = csv.reader(csv_file).next()
        return fieldnames

class EqEntryReader(object):

    EMPTY_STRING = ''

    def __init__(self, eq_entries_source):
        self.eq_entries_source = eq_entries_source

        self.to_int = ['eventID', 'Identifier', 'year', 'month',
                'day', 'hour', 'minute']

        self.to_float = ['second', 'timeError', 'longitude',
                'latitude','SemiMajor90', 'SemiMinor90',
                'ErrorStrike', 'depth', 'depthError',
                'Mw', 'sigmaMw', 'Ms',
                'sigmaMs',  'mb', 'sigmamb',
                'ML', 'sigmaML']

        self.compulsory_fields = self.to_int + [self.to_float[2],
                self.to_float[3], self.to_float[7], self.to_float[9]]

        self.check_map = {
                'eventID': self.check_positive_value,
                'Agency': self.no_check,
                'Identifier': self.check_positive_value,
                'year': self.check_year,
                'month': self.check_month,
                'day': self.check_day,
                'hour': self.check_hour,
                'minute': self.check_minute,
                'second': self.check_second,
                'timeError': self.no_check,
                'longitude': self.check_longitude,
                'latitude': self.check_latitude,
                'SemiMajor90': self.check_positive_value,
                'SemiMinor90': self.check_positive_value,
                'ErrorStrike': self.check_epicentre_error_location,
                'depth': self.check_positive_value,
                'depthError': self.check_positive_value,
                'Mw': self.no_check,
                'sigmaMw': self.check_positive_value,
                'Ms': self.no_check,
                'sigmaMs': self.check_positive_value,
                'mb': self.no_check,
                'sigmamb': self.check_positive_value,
                'ML': self.no_check,
                'sigmaML': self.check_positive_value
        }

    def read(self):
        csv_reader =  CsvReader(self.eq_entries_source)
        field_names = csv_reader.fieldnames
        for eq_line in csv_reader.read():
            dict_fields_values = dict(zip(field_names, eq_line))
            eq_entry = self.convert_values(dict_fields_values)
            for key, value in eq_entry.iteritems():
                eq_entry = self.check_map[key](key, value, eq_entry)
            yield eq_entry

    def convert_values(self, dict_fields_values):
        for key in dict_fields_values:
            if key in self.to_int:
                try:
                    dict_fields_values[key] = int(
                        dict_fields_values[key])
                except ValueError:
                    # fields in self.to_int are all compulsory
                    raise EqEntryValidationError(key,
                            dict_fields_values[key])

            elif key in self.to_float:

                try:
                    dict_fields_values[key] = float(
                        dict_fields_values[key])
                except ValueError:
                    if key in self.compulsory_fields:
                        raise EqEntryValidationError(key,
                            dict_fields_values[key])
                    else:
                        dict_fields_values[key] = EqEntryReader.EMPTY_STRING

        return dict_fields_values

    def no_check(self, field, value, eq_entry):
        return eq_entry

    def check_positive_value(self, field, value, eq_entry):
        if field in self.compulsory_fields:
            if value < 0:
                raise EqEntryValidationError(field, value)
        if value < 0:
            eq_entry[field] = EqEntryReader.EMPTY_STRING
        return eq_entry

    def check_year(self, field, value, eq_entry):
        if not -10000 <= value <= time.now().year:
            raise EqEntryValidationError(field, value)
        return eq_entry

    def check_month(self, field, value, eq_entry):
        if not 1 <= value <= 12:
            raise EqEntryValidationError(field, value)
        return eq_entry

    def check_day(self, field, value, eq_entry):
        if (eq_entry['month'] == 2 and value > 29)\
            or value > 31:
            raise EqEntryValidationError(field, value)
        return eq_entry

    def check_hour(self, field, value, eq_entry):
        if not 0 <= value <= 23:
            raise EqEntryValidationError(field, value)
        return eq_entry

    def check_minute(self, field, value, eq_entry):
        if not 0 <= value <= 59:
            raise EqEntryValidationError(field, value)
        return eq_entry

    def check_second(self, field, value, eq_entry):
        if not 0 <= value <= 59:
            eq_entry[field] = self.EqEntryReader.EMPTY_STRING
        return eq_entry

    def check_longitude(self, field, value, eq_entry):
        if not -180 <= value <= 180:
            raise EqEntryValidationError(field, value)
        return eq_entry

    def check_latitude(self, field, value, eq_entry):
        if not -90 <= value <= 90:
            raise EqEntryValidationError(field, value)
        return eq_entry

    def check_epicentre_error_location(self, field, value, eq_entry):
        if not 0 <= value <= 360 or \
            eq_entry['SemiMinor90'] == EqEntryReader.EMPTY_STRING or \
            eq_entry['SemiMajor90'] == EqEntryReader.EMPTY_STRING or \
            not (eq_entry['SemiMinor90'] <= eq_entry['SemiMajor90']):
                eq_entry['SemiMinor90'], eq_entry['SemiMajor90'], \
                eq_entry['ErrorStrike'] = EqEntryReader.EMPTY_STRING

        return eq_entry

class EqEntryValidationError(Exception):

    def __init__(self, field, value):
        """Constructs a new validation exception for the given eq entry field"""
        msg = 'Validation error with the field: %s, having value: %s'\
            % (field, value)
        Exception.__init__(self, msg)
        self.args = (field, msg)
