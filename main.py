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


from mtoolkit.console import cmd_line
from mtoolkit.workflow import Context, PipeLineBuilder


if __name__ == '__main__':
    INPUT_CONFIG_FILENAME = cmd_line()
    if INPUT_CONFIG_FILENAME != None:
        CONTEXT = Context(INPUT_CONFIG_FILENAME)
        PIPELINE = PipeLineBuilder("test pipeline").build(
                CONTEXT.config)
        PIPELINE.run(CONTEXT)

        print CONTEXT.vcl
        print CONTEXT.vmain_shock
        print CONTEXT.flag_vector
