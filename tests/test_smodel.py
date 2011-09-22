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

from mtoolkit import xml_utils
from mtoolkit.smodel import SourceModelReader
from tests.test_utils import get_data_path, DATA_DIR,\
    SCHEMA_DIR, FILE_NAME_ERROR
import unittest


class SourceModelReaderTestCase(unittest.TestCase):

    def setUp(self):
        self.correct_filename = get_data_path(
            'example_areaSource.xml', DATA_DIR)
        self.incorrect_nrml = get_data_path(
            'incorrect_areaSource.xml', DATA_DIR)
        self.schema = get_data_path('nrml.xsd', SCHEMA_DIR)
        self.sm_reader = SourceModelReader(self.correct_filename, self.schema)

    def test_incorrect_sm_filename_raise_exception(self):
        self.assertRaises(IOError, SourceModelReader, FILE_NAME_ERROR,
                            self.schema)

    def test_incorrect_sm_document_raise_exception(self):
        self.assertRaises(xml_utils.XMLValidationError, SourceModelReader,
            self.incorrect_nrml, self.schema)

    @unittest.skip
    def test_number_as_entries_equals_number_gen_entries(self):
        expected_entries = 2
        read_as_entries = 0
        for _ in self.sm_reader.read():
            read_as_entries += 1
        self.assertEqual(expected_entries, read_as_entries)

    @unittest.skip
    def test_area_source_entry_equal_gen_entry(self):
        pass
