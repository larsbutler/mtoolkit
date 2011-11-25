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

from mtoolkit import utils

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
        if not utils.valid_schema(filename, schema):
            raise utils.XMLValidationError(filename,
               'The source model does not conform to the schema')
        self.filename = filename
        self.tag_action = {utils.AREA_SOURCE: self._parse_area_source,
            utils.SIMPLE_FAULT_SOURCE: self._parse_simple_fault,
            utils.COMPLEX_FAULT_SOURCE: self._parse_complex_fault,
            utils.SIMPLE_POINT_SOURCE: self._parse_simple_point}

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

    def _parse_area_source(self, as_node):
        """
        Return a complex dict data structure representing
        the parsed area source model, the dict data structure
        also contains another dict, rupture_depth_distribution
        and a list which itself contains two dicts:
        truncated_guten_richter and focal_mechanism.
        Area source (as) complete dict structure description:
            type    - source model type
            id_sm   - source model id
            id_as   - area source id
            name    - area source name
            tectonic_region - area source tectonic region
            area_boundary: [values]
             rupture_rate_model=
                [   {truncated_guten_richter},
                    {focal_mechanism: [nodal_planes]
                        where each nodal plane is {} }
                ]
            {rupture_depth_distribution}
            hypocentral_depth
        """

        area_source = {'type': 'area_source'}
        area_source['id_sm'] = as_node.getparent().get(
            utils.GML_ID)

        area_source['id_as'] = as_node.get(
            utils.GML_ID)

        area_source['name'] = as_node.find(
            utils.GML_NAME).text

        area_source['tectonic_region'] = as_node.find(
            utils.TECTONIC_REGION).text

        area_source['area_boundary'] = [float(value) for value in
            as_node.find(utils.AREA_BOUNDARY).find('.//%s' %
                    utils.POS_LIST).text.split()]

        area_source['rupture_rate_model'] = self._parse_rupture_rate_model(
            as_node.find(utils.RUPTURE_RATE_MODEL))

        area_source['rupture_depth_distribution'] = \
                                self._parse_rupture_depth_distrib(
            as_node.find(utils.RUPTURE_DEPTH_DISTRIB))

        area_source['hypocentral_depth'] = float(as_node.find(
            utils.HYPOCENTRAL_DEPTH).text)

        as_node.clear()

        return area_source

    def _parse_truncated_guten_richter(self, tgr_node):
        """
        Return a dict structure which contains truncated
        gutenberg richter data.
        """

        truncated_guten_richter = {'name': 'truncated_guten_richter'}

        truncated_guten_richter['a_value_cumulative'] = float(
            tgr_node.find(utils.A_VALUE_CUMULATIVE).text)

        truncated_guten_richter['b_value'] = float(
            tgr_node.find(utils.B_VALUE).text)

        truncated_guten_richter['min_magnitude'] = float(
            tgr_node.find(utils.MIN_MAGNITUDE).text)

        truncated_guten_richter['max_magnitude'] = float(
            tgr_node.find(utils.MAX_MAGNITUDE).text)

        tgr_node.clear()

        return truncated_guten_richter

    def _parse_focal_mechanism(self, fm_node):
        """
        Return a dict structure which contains
        focal mechanism data.
        """

        focal_mechanism = {'name': 'focal_mechanism'}

        focal_mechanism['id'] = fm_node.get(
            utils.FM_ID_ATTR)

        nodal_plane_nodes = fm_node.find(
                utils.NODAL_PLANES)

        nodal_planes = []
        for child, nodal_plane_elem in enumerate(nodal_plane_nodes):
            nodal_plane_read = {}

            nodal_plane_read['id'] = child

            nodal_plane_read['strike'] = float(nodal_plane_elem.find(
                    utils.NODAL_PLANE_STRIKE).getchildren()[0].text)

            nodal_plane_read['dip'] = float(nodal_plane_elem.find(
                    utils.NODAL_PLANE_DIP).getchildren()[0].text)

            nodal_plane_read['rake'] = float(nodal_plane_elem.find(
                    utils.NODAL_PLANE_RAKE).getchildren()[0].text)

            nodal_planes.append(nodal_plane_read)

        nodal_plane_nodes.clear()
        fm_node.clear()

        focal_mechanism['nodal_planes'] = nodal_planes

        return focal_mechanism

    def _parse_rupture_rate_model(self, rrm_node):
        """
        Return a list which contains two dicts
        trunctated_guten_richter and focal_mechanism.
        """

        rupture_rate_model_read = []

        rupture_rate_model_read.append(
            self._parse_truncated_guten_richter(rrm_node.find(
                utils.TRUNCATED_GUTEN_RICHTER)))

        rupture_rate_model_read.append(
            self._parse_focal_mechanism(rrm_node.find(
                utils.FOCAL_MECHANISM)))

        rrm_node.clear()

        return rupture_rate_model_read

    def _parse_rupture_depth_distrib(self, rdd_node):
        """
        Return a dict structure which contains rupture depth
        distribuition data.
        """

        rupture_depth_distrib_read = {'name': 'rupture_depth_distrib'}
        rupture_depth_distrib_read['magnitude'] = [float(value) for value in
            rdd_node.find(utils.MAGNITUDE).text.split()]

        rupture_depth_distrib_read['depth'] = [float(value) for value in
            rdd_node.find(utils.DEPTH).text.split()]

        rdd_node.clear()

        return rupture_depth_distrib_read

    def _parse_simple_fault(self, sf_node):
        """
        Return a complex dict data structure representing
        the parsed simple fault source model, the dict data
        structure also contains other dicts such as:
        truncated_guten_richter and geometry.
        Simple Fault source (sf) complete dict structure description:
            type    - source model type
            id_sm   - source model id
            id_sf   - simple fault id
            name    - simple fault name
            tectonic_region - simple fault tectonic region
            rake    - simple fault rake
            {truncated_guten_richter}
            {geometry}
        """

        simple_fault = {'type': 'simple_fault'}

        simple_fault['id_sm'] = sf_node.getparent().get(
            utils.GML_ID)

        simple_fault['id_sf'] = sf_node.get(utils.GML_ID)

        simple_fault['name'] = sf_node.find(
            utils.GML_NAME).text

        simple_fault['tectonic_region'] = sf_node.find(
            utils.TECTONIC_REGION).text

        simple_fault['rake'] = float(sf_node.find(
            utils.RAKE).text)

        simple_fault['truncated_guten_richter'] = \
            self._parse_truncated_guten_richter(sf_node.find(
                    utils.TRUNCATED_GUTEN_RICHTER))

        simple_fault['geometry'] = \
            self._parse_simple_fault_geometry(sf_node.find(
                    utils.SIMPLE_FAULT_GEOMETRY))

        sf_node.clear()

        return simple_fault

    def _parse_simple_fault_geometry(self, geo_node):
        """
        Return a dict structure which contains
        geometry data.
        """

        geometry = {'name': 'geometry'}

        geometry['id_geo'] = geo_node.get(
            utils.GML_ID)

        geometry['fault_trace_pos_list'] = [float(value) for value in
            geo_node.find('.//%s' %
                    utils.POS_LIST).text.split()]

        geometry['dip'] = float(geo_node.find(
            utils.DIP).text)

        geometry['upper_seismogenic_depth'] = float(geo_node.find(
            utils.UPPER_SEISMOGENIC_DEPTH).text)

        geometry['lower_seismogenic_depth'] = float(geo_node.find(
            utils.LOWER_SEISMOGENIC_DEPTH).text)

        geo_node.clear()

        return geometry

    def _parse_complex_fault(self, cf_node):
        """
        Return a complex dict data structure representing
        the parsed complex fault source model, the dict data
        structure also contains a dict and a list respectively:
        evenly_discretized_inc_MFD and complex_fault_geometry
        which itself contains fault_top_edge and fault_bottom_edge
        lists.
        Complex Fault source (cf) complete dict structure description:
            type    - source model type
            id_sm   - source model id
            id_cf   - complex fault id
            name    - complex fault name
            tectonic_region - simple complex tectonic region
            rake    - complex fault rake
            {evenly_discretized_inc_MFD}
            geometry =
                [[fault_top_edge], [fault_bottom_edge]]
        """

        complex_fault = {'type': 'complex_fault'}

        complex_fault['id_sm'] = cf_node.getparent().get(
            utils.GML_ID)

        complex_fault['id_cf'] = cf_node.get(utils.GML_ID)

        complex_fault['name'] = cf_node.find(
            utils.GML_NAME).text

        complex_fault['tectonic_region'] = cf_node.find(
            utils.TECTONIC_REGION).text

        complex_fault['rake'] = float(cf_node.find(
            utils.RAKE).text)

        complex_fault['evenly_discretized_inc_MFD'] = {
            'name': 'evenly_discretized_inc_MFD',

            'bin_size': float(cf_node.find(
            utils.EVENLY_DISCRETIZED_INC_MFD).get(utils.BIN_SIZE)),

            'min_val': float(cf_node.find(
            utils.EVENLY_DISCRETIZED_INC_MFD).get(utils.MIN_VAL)),

            'values': [float(value) for value in cf_node.find(
            utils.EVENLY_DISCRETIZED_INC_MFD).text.split()]}

        fault_bottom_edge, fault_top_edge = self._parse_complex_fault_geometry(
            cf_node.find(utils.COMPLEX_FAULT_GEOMETRY))

        complex_fault['geometry'] = [fault_top_edge, fault_bottom_edge]

        cf_node.clear()

        return complex_fault

    def _parse_complex_fault_geometry(self, geo_node):
        """
        Return two lists which contain fault bottom and top
        edge data.
        """

        fbe_list = [float(value) for value in geo_node.find('.//%s' %
            utils.FAULT_BOTTOM_EDGE).find('.//%s' %
            utils.POS_LIST).text.split()]
        fte_list = [float(value) for value in geo_node.find('.//%s' %
            utils.FAULT_TOP_EDGE).find('.//%s' %
            utils.POS_LIST).text.split()]

        geo_node.clear()

        return fbe_list, fte_list

    def _parse_simple_point(self, sp_node):
        """
        Return a complex dict data structure representing
        the parsed simple point source model, the dict data
        structure also contains two dicts such as:
        rupture_rate_model and rupture_depth_distribution.
        Simple point source (sp) complete dict structure description:
            type    - source model type
            id_sm   - source model id
            id_sp   - simple point id
            tectonic_region - simple point tectonic region
            {location} - simple point location
            rupture_rate_model=
                [   {evenly_discretized_inc_mfd},
                    {focal_mechanism: [nodal_planes]
                        where each nodal plane is {} }
                ]
            {rupture_depth_distribution}
            hypocentral_depth - simple point hypocentral depth
        """
        simple_point = {'type': 'simple_point'}

        simple_point['id_sm'] = sp_node.getparent().get(
            utils.GML_ID)

        simple_point['id_sp'] = sp_node.get(utils.GML_ID)

        simple_point['name'] = sp_node.find(
            utils.GML_NAME).text

        simple_point['tectonic_region'] = sp_node.find(
            utils.TECTONIC_REGION).text

        simple_point['location'] = {
            'name': 'location',
            'srs_name': sp_node.find('.//%s' %
                utils.POINT).get(utils.SRS_NAME),
            'pos': [float(x) for x in sp_node.find(
                './/%s' % utils.POS).text.split()]
        }

        simple_point['rupture_rate_model'] = self._parse_rupture_rate_model(
            sp_node.find(utils.RUPTURE_RATE_MODEL))

        simple_point['rupture_depth_distribution'] = \
                self._parse_rupture_depth_distrib(
                    sp_node.find(utils.RUPTURE_DEPTH_DISTRIB))

        simple_point['hypocentral_depth'] = float(sp_node.find(
            utils.HYPOCENTRAL_DEPTH).text)

        sp_node.clear()

        return simple_point
