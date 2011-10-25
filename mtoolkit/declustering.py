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

'''Module to implement declustering algorithms'''

import numpy as np
from mtoolkit.catalogue_utilities import decimal_year, haversine


# Choose Calculate Magnitude and Distance Windows (for Gardner & Knopoff)
def calc_windows(m, window_opt):
    """Function to calculate time and distance windows according \
    to the methods of "Gruenthal", "Uhrhammer" or "GardnerKnopoff"""
    if window_opt == 'Gruenthal':
        # Gruenthal
        f_space = np.exp(1.77 + np.sqrt(0.037 + 1.02 * m))
        f_time = np.abs((np.exp(-3.95 + np.sqrt(0.62 + 17.32 * m))) / 365.)
        f_time[m >= 6.5] = np.power(10, 2.8 + 0.024 * m[m >= 6.5]) / 365.
    elif window_opt == 'Uhrhammer':
        # Uhrhammer
        f_space = np.exp(-1.024 + 0.804 * m)
        f_time = np.exp(-2.87 + 1.235 * m / 365.)
    else:
        #Gardner & Knopoff
        f_space = np.power(10.0, 0.1238 * m + 0.983)
        f_time = np.power(10.0, 0.032 * m + 2.7389) / 365.
        f_time[m < 6.5] = np.power(10.0, 0.5409 * m[m < 6.5] - 0.547) / 365.
    return f_space, f_time


def gardner_knopoff_decluster(
    data, window_opt='GardnerKnopoff', fs_time_prop=0):
    ''' Function to implement Gardner & Knopoff Declustering Algorithm
        data = EQ catalogue in sample format
        WindowOpt = 'GardnerKnopoff' for Gardner & Knopoff windows
                              'Uhrhammer' for 'Uhrhammer' implementation
                              'Gruenthal' for Gruenthal implementation
        FSTimeProp = Foreshock time window as a proportion of aftershock
                              time window '''

    #~ #Define reference ellipsoid for geospatial calculations
    #~ ref_geoid = Geod(ellps="WGS84")

    # Get relevent parameters
    m = data[:, 5]
    neq = np.shape(data)[0]  # Number of earthquakes
    # Get decimal year (needed for time windows)
    year_dec = decimal_year(data[:, 0], data[:, 1], data[:, 2])
    # Get space and time windows corresponding to each event
    f_space, f_time = calc_windows(m, window_opt)
    eqid = np.arange(0, neq, 1)  # Initial Position Identifier

    # Pre-allocate cluster index vectors
    vcl = np.zeros(neq, dtype=int)

    # Sort magnitudes into descending order
    id0 = np.flipud(np.argsort(m, kind='heapsort'))
    m = m[id0]
    data = data[id0, :]
    f_space = f_space[id0]
    f_time = f_time[id0]
    year_dec = year_dec[id0]
    eqid = eqid[id0]
    #Begin cluster identification
    i = 0
    while i < neq:
        if vcl[i] == 0:
            #fMag = m[i]
            #mPos = data[i, 10:11]

            # Find Events inside both fore- and aftershock time windows
            dt = year_dec - year_dec[i]
            ick = np.zeros(neq, dtype=int)
            vsel = np.logical_and(dt >= (-f_time[i] * fs_time_prop),
                                              dt <= f_time[i], vcl == 0)
            # Of those events inside time window, find those inside distance
            # window
            vsel1 = haversine(data[vsel, 3], data[vsel, 4], data[i, 3],
                               data[i, 4]) <= f_space[i]
            # Update logical array so that those events inside time window
            # but outside distance window are switched to False
            vsel[vsel] = vsel1
            # Allocate a cluster number
            vcl[vsel] = i + 1
            ick[vsel] = i + 1
            # Number of elements in cluster
            #nCl = np.max(np.shape(np.nonzero(ick != 0)[0]))
            ick[i] = 0  # Remove mainshock from cluster
            # Indicate the foreshocks
            tempick = ick[vsel]
            id2 = year_dec[vsel] < year_dec[i]
            tempick[id2] = -1 * (i + 1)
            vcl[vsel] = tempick

            # vcl indicates the cluster to which an event belongs
            # +vcl = aftershock, -vcl = foreshock
            i += 1
        else:
            # Already allocated to cluster - skip event
            i += 1

    # Re-sort the data into original order
    id1 = np.argsort(eqid, kind='heapsort')
    eqid = eqid[id1]
    data = data[id1, :]
    vcl = vcl[id1]
    # Now to produce a catalogue with aftershocks purged
    vmain_shock = data[np.nonzero(vcl == 0)[0], :]
    # Also create a simple flag vector which, for each event, takes
    # a value of 1 if aftershock, -1 if foreshock, and 0 otherwise
    flagvector = np.copy(vcl)
    flagvector[vcl < 0] = -1
    flagvector[vcl > 0] = 1

    return vcl, vmain_shock, flagvector
