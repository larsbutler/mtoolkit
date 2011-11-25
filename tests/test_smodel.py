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

from mtoolkit import utils
from mtoolkit.smodel import NRMLReader
from mtoolkit.utils import get_data_path, DATA_DIR, \
    SCHEMA_DIR, FILE_NAME_ERROR


class NRMLReaderTestCase(unittest.TestCase):

    def setUp(self):
        self.area_source_nrml = get_data_path(
            'area_source_model.xml', DATA_DIR)
        self.simple_fault_nrml = get_data_path(
            'simple_fault_source_model.xml', DATA_DIR)
        self.complex_fault_nrml = get_data_path(
            'complex_source_model.xml', DATA_DIR)
        self.simple_point_nrml = get_data_path(
            'simple_point_source_model.xml', DATA_DIR)
        self.incorrect_nrml = get_data_path(
            'incorrect_area_source_model.xml', DATA_DIR)
        self.schema = get_data_path('nrml.xsd', SCHEMA_DIR)

        self.area_source_reader = NRMLReader(self.area_source_nrml,
                self.schema)
        self.simple_fault_reader = NRMLReader(self.simple_fault_nrml,
                self.schema)
        self.complex_fault_reader = NRMLReader(self.complex_fault_nrml,
                self.schema)
        self.simple_point_reader = NRMLReader(self.simple_point_nrml,
                self.schema)

        self.gen_as = self.area_source_reader.read().next()
        self.gen_sf = self.simple_fault_reader.read().next()
        self.gen_cf = self.complex_fault_reader.read().next()
        self.gen_sp = self.simple_point_reader.read().next()

    def test_incorrect_sm_filename_raise_exception(self):
        self.assertRaises(IOError, NRMLReader, FILE_NAME_ERROR,
                            self.schema)

    def test_incorrect_sm_document_raise_exception(self):
        self.assertRaises(utils.XMLValidationError, NRMLReader,
            self.incorrect_nrml, self.schema)

    def test_number_as_entries_equals_number_gen_entries(self):
        expected_entries = 2
        read_as_entries = 0
        for _ in self.area_source_reader.read():
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
        as_pos_list = [132.93, 42.85, 134.86, 41.82,
                129.73, 38.38, 128.15, 40.35]
        as_hypocentral_depth = 15.0

        self.assertEqual(sm_id, self.gen_as.get('id_sm'))
        self.assertEqual(type_sm, self.gen_as.get('type'))
        self.assertEqual(as_id, self.gen_as.get('id_as'))
        self.assertEqual(as_name, self.gen_as.get('name'))
        self.assertEqual(as_tectonic_region,
                self.gen_as.get('tectonic_region'))
        self.assertEquals(as_pos_list, self.gen_as.get('area_boundary'))
        self.assertEqual(as_hypocentral_depth,
                self.gen_as.get('hypocentral_depth'))

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
        depth = [15.0]
        magnitude = [5.0]

        self.assertEqual(name, rdd.get('name'))
        self.assertEqual(depth, rdd.get('depth'))
        self.assertEqual(magnitude, rdd.get('magnitude'))

    def test_sf_simple_attrib(self):
        sm_id = 'sm1'
        type_sm = 'simple_fault'
        sf_id = 'ALCS001'
        sf_name = 'Southern Albania offshore'
        sf_tectonic_region = 'Active Shallow Crust'
        sf_rake = 90.0

        self.assertEqual(sm_id, self.gen_sf.get('id_sm'))
        self.assertEqual(type_sm, self.gen_sf.get('type'))
        self.assertEqual(sf_id, self.gen_sf.get('id_sf'))
        self.assertEqual(sf_name, self.gen_sf.get('name'))
        self.assertEqual(sf_tectonic_region,
                self.gen_sf.get('tectonic_region'))
        self.assertEqual(sf_rake, self.gen_sf.get('rake'))

    def test_sf_truncated_gutenberg_richter(self):
        tgr = self.gen_sf.get('truncated_guten_richter')
        name = 'truncated_guten_richter'
        a_value_cumulative = 3.6786313049897035
        b_value = 1.0
        min_magnitude = 5.0
        max_magnitude = 7.0

        self.assertEqual(name, tgr.get('name'))
        self.assertEqual(a_value_cumulative, tgr.get('a_value_cumulative'))
        self.assertEqual(b_value, tgr.get('b_value'))
        self.assertEqual(min_magnitude, tgr.get('min_magnitude'))
        self.assertEqual(max_magnitude, tgr.get('max_magnitude'))

    def test_sf_geometry(self):
        geo = self.gen_sf.get('geometry')
        name = 'geometry'
        geo_id = 'sfg_0'
        pos_list = [19.5417, 40.0925, 1.0, 19.4654, 40.1496, 1.0, 19.3891,
                    40.2067, 1.0, 19.297200000000004, 40.2833, 1.0,
                    19.2052, 40.3599, 1.0, 19.1299, 40.4443, 1.0,
                    19.0545, 40.5286, 1.0, 18.9921, 40.629, 1.0,
                    18.9296, 40.7293, 1.0, 18.884, 40.8269, 1.0,
                    18.8385, 40.9245, 1.0, 18.8033, 41.0104, 1.0,
                    18.7681, 41.09620000000001, 1.0]
        dip = 37.5
        upper_seismogenic_depth = 1.0
        lower_seismogenic_depth = 12.0

        self.assertEqual(name, geo.get('name'))
        self.assertEqual(geo_id, geo.get('id_geo'))
        self.assertEqual(pos_list, geo.get('fault_trace_pos_list'))
        self.assertEqual(dip, geo.get('dip'))
        self.assertEqual(upper_seismogenic_depth, geo.get(
                'upper_seismogenic_depth'))
        self.assertEqual(lower_seismogenic_depth, geo.get(
                'lower_seismogenic_depth'))

    def test_cf_simple_attrib(self):
        sm_id = 'sm1'
        type_sm = 'complex_fault'
        cf_id = 'src_cascadia.mid.8387z.in'
        cf_name = 'Cascadia Megathrust'
        cf_tectonic_region = 'Subduction Interface'
        cf_rake = 90.0

        self.assertEqual(sm_id, self.gen_cf.get('id_sm'))
        self.assertEqual(type_sm, self.gen_cf.get('type'))
        self.assertEqual(cf_id, self.gen_cf.get('id_cf'))
        self.assertEqual(cf_name, self.gen_cf.get('name'))
        self.assertEqual(cf_tectonic_region,
                self.gen_cf.get('tectonic_region'))
        self.assertEqual(cf_rake, self.gen_cf.get('rake'))

    def test_cf_evenly_discretized_inc_mfd(self):
        edi = self.gen_cf.get('evenly_discretized_inc_MFD')
        cf_name = 'evenly_discretized_inc_MFD'
        cf_bin_size = 0.1
        cf_min_val = 8.3
        cf_edi_values = [8.056204131504448e-05,
            6.828805796045152e-05, 5.788407026299047e-05,
            4.906517611250961e-05]

        self.assertEqual(cf_name, edi.get('name'))
        self.assertEqual(cf_bin_size, edi.get('bin_size'))
        self.assertEqual(cf_min_val, edi.get('min_val'))
        self.assertEqual(cf_edi_values, edi.get('values'))

    def test_cf_geometry(self):
        geo = self.gen_cf.get('geometry')
        fault_top_edge = [-124.704, 40.363, 5.49326,
                            -124.977, 41.214000000000006,
                            4.98856, -125.14, 42.096,
                            4.89734, -125.21899999999998,
                            42.965, 4.84761, -125.25700000000002,
                            43.852, 4.87128, -125.313, 44.718,
                            4.78242, -125.416, 45.458, 4.41088,
                            -125.623, 46.33700000000001, 4.02817,
                            -125.746, 46.642, 3.7974, -125.874,
                            46.965, 3.64988, -126.015, 47.289,
                            3.65067, -126.23999999999998, 47.661,
                            3.67516, -126.422, 47.994, 3.90795,
                            -126.66000000000001, 48.287, 4.12516,
                            -127.037, 48.711, 4.58367, -127.605,
                            49.279, 4.76158]

        fault_bottom_edge = [-124.0415, 40.347, 15.55, -124.33,
                            41.214000000000006, 13.46,
                            -124.474, 42.1095, 13.44, -124.5375,
                            42.9775, 13.32, -124.51500000000001,
                            43.861, 14.19, -124.4955, 44.737,
                            14.89, -124.43400000000001, 45.487,
                            16.57, -124.28950000000002, 46.361,
                            19.0, -124.169, 46.7745, 20.0,
                            -124.051, 47.2145, 20.35,
                            -124.09550000000002, 47.669, 20.1,
                            -124.5975, 48.0865, 19.47,
                            -125.19899999999998, 48.416, 19.09,
                            -125.7345, 48.723, 18.9, -126.354,
                            49.111, 18.46, -127.084, 49.5945,
                            17.37]

        self.assertEqual(fault_bottom_edge, geo[1])
        self.assertEqual(fault_top_edge, geo[0])

    def test_sp_simple_attrib(self):
        sm_id = 'sm1'
        sm_type = 'simple_point'
        sp_id = 'src04'
        sp_name = 'point'
        sp_tectonic_region = 'Active Shallow Crust'
        sp_hypocentral_depth = 5.0

        sp_location_dict_name = 'location'
        sp_location_name = 'epsg:4326'
        sp_location_pos = [-122.0, 38.0]
        location = self.gen_sp.get('location')

        self.assertEqual(sm_id, self.gen_sp.get('id_sm'))
        self.assertEqual(sm_type, self.gen_sp.get('type'))
        self.assertEqual(sp_id, self.gen_sp.get('id_sp'))
        self.assertEqual(sp_name, self.gen_sp.get('name'))
        self.assertEqual(sp_tectonic_region, self.gen_sp.get(
                'tectonic_region'))

        self.assertEqual(sp_location_dict_name, location['name'])
        self.assertEqual(sp_location_name, location['srs_name'])
        self.assertEqual(sp_location_pos, location['pos'])
        self.assertEqual(sp_hypocentral_depth, self.gen_sp.get(
                'hypocentral_depth'))

    def test_sp_rrm_truncated_gutenberg_richter(self):
        tgr = self.gen_sp.get('rupture_rate_model')[0]
        name = 'truncated_guten_richter'
        a_value_cumulative = 5.0
        b_value = 0.8
        min_magnitude = 5.0
        max_magnitude = 7.0

        self.assertEqual(name, tgr.get('name'))
        self.assertEqual(a_value_cumulative, tgr.get('a_value_cumulative'))
        self.assertEqual(b_value, tgr.get('b_value'))
        self.assertEqual(min_magnitude, tgr.get('min_magnitude'))
        self.assertEqual(max_magnitude, tgr.get('max_magnitude'))

    def test_sp_rrm_focal_mechanism(self):
        rrm_fm = self.gen_sp.get('rupture_rate_model')[1]
        fm_id = 'smi:local/1'
        name = 'focal_mechanism'
        first_nodal_plane = {'id': 0, 'strike': 0.0,
                'rake': 0.0, 'dip': 90.0}
        number_nodal_planes = 1

        self.assertEqual(fm_id, rrm_fm.get('id'))
        self.assertEqual(name, rrm_fm.get('name'))
        self.assertEqual(first_nodal_plane,
                rrm_fm.get('nodal_planes')[0])
        self.assertEquals(number_nodal_planes,
                len(rrm_fm.get('nodal_planes')))

    def test_sp_rdd(self):
        sp_rdd = self.gen_sp.get('rupture_depth_distribution')
        name = 'rupture_depth_distrib'
        magnitude = [6.0, 6.5, 7.0]
        depth = [5.0, 3.0, 0.0]

        self.assertEqual(name, sp_rdd.get('name'))
        self.assertEqual(depth, sp_rdd.get('depth'))
        self.assertEqual(magnitude, sp_rdd.get('magnitude'))
