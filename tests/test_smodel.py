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

from mtoolkit import xml_utils
from mtoolkit.smodel import SourceModelReader

from tests.test_utils import get_data_path, DATA_DIR, \
    SCHEMA_DIR, FILE_NAME_ERROR


class SourceModelReaderTestCase(unittest.TestCase):

    def setUp(self):
        self.correct_filename = get_data_path(
            'example_areaSource.xml', DATA_DIR)
        self.incorrect_nrml = get_data_path(
            'incorrect_areaSource.xml', DATA_DIR)
        self.schema = get_data_path('nrml.xsd', SCHEMA_DIR)
        self.sm_reader = SourceModelReader(self.correct_filename, self.schema)
        self.gen_as = self.sm_reader.read().next()

    def test_incorrect_sm_filename_raise_exception(self):
        self.assertRaises(IOError, SourceModelReader, FILE_NAME_ERROR,
                            self.schema)

    def test_incorrect_sm_document_raise_exception(self):
        self.assertRaises(xml_utils.XMLValidationError, SourceModelReader,
            self.incorrect_nrml, self.schema)

    def test_number_as_entries_equals_number_gen_entries(self):
        expected_entries = 2
        read_as_entries = 0
        for _ in self.sm_reader.read():
            read_as_entries += 1
        self.assertEqual(expected_entries, read_as_entries)

    def test_as_simple_attrib(self):
        """
        tests if the area source simple
        attributes are equal to the read
        ones
        """

        sm_id = 'sm1'
        type_sm = 'area_source'
        as_id = 'src_1'
        as_name = 'Source 8.CH.3'
        as_tectonic_region = 'Active Shallow Crust'
        as_hypocentral_depth = 15.0

        self.assertEqual(sm_id, self.gen_as.get('id_sm'))
        self.assertEqual(type_sm, self.gen_as.get('type'))
        self.assertEqual(as_id, self.gen_as.get('id_as'))
        self.assertEqual(as_name, self.gen_as.get('name'))
        self.assertEqual(as_tectonic_region,
                self.gen_as.get('tectonic_region'))
        self.assertEqual(as_hypocentral_depth,
                self.gen_as.get('hypocentral_depth'))

    def test_as_area_boundary(self):
        pos_list = [(132.93, 42.85), (134.86, 41.82),
                (129.73, 38.38), (128.15, 40.35)]
        area_boundary = self.gen_as.get('area_boundary')

        self.assertEquals(pos_list,
                area_boundary.get('area_boundary_pos_list'))

    def test_as_rrm_truncated_gutenberg_richter(self):
        rrm_tgr = self.gen_as.get('rupture_rate_model')[0]
        name = 'truncated_guten_richter'
        a_value_cumulative = 3.1612436654341836
        b_value = 0.7318999871612379
        min_magnitude = 5.0
        max_magnitude = 8.0

        self.assertEqual(name, rrm_tgr.get('name'))
        self.assertEqual(a_value_cumulative, rrm_tgr.get('a_value_cumulative'))
        self.assertEqual(b_value, rrm_tgr.get('b_value'))
        self.assertEqual(min_magnitude, rrm_tgr.get('min_magnitude'))
        self.assertEqual(max_magnitude, rrm_tgr.get('max_magnitude'))

    def test_as_rrm_focal_mechanism(self):
        rrm_fm = self.gen_as.get('rupture_rate_model')[1]
        fm_id = 'smi:fm1/0'
        name = 'focal_mechanism'
        number_nodal_planes = 2
        second_nodal_plane = {'id': 1, 'strike': 12.0,
                'rake': 0.0, 'dip': 40.0}

        self.assertEqual(fm_id, rrm_fm.get('id'))
        self.assertEqual(name, rrm_fm.get('name'))
        self.assertEqual(second_nodal_plane,
                rrm_fm.get('nodal_planes')[1])
        self.assertEquals(number_nodal_planes,
                len(rrm_fm.get('nodal_planes')))

    def test_rupture_depth_distribution(self):
        rdd = self.gen_as.get('rupture_depth_distribution')
        name = 'rupture_depth_distrib'
        depth = 15.0
        magnitude = 5.0

        self.assertEqual(name, rdd.get('name'))
        self.assertEqual(depth, rdd.get('depth'))
        self.assertEqual(magnitude, rdd.get('magnitude'))
