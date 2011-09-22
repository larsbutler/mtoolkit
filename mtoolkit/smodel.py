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
to read different source models data from a nrml
file.
"""

import os
import mtoolkit.xml_utils as xml_utils
from lxml import etree


class SourceModelReader(object):
    """
    SourceModelReader allows to read source models (SM)
    in a nrml file, in an iterative way by providing
    a dict data structure.
    """

    def __init__(self, filename, schema):
        file_exists = os.path.exists(filename)
        if not file_exists:
            raise IOError('File %s not found' % filename)
        if not xml_utils.valid_schema(filename, schema):
            raise xml_utils.XMLValidationError(filename,
               'The source model is not conform to the schema')
        self.filename = filename
        self.schema = schema

    def read(self):
        """
        Return a generator which provides a SM definition
        for every source model read.
        """

        with open(self.filename, 'rb') as nrml_file:
            elem = 1
            for source_model in etree.iterparse(nrml_file,
                tag=xml_utils.AREA_SOURCE):
                if source_model[elem].tag == xml_utils.AREA_SOURCE:
                    source_model_id = source_model[elem].getparent().get(
                        xml_utils.SOURCE_MODEL_ID_ATTR)
                    source = self._parse_area_source(source_model_id,
                            source_model[elem])
                yield source

    def _parse_area_source(self, source_model_id, source_model):
        """
        Return a complex dict data structure representing
        the parsed area source model, the dict data structure
        also contains other dicts such as: area_boundary,
        rupture_depth_distribution and a list which itself
        contains two dicts: truncated_guten_richter and
        focal_mechanism.
        Area source (as) complete dict structure description:
            source_model_id
            as_id
            as_name
            as_tectonic_region
            {as_area_boundary: [(pos)]}
            as_rupture_rate_model=
                    [   {truncated_guten_richter},
                        {focal_mechanism: [nodal_planes]
                         where each nodal plane is {} }
                    ]
            {rupture_depth_distribution}
            as_hypocentral_depth
        """

        area_source = {'type': 'area_source'}
        area_source['id_sm'] = source_model_id

        as_id = source_model.get(xml_utils.AREA_SOURCE_ID)
        area_source['id_as'] = as_id

        as_name = source_model.find(xml_utils.GML_NAME).text
        area_source['name'] = as_name

        as_tectonic_region = source_model.find(xml_utils.TECTONIC_REGION).text
        area_source['tectonic_region'] = as_tectonic_region

        as_area_boundary = self._parse_area_boundary(source_model.find(
                xml_utils.AREA_BOUNDARY))
        area_source['area_boundary'] = as_area_boundary

        as_rupture_rate_model = self._parse_rupture_rate_model(
            source_model.find(xml_utils.RUPTURE_RATE_MODEL))
        area_source['rupture_rate_model'] = as_rupture_rate_model

        as_rupture_depth_distribution = self._parse_rupture_depth_distrib(
            source_model.find(xml_utils.RUPTURE_DEPTH_DISTRIB))
        area_source['rupture_depth_distribution'] = \
                                as_rupture_depth_distribution

        as_hypocentral_depth = source_model.find(
            xml_utils.HYPOCENTRAL_DEPTH).text
        area_source['hypocentral_depth'] = as_hypocentral_depth

        source_model.clear()
        return area_source

    def _parse_area_boundary(self, area_boundary):
        """
        Return a dict structure which contains
        area boundary data.
        """

        pos_list = area_boundary.find('.//%s' %
                xml_utils.A_BOUNDARY_POS_LIST).text.split()
        pos_couple_list = [(pos_list[i], pos_list[i + 1])
                for i in xrange(0, len(pos_list), 2)]

        area_boundary.clear()
        area_boundary_read = {'name': 'area_boundary'}

        area_boundary_read = {'area_boundary_pos_list': pos_couple_list}
        return area_boundary_read

    def _parse_rrm_focal_mecanism(self, rupture_rate_model):
        """
        Return a dict structure which contains
        focal mechanism data.
        """

        focal_mechanism = {'name': 'focal_mechanism'}
        nodal_plane_read = {}

        focal_mechanism_id = rupture_rate_model.find('.//%s' %
                xml_utils.FOCAL_MECHANISM).get(xml_utils.FM_ID_ATTR)
        focal_mechanism['id'] = focal_mechanism_id

        nodal_planes = rupture_rate_model.find('.//%s' %
                xml_utils.NODAL_PLANES)
        list_nodal_plane = []
        id_nodal_plane = 0
        for nodal_plane in nodal_planes.iterchildren():
            nodal_plane_read['id'] = id_nodal_plane

            np_strike = nodal_plane.find('.//%s' %
                    xml_utils.NODAL_PLANE_STRIKE).getchildren()[0].text
            nodal_plane_read['strike'] = np_strike

            np_dip = nodal_plane.find('.//%s' %
                    xml_utils.NODAL_PLANE_DIP).getchildren()[0].text
            nodal_plane_read['dip'] = np_dip

            np_rake = nodal_plane.find('.//%s' %
                    xml_utils.NODAL_PLANE_RAKE).getchildren()[0].text
            nodal_plane_read['rake'] = np_rake
            list_nodal_plane.append(nodal_plane_read)
            id_nodal_plane += 1
        nodal_planes.clear()

        focal_mechanism['nodal_planes'] = list_nodal_plane
        return focal_mechanism

    def _parse_rupture_rate_model(self, rupture_rate_model):
        """
        Return a list which contains two dicts
        trunctated_guten_richter and focal_mechanism.
        """

        rupture_rate_model_read = []
        truncated_guten_richter = {'name': 'truncated_guten_richter'}

        rrm_a_value_cumulative = rupture_rate_model.find('.//%s' %
                xml_utils.A_VALUE_CUMULATIVE).text
        truncated_guten_richter['a_value_cumulative'] = rrm_a_value_cumulative

        rrm_b_value = rupture_rate_model.find('.//%s' %
                xml_utils.B_VALUE).text
        truncated_guten_richter['b_value'] = rrm_b_value

        rrm_min_magnitude = rupture_rate_model.find('.//%s' %
                xml_utils.MIN_MAGNITUDE).text
        truncated_guten_richter['min_magnitude'] = rrm_min_magnitude

        rrm_max_magnitude = rupture_rate_model.find('.//%s' %
                xml_utils.MAX_MAGNITUDE).text
        truncated_guten_richter['max_magnitude'] = rrm_max_magnitude

        rupture_rate_model_read.append(truncated_guten_richter)

        focal_mechanism = self._parse_rrm_focal_mecanism(rupture_rate_model)
        rupture_rate_model.clear()

        rupture_rate_model_read.append(focal_mechanism)
        return rupture_rate_model_read

    def _parse_rupture_depth_distrib(self, rupture_depth_distrib):
        """
        Return a dict structure which contains rupture depth
        distribuition.
        """

        rupture_depth_distrib_read = {}
        magnitude = rupture_depth_distrib.find('.//%s' %
                xml_utils.MAGNITUDE).text
        depth = rupture_depth_distrib.find('.//%s' % xml_utils.DEPTH).text
        rupture_depth_distrib.clear()

        rupture_depth_distrib_read['name'] = 'rupture_depth_distrib'
        rupture_depth_distrib_read['magnitude'] = magnitude
        rupture_depth_distrib_read['depth'] = depth
        return rupture_depth_distrib_read
