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

from collections import OrderedDict

class Pipeline(object):

    def __init__(self, name):
        self.name = name
        self.steps = OrderedDict()

    def add_step(self, name, func):
        try:
            self.steps[name]
            raise DuplicatedStepError(name)
        except KeyError:
            self.steps[name] = Step(func)


class Step(object):

    def __init__(self, func):
        self.func = func


class DuplicatedStepError(Exception):

    def __init__(self, step):
        msg = "Duplicated step error with step name: %s " % step
        Exception.__init__(self, msg)
        self.args = (step,)
