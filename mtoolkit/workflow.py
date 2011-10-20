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

"""
The purpose of this module is to provide objects
to process a series of jobs in a predetermined
order. The order is determined by the queue of jobs.
"""


class Pipeline(object):
    """
    Pipeline allows to create a queue of
    jobs and execute them in order.
    """

    def __init__(self, name):
        """
        Initialize a pipeline object having
        attributes: name and jobs, a list
        of callable objects.
        """

        self.name = name
        self.jobs = []

    def add_job(self, a_callable):
        """Append a new job the to queue"""

        self.jobs.append(a_callable)

    def run(self, context):
        """
        Run all the jobs in queue,
        where each job take input data
        and write the results
        of calculation in context.
        """

        for job in self.jobs:
            job(context)
