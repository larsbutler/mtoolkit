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

import numpy as np
from shapely.geometry import Polygon, Point

from mtoolkit.eqcatalog     import EqEntryReader
from mtoolkit.smodel        import NRMLReader
from mtoolkit.declustering  import gardner_knopoff_decluster
from mtoolkit.completeness  import stepp_analysis

from tests.test_utils import get_data_path, SCHEMA_DIR

NRML_SCHEMA_PATH = get_data_path('nrml.xsd', SCHEMA_DIR)


def read_eq_catalog(context):
    """Create eq entries by reading an eq catalog"""

    reader = EqEntryReader(context.config['eq_catalog_file'])
    eq_entries = []
    for eq_entry in reader.read():
        eq_entries.append(eq_entry)
    context.eq_catalog = eq_entries


def read_source_model(context):
    """Create smodel definitions by reading a source model"""

    reader = NRMLReader(context.config['source_model_file'],
            NRML_SCHEMA_PATH)
    sm_definitions = []
    for sm in reader.read():
        sm_definitions.append(sm)
    context.sm_definitions = sm_definitions


def _create_numpy_matrix(context):
    """Create a numpy matrix according to fixed attributes"""

    matrix = []
    attributes = ['year', 'month', 'day', 'longitude', 'latitude', 'Mw']
    for eq_entry in context.eq_catalog:
        matrix.append([eq_entry[attribute] for attribute in attributes])
    return np.array(matrix)


def gardner_knopoff(context, alg=gardner_knopoff_decluster):
    """Apply gardner_knopoff declustering algorithm to the eq catalog"""

    vcl, vmain_shock, flag_vector = alg(
            _create_numpy_matrix(context),
            context.config['GardnerKnopoff']['time_dist_windows'],
            context.config['GardnerKnopoff']['foreshock_time_window'])

    context.vcl = vcl
    context.vmain_shock = vmain_shock
    context.flag_vector = flag_vector


def a_declustering_was_executed(context):
    """
    Return True if a declustering
    algorithm has been executed in
    the pipeline
    """
    return hasattr(context, 'vmain_shock')


def stepp(context, alg=stepp_analysis):
    """
    Apply step algorithm to the eq catalog
    or to the numpy array built by a
    declustering algorithm
    """

    year_index = 0
    mw_index = 5

    if a_declustering_was_executed(context):
        context.completeness_table = alg(
            context.vmain_shock[:, year_index],
            context.vmain_shock[:, mw_index],
            context.config['Stepp']['magnitude_windows'],
            context.config['Stepp']['time_window'],
            context.config['Stepp']['sensitivity'],
            context.config['Stepp']['increment_lock'])
    else:
        context.numpy_matrix = _create_numpy_matrix(context)
        context.completeness_table = alg(
            context.numpy_matrix[:, year_index],
            context.numpy_matrix[:, mw_index],
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
