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

from mtoolkit.workflow import Pipeline, DuplicatedStepError

class PipelineTestCase(unittest.TestCase):



    def setUp(self):
        def square_step(x):
            return x*x

        self.pipeline = Pipeline('preprocessing step')
        self.step_name = 'square(x)'
        self.step_callable = square_step

    def test_add_processing_step(self):
        self.pipeline.add_step(self.step_name, self.step_callable)
        self.assertEqual(self.pipeline.steps[self.step_name].func,
                self.step_callable)

    def test_adding_a_duplicate_step_raise_exception(self):
        self.pipeline.add_step(self.step_name, self.step_callable)
        self.assertRaises(DuplicatedStepError,
                self.pipeline.add_step, self.step_name, self.step_callable)

