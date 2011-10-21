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

from mtoolkit.jobs import load_config_file

from tests.test_utils import get_data_path, ROOT_DIR


class JobsTestCase(unittest.TestCase):

    def setUp(self):
        self.context = {'config_filename': get_data_path(
            'config.yml', ROOT_DIR),
                        'config': {}}

    def test_load_config_file(self):
        expected_config_dict = {
            'apply_processing_steps': None,
            'pprocessing_result_file': 'path_to_file',
            'GardnerKnopoff': {'time_dist_windows': False,
                    'foreshock_time_window': 0},
            'result_file': 'path_to_file',
            'eq_catalog_file': 'path_to_file',
            'preprocessing_steps': ['GardnerKnopoff'],
            'source_model_file': 'path_to_file'}

        load_config_file(self.context)

        self.assertEqual(expected_config_dict, self.context['config'])
