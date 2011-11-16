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
The purpose of this module is to provide functions
which tackle specific job.
"""

import logging
import numpy as np
from shapely.geometry import Polygon, Point

from mtoolkit.eqcatalog     import EqEntryReader
from mtoolkit.smodel        import NRMLReader
from mtoolkit.utils import get_data_path, SCHEMA_DIR

NRML_SCHEMA_PATH = get_data_path('nrml.xsd', SCHEMA_DIR)


def logged_job(job):
    """
    Decorate a job by adding logging
    statements before and after the execution
    of the job
    """

    def wrapper(context):
        """Wraps a job, adding logging statements"""
        logger = logging.getLogger('mt_logger')
        start_job_line = 'Start:\t%21s \t' % job.__name__
        end_job_line = 'End:\t%21s \t' % job.__name__
        logger.info(start_job_line)
        job(context)
        logger.info(end_job_line)
    return wrapper


@logged_job
def read_eq_catalog(context):
    """Create eq entries by reading an eq catalog"""

    reader = EqEntryReader(context.config['eq_catalog_file'])
    eq_entries = []
    for eq_entry in reader.read():
        eq_entries.append(eq_entry)
    context.eq_catalog = eq_entries


@logged_job
def read_source_model(context):
    """Create smodel definitions by reading a source model"""

    reader = NRMLReader(context.config['source_model_file'],
            NRML_SCHEMA_PATH)
    sm_definitions = []
    for sm in reader.read():
        sm_definitions.append(sm)
    context.sm_definitions = sm_definitions


@logged_job
def create_catalog_matrix(context):
    """Create a numpy matrix according to fixed attributes"""

    matrix = []
    attributes = ['year', 'month', 'day', 'longitude', 'latitude', 'Mw']
    for eq_entry in context.eq_catalog:
        matrix.append([eq_entry[attribute] for attribute in attributes])
    context.catalog_matrix = np.array(matrix)


@logged_job
def gardner_knopoff(context):
    """Apply gardner_knopoff declustering algorithm to the eq catalog"""

    vcl, vmain_shock, flag_vector = context.map_sc['gardner_knopoff'](
            context.catalog_matrix,
            context.config['GardnerKnopoff']['time_dist_windows'],
            context.config['GardnerKnopoff']['foreshock_time_window'])

    context.vcl = vcl
    context.catalog_matrix = vmain_shock
    context.flag_vector = flag_vector


@logged_job
def stepp(context):
    """
    Apply step algorithm to the eq catalog
    or to the numpy array built by a
    declustering algorithm
    """

    year_index = 0
    mw_index = 5

    context.completeness_table = context.map_sc['stepp'](
        context.catalog_matrix[:, year_index],
        context.catalog_matrix[:, mw_index],
        context.config['Stepp']['magnitude_windows'],
        context.config['Stepp']['time_window'],
        context.config['Stepp']['sensitivity'],
        context.config['Stepp']['increment_lock'])


def _processing_steps_required(context):
    """Return bool which states if processing steps are required"""

    return context.config['apply_processing_steps']


def _create_polygon(source_model):
    """
    Return a polygon object which is built
    using a list of points contained in
    the source model geometry
    """

    area_boundary_plist = source_model['area_boundary']
    points_list = [(area_boundary_plist[i], area_boundary_plist[i + 1])
            for i in xrange(0, len(area_boundary_plist), 2)]
    return Polygon(points_list)


def _check_polygon(polygon):
    """Check polygon validity"""

    if not polygon.is_valid:
        raise RuntimeError('Polygon invalid wkt: %s' % polygon.wkt)


def _filter_eq_entries(context, polygon):
    """
    Return a numpy matrix of filtered eq events.
    The matrix contains all eq entries
    contained in the given polygon
    """

    filtered_eq = []
    longitude = 3
    latitude = 4
    for eq in context.vmain_shock:
        eq_point = Point(eq[longitude], eq[latitude])
        if polygon.contains(eq_point):
            filtered_eq.append(eq)
    return np.array(filtered_eq)


def processing_workflow_setup_gen(context):
    """
    Return the necessary input to start
    the processing pipeline. The input
    is constituted by a source model and
    the eq events related to the source
    model geometry in the form of a numpy
    matrix
    """

    if _processing_steps_required(context):
        for sm in context.sm_definitions:
            polygon = _create_polygon(sm)
            _check_polygon(polygon)
            filtered_eq = _filter_eq_entries(context, polygon)
            yield sm, filtered_eq
