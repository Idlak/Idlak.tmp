# -*- coding: utf-8 -*-
# Copyright 2018 Cereproc Ltd. (author: David Braude)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License.

# Excitation functions

from . import pyIdlak_vocoder
from .. import pylib

def SPTK_excitation(f0s, srate = 48000, fshift = 0.005, iperiod = 1, gauss = False, seed = 1):
    """ Generates Excitation Using F0s and SPTK

        srate:      sample rate in Hz (int)
        fshift:     frame shift in seconds (float)
        iperiod:    interpolation period (int)
        gauss:      use Gaussian noise (bool)
        seed:       randomisation seed (int)
    """
    srate = int(srate)
    fshift = float(fshift)
    fperiod = int(srate * fshift)
    iperiod = int(iperiod)
    gauss = bool(gauss)
    seed = int(seed)
    periods = [ srate / float(f0) if f0 > 0.0 else 0.0  for f0 in f0s ]
    excitation = pyIdlak_vocoder.PySPTK_excite(periods, fperiod, iperiod, gauss, seed)
    return excitation


def mixed_excitation(f0s, bndaps, srate = 48000, fshift = 0.005, seed = 1):
    """ Generates mixed excitation

        Generates the excitation by mising a pulse train with
        noise specific to different energy bands

        see. compute-aperiodic-feats.cc for details on the theory
    """
    bands = get_band_info(len(bndaps[0]), srate, fshift)


    excitation = []
    return excitation



def get_band_info(numbands, srate, fshift, **kwargs):
    """ Figure out where the Bands need to be

        Returns a list of tuples in Hz of (start, center, end)
    """
    opts = pylib.PyOptions(pylib.AperiodicEnergyOptions)
    kwargs['sample-frequency'] = float(srate)
    kwargs['frame-shift'] = float(fshift)
    kwargs['num-mel-bins'] = float(numbands)

    for k, v in kwargs.items():
        kw = k.replace('_', '-')
        if kw in opts.options:
            opts.set(kw, v)
        else:
            raise TypeError("get_band_info() got an unexpected keyword argument '{0}'".format(k))

    band_starts  = pyIdlak_vocoder.PyVocoder_get_aperiodic_band_starts(opts.kaldiopts)
    band_centers = pyIdlak_vocoder.PyVocoder_get_aperiodic_band_centers(opts.kaldiopts)
    band_ends    = pyIdlak_vocoder.PyVocoder_get_aperiodic_band_ends(opts.kaldiopts)
    return list(zip(band_starts, band_centers, band_ends))







