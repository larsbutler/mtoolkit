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


class Pipeline(object):

    def __init__(self, name, context):
        self.name = name
        self.jobs = []
        self.context = context

    def add_job(self, a_callable, working_data):
        new_job = Job(a_callable, working_data)
        self.jobs.append(new_job)

    def run(self):
        for job in self.jobs:
            self.context[job.working_data] = job.execute(
                self.context[job.working_data])


class Job(object):

    def __init__(self, a_callable, working_data):
        self.job = a_callable
        self.working_data = working_data

    def execute(self, data):
        return self.job(data)
