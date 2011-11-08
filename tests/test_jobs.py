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

from mtoolkit.workflow import Context
from mtoolkit.jobs import read_eq_catalog, gardner_knopoff
from mtoolkit.jobs import _create_numpy_matrix

from tests.test_utils import get_data_path, ROOT_DIR, DATA_DIR


class JobsTestCase(unittest.TestCase):

    def setUp(self):
        self.context = Context(get_data_path(
            'config.yml', ROOT_DIR))
        self.eq_catalog_filename = get_data_path(
            'ISC_small_data.csv', DATA_DIR)

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

    def test_gardner_knopoff(self):

        self.context.config['eq_catalog_file'] = get_data_path(
            'declustering_input_test.csv', DATA_DIR)
        self.context.config['GardnerKnopoff']['time_dist_windows'] = 0.5

        read_eq_catalog(self.context)

        expected_vmain_shock = _create_numpy_matrix(self.context)
        expected_vmain_shock = np.delete(expected_vmain_shock, [4, 10, 19], 0)

        expected_vcl = np.array([0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0,
            0, 0, 0, 0, 6])

        expected_flag_vector = np.array([0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
            0, 0, 0, 0, 0, 0, 1])

        gardner_knopoff(self.context)

        self.assertTrue(np.array_equal(expected_vcl, self.context.vcl))
        self.assertTrue(np.array_equal(expected_flag_vector,
                self.context.flag_vector))
        self.assertTrue(np.array_equal(expected_vmain_shock,
                self.context.vmain_shock))
