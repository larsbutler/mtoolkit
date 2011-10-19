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

from mtoolkit.workflow import Pipeline

class PipelineTestCase(unittest.TestCase):



    def setUp(self):

        def square_job(x):
            return x*x

        def double_job(x):
            return 2*x

        self.square_job = square_job
        self.double_job = double_job
        self.pipeline_name = 'square pipeline'
        self.working_data = 'number'
        self.context = {self.working_data: 2}
        self.pipeline = Pipeline(self.pipeline_name, self.context)


    def test_add_job(self):
        self.pipeline.add_job(self.square_job, self.working_data)
        self.pipeline.add_job(self.double_job, self.working_data)

        self.assertEqual(self.square_job, self.pipeline.jobs[0].job)
        self.assertEqual(self.double_job, self.pipeline.jobs[1].job)

    def test_run_jobs(self):
        self.pipeline.add_job(self.square_job, self.working_data)
        self.pipeline.add_job(self.double_job, self.working_data)
        self.pipeline.run()
        self.assertEqual(8, self.pipeline.context[self.working_data])
