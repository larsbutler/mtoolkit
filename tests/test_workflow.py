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

from mtoolkit.workflow import PipeLine, PipeLineBuilder, Context
from mtoolkit.jobs import read_eq_catalog, create_numpy_matrix, gardner_knopoff

from tests.test_utils import get_data_path, ROOT_DIR


class ContextTestCase(unittest.TestCase):

    def setUp(self):
        self.context = Context(get_data_path('config.yml', ROOT_DIR))

    def test_load_config_file(self):
        expected_config_dict = {
            'apply_processing_steps': None,
            'pprocessing_result_file': 'path_to_file',
            'GardnerKnopoff': {'time_dist_windows': False,
                    'foreshock_time_window': 0},
            'Stepp': {'increment_lock': True,
            'magnitude_windows': 0.2,
            'sensitivity': 0.1,
            'time_window': 5},
            'result_file': 'path_to_file',
            'eq_catalog_file': 'tests/data/ISC_correct.csv',
            'preprocessing_steps': ['GardnerKnopoff'],
            'source_model_file': 'path_to_file'}

        self.assertEqual(expected_config_dict, self.context.config)


class PipelineTestCase(unittest.TestCase):

    def setUp(self):

        def square_job(context):
            value = context.number
            context.number = value * value

        def double_job(context):
            value = context.number
            context.number = 2 * value

        self.square_job = square_job
        self.double_job = double_job

        self.pipeline_name = 'square pipeline'
        self.pipeline = PipeLine(self.pipeline_name)

        self.context = Context(get_data_path('config.yml', ROOT_DIR))
        self.context.number = 2

    def test_add_job(self):
        self.pipeline.add_job(self.square_job)
        self.pipeline.add_job(self.double_job)

        self.assertEqual(self.pipeline_name, self.pipeline.name)
        self.assertEqual(self.square_job, self.pipeline.jobs[0])
        self.assertEqual(self.double_job, self.pipeline.jobs[1])

    def test_run_jobs(self):
        self.pipeline.add_job(self.square_job)
        self.pipeline.add_job(self.double_job)
        self.pipeline.run(self.context)

        self.assertEqual(8, self.context.number)

        # Change jobs order
        self.pipeline.jobs.reverse()
        # Reset context to a base value
        self.context.number = 2
        self.pipeline.run(self.context)

        self.assertEqual(16, self.context.number)


class PipeLineBuilderTestCase(unittest.TestCase):

    def setUp(self):
        self.pipeline_name = 'main workflow'
        self.pipeline_builder = PipeLineBuilder(self.pipeline_name)
        self.context = Context(get_data_path('config.yml', ROOT_DIR))

    def test_build_pipeline(self):
        expected_pipeline = PipeLine(self.pipeline_name)
        expected_pipeline.add_job(read_eq_catalog)
        expected_pipeline.add_job(create_numpy_matrix)
        expected_pipeline.add_job(gardner_knopoff)

        self.assertEqual(expected_pipeline,
            self.pipeline_builder.build(self.context.config))
