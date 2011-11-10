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

"""Module which implements completeness algorithms"""


import numpy as np


def stepp_analysis(year, mw, dm=0.1, dt=1, ttol=0.2, iloc=True):
    """
    Stepp function
    Year    = Year of earthquake
    M       = Magnitude (Mw)
    dM      = Magnitude interval
    dT      = time interval
    ttol    = Tolerance threshold
    iloc    = Fix analysis such that completeness magnitude
              can only increase with catalogue duration
              (i.e. completess cannot increase for more
               recent catalogues)
    """

    # Round off the magnitudes to 2 d.p
    mw = np.around(100.0 * mw) / 100.0
    lowm = np.floor(10. * np.min(mw)) / 10.
    highm = np.ceil(10. * np.max(mw)) / 10.
    # Determine magnitude bins
    mbin = np.arange(lowm, highm + dm, dm)
    ntb = np.max(np.shape(mbin))
    # Determine time bins
    endT = np.max(year)
    startT = np.min(year)
    T = np.arange(dt, endT - startT + 2, dt)
    #T = np.vstack([np.arange(dt, endT - startT, dt)[:, np.newaxis], endT])
    nt = np.max(np.shape(T))
    TUB = endT * np.ones(nt)
    TLB = TUB - T
    TRT = 1. / np.sqrt(T)  # Poisson rate

    N = np.zeros((nt, ntb - 1))
    lamda = np.zeros((nt, ntb - 1))
    siglam = np.zeros((nt, ntb - 1))
    ii = 0
    # count number of events catalogue and magnitude windows
    while ii <= (nt - 1):
    # Select earthquakes later than or in Year[ii]
        yrchk = year >= TLB[ii]
        mtmp = mw[yrchk]
        jj = 0
        while jj <= (ntb - 2):
            #Count earthquakes in magnitude bin
            if jj == (ntb - 2):
                N[ii, jj] = np.sum(mtmp >= np.sum(mbin[jj]))
            else:
                N[ii, jj] = np.sum(np.logical_and(mtmp >= mbin[jj],
                                           mtmp < mbin[jj + 1]))
            jj = jj + 1
        ii = ii + 1

    diffT = (np.log10(TRT[1:]) - np.log10(TRT[:-1]))
    diffT = diffT / (np.log10(T[1:]) - np.log10(T[:-1]))
    comp_length = np.zeros((ntb - 1, 1))
    tloc = np.zeros((ntb - 1, 1), dtype=int)
    ii = 0
    while ii < (ntb - 1):
        lamda[:, ii] = N[:, ii] / T
        siglam[:, ii] = np.sqrt(lamda[:, ii] / T)
        zero_find = siglam[:, ii] < 1E-14   # To avoid divide by zero
        siglam[zero_find, ii] = 1E-14
        #print siglam[:, ii]
        grad1 = (np.log10(siglam[1:, ii]) - np.log10(siglam[:-1, ii]))
        grad1 = grad1 / (np.log10(T[1:]) - np.log10(T[:-1]))
        resid1 = grad1 - diffT
        test1 = np.abs(resid1[1:] - resid1[:-1])
        tloct = np.nonzero(test1 > ttol)[0]
        if not(np.any(tloct)):
            tloct = -1
        else:
            tloct = tloct[-1]
        if tloct < 0:
            # No location passes test
            if ii > 0:
                # Use previous value
                tloc[ii] = tloc[ii - 1]
            else:
                # Print warning
                print "Fitting tolerance removed all data - change parameter"
        else:
            tloc[ii] = tloct
        if tloct > np.max(np.shape(T)):
            tloc[ii] = np.max(np.shape(T))

        if ii > 0:
            # If the increasing completeness is option is set
            # and the completeness is lower than the previous value
            # then fix at previous value
            inc_check = np.logical_and(iloc, (tloc[ii] < tloc[ii - 1]))
            if inc_check:
                tloc[ii] = tloc[ii - 1]
        comp_length[ii] = T[tloc[ii]]

        ii = ii + 1

    completeness_table = np.column_stack([mbin[:-1].T, endT - comp_length])

    return completeness_table
