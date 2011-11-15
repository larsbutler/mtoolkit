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

import yaml
import logging
from itertools import imap

from mtoolkit.jobs import read_eq_catalog, gardner_knopoff, stepp, \
create_catalog_matrix


def logged_job(job):
    """
    Decorate a job by adding logging
    statements before and after the execution
    of the job
    """

    def wrapper(context):
        """Wraps a job, adding logging statements"""
        logger = logging.getLogger('mt_logger')
        start_job_line = 'Start:\t%s \t' % job.__name__
        end_job_line = 'End:\t%s \t' % job.__name__
        logger.debug(start_job_line)
        logger.info(start_job_line)
        job(context)
        logger.debug(end_job_line)
        logger.info(end_job_line)
    return wrapper


class PipeLine(object):
    """
    PipeLine allows to create a queue of
    jobs and execute them in order.
    """

    def __init__(self, name):
        """
        Initialize a PipeLine object having
        attributes: name and jobs, a list
        of callable objects.
        """

        self.name = name
        self.jobs = []

    def __eq__(self, other):
        return self.name == other.name\
                and self.jobs == other.jobs

    def add_job(self, a_callable):
        """Append a new job the to queue"""

        self.jobs.append(a_callable)

    def run(self, context, log):
        """
        Run all the jobs in queue,
        where each job take input data
        and write the results
        of calculation in context.
        If logging is triggered by cmdline
        each job is decorated by adding
        logging statements.
        """

        if log:
            self.jobs = imap(logged_job, self.jobs)
        for job in self.jobs:
            job(context)


class PipeLineBuilder(object):
    """
    PipeLineBuilder allows to build a PipeLine
    by assembling all the required jobs/steps
    specified in the config file.
    """

    def __init__(self, name):
        self.name = name
        self.map_step_callable = {'GardnerKnopoff': gardner_knopoff,
                                  'Stepp': stepp}

    def build(self, config):
        """
        Build method creates the pipeline by
        assembling all the steps required.
        The steps described in the config
        could be preprocessing or processing
        steps.
        """

        pipeline = PipeLine(self.name)
        pipeline.add_job(read_eq_catalog)
        pipeline.add_job(create_catalog_matrix)
        for step in config['preprocessing_steps']:
            pipeline.add_job(self.map_step_callable[step])

        return pipeline


class Context(object):
    """
    Context allows to read the config file
    and store preprocessing/processing steps
    intermediate results.
    """

    def __init__(self, config_filename):
        config_file = open(config_filename, 'r')
        self.config = yaml.load(config_file)
