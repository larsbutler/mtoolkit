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

import csv

EMPTY_STRING = ''

class CsvReader(object):
    """
    CsvReader allows to read csv file in
    an iterative way, building a dictionary
    for every data line inside the csv file,
    dictionary's keys correspond to the csv
    fieldnames while dictionary values are the
    corresponding fieldname/column value.
    """

    def __init__(self, filename):
        file_exists = os.path.exists(filename)
        if not file_exists:
            raise IOError('File %s not found' % filename)
        self.filename = filename
        self.check_map = {
                'eventID': self.check_positive_int,
                'Agency': self.no_check,
                'Identifier': self.check_positive_int,
                'year': self.check_year,
                'month': self.check_month,
                'day': self.check_day,
                'hour': self.check_hour,
                'minute': self.check_minute,
                'second': self.check_second,
                'timeError': self.check_time_error,
                'longitude': self.check_longitude,
                'latitude': self.check_latitude,
                'SemiMajor90': self.check_semi_major,
                'SemiMinor90': self.check_semi_minor,
                'ErrorStrike': self.check_error_strike,
                'depth': self.check_depth,
                'depthError': self.check_depth_error,
                'Mw': self.check_mw,
                'sigmaMw': self.check_positive_float,
                'Ms': self.check_float,
                'sigmaMs': self.check_positive_float,
                'mb': self.check_float,
                'sigmamb': self.check_positive_float,
                'ML': self.check_float,
                'sigmaML': self.check_positive_float
        }

    def read(self):
        """
        Return a generator that provides an EQ definition
        in a dictionary for each line of the file.
        """
        with open(self.filename, 'rb') as csv_file:
            reader = csv.reader(csv_file)
            reader.next()  # Skip the first line containing fieldnames
            for line in reader:
                valid_eq, eq_entry = self.check_line(line)
                if valid_eq:
                    yield eq_entry

    @property
    def fieldnames(self):
        """Return the fieldnames inside the csv file."""
        with open(self.filename, 'rb') as csv_file:
            reader = csv.reader(csv_file).next()
        return reader

    def check_line(self, line):
        eq_entry = {}
        correct_eq = True
        for field, value in zip(self.fieldnames, line):
            valid, converted_value = self.check_map[field](value, eq_entry)
            if not valid:
                correct_eq = False
                break
            else:
                eq_entry[field] = converted_value
        return correct_eq, eq_entry

    def check_positive_int(self, value, eq_entry):
        try:
            converted_value = int(value)
        except ValueError:
            return False, 0
        return converted_value >= 0, converted_value

    def check_year(self, value, eq_entry):
        try:
            converted_value = int(value)
        except ValueError:
            return False, 0
        return True, converted_value

    def check_month(self, value, eq_entry):
        try:
            converted_value = int(value)
        except ValueError:
            return False, 0
        return converted_value in xrange(1, 13), converted_value

    def check_day(self, value, eq_entry):
        try:
            converted_value = int(value)
        except ValueError:
            return False, 0
        if eq_entry['month'] == 2:
            valid = converted_value in xrange(1, 30)
        else:
            valid = converted_value in xrange(1, 32)
        return valid, converted_value

    def check_hour(self, value, eq_entry):
        try:
            converted_value = int(value)
        except ValueError:
            return False, 0
        return converted_value in xrange(0, 24), converted_value

    def check_minute(self, value, eq_entry):
        try:
            converted_value = int(value)
        except ValueError:
            return False, 0
        return converted_value in xrange(0, 60), converted_value

    def check_second(self, value, eq_entry):
        if not value.isspace():
            try:
                converted_value = float(value)
            except ValueError:
                return False, 0
            return converted_value in xrange(0, 60), converted_value
        else:
            return True, EMPTY_STRING

    def check_time_error(self, value, eq_entry):
        if not value.isspace():
            try:
                converted_value = float(value)
            except ValueError:
                return False, 0
            return True, converted_value
        else:
            return True, EMPTY_STRING

    def check_longitude(self, value, eq_entry):
        try:
            converted_value = float(value)
        except ValueError:
            return False, 0
        return -180 <= converted_value <= 180 , converted_value

    def check_latitude(self, value, eq_entry):
        try:
            converted_value = float(value)
        except ValueError:
            return False, 0
        return -90 <= converted_value <= 90, converted_value

    def check_semi_major(self, value, eq_entry):
        if not value.isspace():
            try:
                converted_value = float(value)
            except ValueError:
                return False, 0
            return converted_value >= 0, converted_value
        else:
            return True, EMPTY_STRING

    def check_semi_minor(self, value, eq_entry):
        if not value.isspace():
            try:
                converted_value = float(value)
            except ValueError:
                return False, 0
            return converted_value <= eq_entry['SemiMajor90'], \
                    converted_value
        else:
            return True, EMPTY_STRING

    def check_error_strike(self, value, eq_entry):
        if not value.isspace():
            try:
                converted_value = float(value)
            except ValueError:
                return False, 0
            return 0 <= converted_value <= 360, converted_value
        else:
            return True, EMPTY_STRING

    def check_depth(self, value, eq_entry):
        try:
            converted_value = float(value)
        except ValueError:
            return False, 0
        return converted_value >= 0, converted_value

    def check_depth_error(self, value, eq_entry):
        if not value.isspace():
            try:
                converted_value = float(value)
            except ValueError:
                return False, 0
            return converted_value >=0, converted_value
        else:
            return True, EMPTY_STRING

    def check_mw(self, value, eq_entry):
        try:
            converted_value = float(value)
        except ValueError:
            return False, 0
        return True, converted_value

    def check_positive_float(self, value, eq_entry):
        if not value.isspace():
            try:
                converted_value = float(value)
            except ValueError:
                return False, 0
            return converted_value >= 0, converted_value
        else:
            return True, EMPTY_STRING

    def check_float(self, value, eq_entry):
        if not value.isspace():
            try:
                converted_value = float(value)
            except ValueError:
                return False, 0
            return True, converted_value
        else:
            return True, EMPTY_STRING

    def no_check(self, value, eq_entry):
        return True, value
