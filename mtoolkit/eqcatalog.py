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

""" Provide a way to parse csv files """

import os
import csv


class CsvParser(object):
    """
    CsvParser allows to parse csv file in
    an iterative way
    """

    def __init__(self):
        self.filename = None
        self.fieldnames = []

    def parse(self, filename):
        """ Parse the csv file specified by its filename """
        self.filename = filename
        file_exists = os.path.exists(filename)
        if not file_exists:
            raise IOError('File not found')
        self.fieldnames = self._get_fieldnames()

    def _get_fieldnames(self):
        """ Get the fieldnames inside the csv file """
        with open(self.filename, 'rb') as csv_file:
            reader = csv.DictReader(csv_file)
            self.fieldnames = reader.fieldnames
        return self.fieldnames
