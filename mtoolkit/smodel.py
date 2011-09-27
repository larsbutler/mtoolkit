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

from lxml import etree

from mtoolkit import xml_utils

XML_NODE = 1


class NRMLReader(object):
    """
    NRMLReader allows to read source models (SM)
    in a nrml file, in an iterative way by providing
    a dict data structure.
    """

    def __init__(self, filename, schema):
        file_exists = os.path.exists(filename)
        if not file_exists:
            raise IOError('File %s not found' % filename)
        if not xml_utils.valid_schema(filename, schema):
            raise xml_utils.XMLValidationError(filename,
               'The source model does not conform to the schema')
        self.filename = filename
        self.tag_action = {xml_utils.AREA_SOURCE: self._parse_area_source,
            xml_utils.SIMPLE_FAULT_SOURCE: self._parse_simple_fault}

    def read(self):
        """
        Return a generator which provides a SM definition
        for every source model read.
        """

        with open(self.filename, 'rb') as nrml_file:
            for source_model in etree.iterparse(nrml_file):
                tag = source_model[XML_NODE].tag
                if tag in self.tag_action:
                    yield self.tag_action[tag](source_model[XML_NODE])

    def _parse_area_source(self, source_model):
        """
        Return a complex dict data structure representing
        the parsed area source model, the dict data structure
        also contains other dicts such as: area_boundary,
        rupture_depth_distribution and a list which itself
        contains two dicts: truncated_guten_richter and
        focal_mechanism.
        Area source (as) complete dict structure description:
            type    - source model type
            id_sm   - source model id
            id_as   - area source id
            name    - area source name
            tectonic_region - area source tectonic region
            {area_boundary: [(latitude, longitude)]}
             rupture_rate_model=
                [   {truncated_guten_richter},
                    {focal_mechanism: [nodal_planes]
                        where each nodal plane is {} }
                ]
            {rupture_depth_distribution}
            hypocentral_depth
        """

        area_source = {'type': 'area_source'}
        area_source['id_sm'] = source_model.getparent()\
                .get(xml_utils.GML_ID)

        area_source['id_as'] = source_model.get(
            xml_utils.GML_ID)

        area_source['name'] = source_model.find(
            xml_utils.GML_NAME).text

        area_source['tectonic_region'] = source_model.find(
            xml_utils.TECTONIC_REGION).text

        area_source['area_boundary'] = self._parse_area_boundary(
            source_model.find(xml_utils.AREA_BOUNDARY))

        area_source['rupture_rate_model'] = self._parse_rupture_rate_model(
            source_model.find(xml_utils.RUPTURE_RATE_MODEL))

        area_source['rupture_depth_distribution'] = \
                                self._parse_rupture_depth_distrib(
            source_model.find(xml_utils.RUPTURE_DEPTH_DISTRIB))

        area_source['hypocentral_depth'] = float(source_model.find(
            xml_utils.HYPOCENTRAL_DEPTH).text)

        source_model.clear()
        return area_source

    def _parse_area_boundary(self, area_boundary):
        """
        Return a dict structure which contains
        area boundary data.
        """

        pos_list = area_boundary.find('.//%s' %
                xml_utils.POS_LIST).text.split()
        pos_couple_list = [((float(pos_list[i])), float(pos_list[i + 1]))
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

        focal_mechanism['id'] = rupture_rate_model.find(
                xml_utils.FOCAL_MECHANISM).get(xml_utils.FM_ID_ATTR)

        nodal_plane_elems = rupture_rate_model.find('.//%s' %
                xml_utils.NODAL_PLANES)
        nodal_planes = []
        for child, nodal_plane_elem in enumerate(nodal_plane_elems):
            nodal_plane_read = {}

            nodal_plane_read['id'] = child

            nodal_plane_read['strike'] = float(nodal_plane_elem.find(
                    xml_utils.NODAL_PLANE_STRIKE).getchildren()[0].text)

            nodal_plane_read['dip'] = float(nodal_plane_elem.find(
                    xml_utils.NODAL_PLANE_DIP).getchildren()[0].text)

            nodal_plane_read['rake'] = float(nodal_plane_elem.find(
                    xml_utils.NODAL_PLANE_RAKE).getchildren()[0].text)

            nodal_planes.append(nodal_plane_read)
        nodal_plane_elems.clear()

        focal_mechanism['nodal_planes'] = nodal_planes
        return focal_mechanism

    def _parse_rupture_rate_model(self, rupture_rate_model):
        """
        Return a list which contains two dicts
        trunctated_guten_richter and focal_mechanism.
        """

        rupture_rate_model_read = []

        rupture_rate_model_read.append(
            self._parse_truncated_guten_richter(rupture_rate_model.find(
            xml_utils.TRUNCATED_GUTEN_RICHTER)))

        focal_mechanism = self._parse_rrm_focal_mecanism(rupture_rate_model)
        rupture_rate_model.clear()

        rupture_rate_model_read.append(focal_mechanism)
        return rupture_rate_model_read

    def _parse_rupture_depth_distrib(self, rupture_depth_distrib):
        """
        Return a dict structure which contains rupture depth
        distribuition data.
        """

        rupture_depth_distrib_read = {}
        magnitude = float(rupture_depth_distrib.find(
                xml_utils.MAGNITUDE).text)
        depth = float(rupture_depth_distrib.find(
                xml_utils.DEPTH).text)
        rupture_depth_distrib.clear()

        rupture_depth_distrib_read['name'] = 'rupture_depth_distrib'
        rupture_depth_distrib_read['magnitude'] = magnitude
        rupture_depth_distrib_read['depth'] = depth
        return rupture_depth_distrib_read

    def _parse_truncated_guten_richter(self, tgr_node):
        """
        Return a dict structure which contains truncated
        gutenberg richter data
        """

        truncated_guten_richter = {'name': 'truncated_guten_richter'}

        truncated_guten_richter['a_value_cumulative'] = float(
            tgr_node.find(xml_utils.A_VALUE_CUMULATIVE).text)

        truncated_guten_richter['b_value'] = float(
            tgr_node.find(xml_utils.B_VALUE).text)

        truncated_guten_richter['min_magnitude'] = float(
            tgr_node.find(xml_utils.MIN_MAGNITUDE).text)

        truncated_guten_richter['max_magnitude'] = float(
            tgr_node.find(xml_utils.MAX_MAGNITUDE).text)

        tgr_node.clear()
        return truncated_guten_richter

    def _parse_simple_fault(self, source_model):
        """
        Return a complex dict data structure representing
        the parsed simple fault source model, the dict data
        structure also contains other dicts such as:
        truncated_guten_richter and geometry

        Simple Fault source (sf) complete dict structure description:
            type    - source model type
            id_sm   - source model id
            id_sf   - simple fault id
            name    - simple fault name
            tectonic_region - simple fault tectonic region
            rake    - simple fault rake
            {truncated_guten_richter}
            {geometry:[(lat, lon, depth)]}
        """

        simple_fault = {'type': 'simple_fault'}

        simple_fault['id_sm'] = source_model.getparent()\
                .get(xml_utils.GML_ID)

        simple_fault['id_sf'] = source_model.get(xml_utils.GML_ID)

        simple_fault['name'] = source_model.find(
            xml_utils.GML_NAME).text

        simple_fault['tectonic_region'] = source_model.find(
            xml_utils.TECTONIC_REGION).text

        simple_fault['rake'] = float(source_model.find(
            xml_utils.RAKE).text)

        simple_fault['truncated_guten_richter'] = \
            self._parse_truncated_guten_richter(source_model.find(
                    xml_utils.TRUNCATED_GUTEN_RICHTER))

        simple_fault['geometry'] = \
            self._parse_simple_fault_geometry(source_model.find(
                    xml_utils.SIMPLE_FAULT_GEOMETRY))

        source_model.clear()
        return simple_fault

    def _parse_simple_fault_geometry(self, sf_geometry):
        """
        Return a dict structure which contains
        geometry data.
        """

        geometry = {'name': 'geometry'}
        geometry['id'] = sf_geometry.get(
            xml_utils.GML_ID)

        pos_list = sf_geometry.find('.//%s' %
            xml_utils.POS_LIST).text.split()
        geometry['fault_trace_pos_list'] = \
            [((float(pos_list[i])),
            float(pos_list[i + 1]), float(pos_list[i + 2]))
                for i in xrange(0, len(pos_list), 3)]

        geometry['dip'] = float(sf_geometry.find(
            xml_utils.DIP).text)

        geometry['upper_seismogenic_depth'] = float(sf_geometry.find(
            xml_utils.UPPER_SEISMOGENIC_DEPTH).text)

        geometry['lower_seismogenic_depth'] = float(sf_geometry.find(
            xml_utils.LOWER_SEISMOGENIC_DEPTH).text)

        sf_geometry.clear()
        return geometry
