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
The purpose of this module is to provide constants,
and some utilities: function and exception to deal
with nrml (xml file format).
"""

from lxml import etree

NRML_NS = 'http://openquake.org/xmlns/nrml/0.2'
GML_NS = 'http://www.opengis.net/gml'
QUAKEML_NS = 'http://quakeml.org/xmlns/quakeml/1.1'

NRML = "{%s}" % NRML_NS
GML = "{%s}" % GML_NS
QUAKEML = "{%s}" % QUAKEML_NS

NSMAP = {None: NRML_NS, "gml": GML_NS}
NSMAP_WITH_QUAKEML = {None: NRML_NS, "gml": GML_NS, "qml": QUAKEML_NS}

SOURCE_MODEL_ID_ATTR = "%sid" % GML
AREA_SOURCE = "%sareaSource" % NRML
AREA_SOURCE_ID = "%sid" % GML
GML_NAME = "%sname" % GML
TECTONIC_REGION = "%stectonicRegion" % NRML

AREA_BOUNDARY = "%sareaBoundary" % NRML
A_BOUNDARY_POS_LIST = "%sposList" % GML

RUPTURE_RATE_MODEL = "%sruptureRateModel" % NRML
A_VALUE_CUMULATIVE = "%saValueCumulative" % NRML
B_VALUE = "%sbValue" % NRML
MIN_MAGNITUDE = "%sminMagnitude" % NRML
MAX_MAGNITUDE = "%smaxMagnitude" % NRML
FOCAL_MECHANISM = "%sfocalMechanism" % NRML
FM_ID_ATTR = "publicID"
NODAL_PLANES = "%snodalPlanes" % QUAKEML
NODAL_PLANE_STRIKE = "%sstrike" % QUAKEML
NODAL_PLANE_DIP = "%sdip" % QUAKEML
NODAL_PLANE_RAKE = "%srake" % QUAKEML

RUPTURE_DEPTH_DISTRIB = "%sruptureDepthDistribution" % NRML
MAGNITUDE = "%smagnitude" % NRML
DEPTH = "%sdepth" % NRML

HYPOCENTRAL_DEPTH = "%shypocentralDepth" % NRML


class XMLValidationError(Exception):
    """XML schema validation error"""

    def __init__(self, filename, message):
        """Constructs a new validation exception for the given file name"""
        Exception.__init__(self, message)
        self.args = (filename, message)
        self.filename = filename
        self.message = message


def valid_schema(source_model_path, schema_path):
    """Check if the xml is conform to the schema provided"""
    xml_doc = etree.parse(source_model_path)
    xmlschema = etree.XMLSchema(etree.parse(schema_path))
    return xmlschema.validate(xml_doc)
