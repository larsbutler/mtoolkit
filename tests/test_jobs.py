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
import numpy as np
from shapely.geometry import Polygon

from mtoolkit.workflow import Context
from mtoolkit.jobs import read_eq_catalog, apply_declustering
from mtoolkit.jobs import read_source_model, processing_workflow_setup_gen, \
_check_polygon
from mtoolkit.declustering import gardner_knopoff_decluster

from tests.test_utils import get_data_path, ROOT_DIR, DATA_DIR


class JobsTestCase(unittest.TestCase):

    def setUp(self):
        self.context = Context(get_data_path(
            'config.yml', ROOT_DIR))
        self.eq_catalog_filename = get_data_path(
            'ISC_small_data.csv', DATA_DIR)
        self.smodel_filename = get_data_path(
            'area_source_model.xml', DATA_DIR)

    def test_read_eq_catalog(self):
        self.context.config['eq_catalog_file'] = self.eq_catalog_filename
        expected_first_eq_entry = {'eventID': 1, 'Agency': 'AAA', 'month': 1,
                'depthError': 0.5, 'second': 13.0, 'SemiMajor90': 2.43,
                'year': 2000, 'ErrorStrike': 298.0, 'timeError': 0.02,
                'sigmamb': '', 'latitude': 44.368, 'sigmaMw': 0.355,
                'sigmaMs': '', 'Mw': 1.71, 'Ms': '',
                'Identifier': 20000102034913, 'day': 2, 'minute': 49,
                'hour': 3, 'mb': '', 'SemiMinor90': 1.01, 'longitude': 7.282,
                'depth': 9.3, 'ML': 1.7, 'sigmaML': 0.1}

        read_eq_catalog(self.context)

        self.assertEqual(10, len(self.context.eq_catalog))
        self.assertEqual(expected_first_eq_entry,
                self.context.eq_catalog[0])

    def test_apply_declustering(self):
        eq_entry = {'year': 2000,
                    'month': 1,
                    'day': 2,
                    'longitude': 7.282,
                    'latitude': 44.368,
                    'Mw': 1.71}
        numpy_matrix = np.array([[2000, 1, 2, 7.282, 44.368, 1.71]])
        vcl, vmain_shock, flag_vector = gardner_knopoff_decluster(numpy_matrix)

        self.context.eq_catalog = [eq_entry]
        apply_declustering(self.context)

        self.assertTrue(np.array_equal(vcl, self.context.vcl))
        self.assertTrue(np.array_equal(vmain_shock,
                self.context.vmain_shock))
        self.assertTrue(np.array_equal(flag_vector,
                self.context.flag_vector))

    def test_read_smodel(self):
        self.context.config['source_model_file'] = self.smodel_filename
        expected_first_sm_definition = \
            {'id_as': 'src_1',
             'area_boundary':
               [132.93, 42.85, 134.86,
                41.82, 129.73, 38.38,
                128.15, 40.35],
             'rupture_rate_model': [
               {'max_magnitude': 8.0,
                'a_value_cumulative':
                    3.1612436654341836,
                'name': 'truncated_guten_richter',
                'min_magnitude': 5.0,
                'b_value': 0.7318999871612379},
             {'name': 'focal_mechanism',
              'nodal_planes': [
                {'strike': 0.0,
                 'rake': 0.0,
                 'dip': 90.0,
                 'id': 0},
                {'strike': 12.0,
                 'rake': 0.0,
                 'dip': 40.0,
                 'id': 1}],
              'id': 'smi:fm1/0'}],
             'tectonic_region':
                'Active Shallow Crust',
             'id_sm': 'sm1',
             'rupture_depth_distribution': {
                'depth': [15.0],
                'magnitude': [5.0],
                'name': 'rupture_depth_distrib'},
             'hypocentral_depth': 15.0,
             'type': 'area_source',
             'name': 'Source 8.CH.3'}

        read_source_model(self.context)
        self.assertEqual(2, len(self.context.sm_definitions))
        self.assertEqual(expected_first_sm_definition,
                self.context.sm_definitions[0])

    def test_a_bad_polygon_raises_exception(self):
        polygon = Polygon([(1, 1), (1, 2), (2, 1), (2, 2)])

        self.assertRaises(RuntimeError, _check_polygon, polygon)

    def test_processing_workflow_setup(self):
        self.context.config['apply_processing_steps'] = True

        eq_internal_point = [2000, 1, 2, -0.25, 0.25]
        eq_external_point = [2000, 1, 2, 0.5, 0.25]
        eq_events = np.array([eq_internal_point, eq_external_point])
        self.context.vmain_shock = eq_events

        sm = {'area_boundary':
            [-0.5, 0.0, -0.5, 0.5, 0.0, 0.5, 0.0, 0.0]}
        self.context.sm_definitions = [sm]

        first_sm, filtered_eq_sm = \
            processing_workflow_setup_gen(self.context).next()

        expected_eq_events = np.array([eq_internal_point])

        self.assertTrue(np.array_equal(expected_eq_events, filtered_eq_sm))
        self.assertEqual(sm, first_sm)
