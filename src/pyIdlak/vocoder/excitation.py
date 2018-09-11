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
import math
import random

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


def mixed_excitation(f0s, bndaps, srate = 48000, fshift = 0.005, f0min = 70.,
                     fftlen = 4096, uv_period = None, gauss = True, seed = 0):
    """ Generates mixed excitation

        Generates the excitation by mising a pulse train with
        noise specific to different energy bands

        see. compute-aperiodic-feats.cc for details on the theory
        
        f0s:        list of f0 values
        bndaps:     list of list of bandaps
        srate:      sample rate in Hz
        fshift:     frame shift in seconds
        f0min:      floor f0 to this value
        fftlen:     length of FFT to use (must be pow of 2)
        uv_period:  shift in unvoiced region in seconds (defaults to half fshift)
        gauss:      use normally distributed noise
        seed:       seed for random number generator
    """
    if uv_period is None:
        uv_period = fshift / 2.
    sshift = int(srate * fshift) # frame shift in samples
    noframes = len(f0s)
    nosamples = noframes * sshift
    
    random.seed(seed)
    
    excitation = [0.] * nosamples
    bands = get_band_info(len(bndaps[0]), srate, fshift)
    period_pre = 0
    for sidx, fidx, period, voiced in _pitch_periods(f0s, srate, sshift, f0min, uv_period):
        pmag = float(period)
        fhann = _pitch_sync_hanning(period_pre, period, fftlen)

        if voiced:
            fbndaps = bndaps[fidx]
            fpulse = [0. for t in range(fftlen)] # periodic pulse
            fpulse[fftlen//2] = math.sqrt(pmag)
            fnoise = _gen_noise(pmag, period_pre, period, fftlen, gauss)
            fexc = _excitation_mixing(fpulse, fnoise, fbndaps, srate, bands)
        else:
            fexc = _gen_noise(pmag, period_pre, period, fftlen, gauss)

        frame_excitation = [e*h for (e,h) in zip(fexc, fhann)]
        _overlap_and_add(excitation, frame_excitation, sidx)
        period_pre = period

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


def _pitch_periods(f0s, srate, sshift, f0min, uv_period):
    """ Generator to get frame index, pitch period, and voicing """
    periods = [ 1 / float(max(f0min, f0)) if f0 > 0.0 else uv_period for f0 in f0s ]
    noframes = len(f0s)
    nosmp = (noframes * sshift)
    fidx = 0 # Frame index
    sidx = 0 # Sample index
    while fidx < noframes and sidx < nosmp:
        period_samples = int(srate * periods[fidx])
        yield (sidx, fidx, period_samples, f0s[fidx] > 0.0)
        sidx += period_samples
        while sidx > (fidx + 1) * sshift:
            fidx += 1


def _gen_noise(pmag, period_pre, period, fftlen, gauss):
    """ Generates the appropriate amount of noise at the correct energy """
    s = (fftlen // 2) - (period_pre // 2)
    e = (fftlen // 2 + fftlen % 2) + (period // 2)
    noise = [t > s and t < e for t in range(fftlen)]
    nmag = pmag / (e - s)
    if gauss:
        return [nmag * random.gauss(0,1) if n else 0. for n in noise]
    else:
        return [nmag * random.random() if n else 0. for n in noise]


def _pitch_sync_hanning(period_pre, period, fftlen):
    """ Pitch synchronous hanning window """
    hlen = fftlen // 2
    s = hlen - (period_pre // 2)
    e = hlen + (fftlen % 2) + (period // 2)
    def _hann(n, N):
        return 0.5 * (1. - math.cos(2.0 * math.pi * n / (N - 1.)))
    def _val(f):
        if f < s or f > e:
            return 0.0
        if f < hlen:
            return _hann(f - s, period_pre)
        return _hann(period//2 + (f - hlen), period)
    return [_val(f) for f in range(fftlen)]


def _excitation_mixing(fpulse, fnoise, fbndaps, srate, bands):
    """ Mixing the periodic signal and noise according in a ratio
        defined by the bndaps in the FFT domain
    """
    pulse_fft = list(pyIdlak_vocoder.PyVocoder_FFT(fpulse))
    noise_fft = list(pyIdlak_vocoder.PyVocoder_FFT(fnoise))
    fftlen = len(pulse_fft)

    pre_bcenter = 0
    pre_nweight = None
    for bidx, bcenterfq in enumerate(map(lambda b: b[1], bands)):
        bcenter = int(bcenterfq * fftlen / srate)
        if bidx == len(bands) - 1:
            bcenter = fftlen//2
        bndap = fbndaps[bidx]
        # noise weight needs to be converted from decibels
        nweight = min(1., max(0., math.pow(10., bndap / 20.0)))
        if pre_nweight is None:
            pre_nweight = nweight
        no_fftbins = bcenter - pre_bcenter
        nweight_delta = (nweight - pre_nweight) / no_fftbins
        for i, f in enumerate(range(pre_bcenter, bcenter)):
            nw = (nweight_delta * i) +  pre_nweight
            pw = min(1., max(0., math.sqrt(1 - nw*nw))) # periodic weight
            # FFTs of real signals are symmetric
            pulse_fft[f] *= pw
            noise_fft[f] *= nw
            pulse_fft[-f] *= pw
            noise_fft[-f] *= nw
        pre_bcenter = bcenter
        pre_nweight = nweight

    exc_fft = [p+n for (p,n) in zip(pulse_fft, noise_fft)]
    fexc_complex = pyIdlak_vocoder.PyVocoder_IFFT(exc_fft)
    return [f.real / fftlen for f in fexc_complex]
    

def _overlap_and_add(excitation, frame_excitation, startidx):
    """ Overlap and add the frame's excitation """
    for i, e in enumerate(frame_excitation):
        if startidx + i >= len(excitation):
            break
        excitation[startidx + i] += e


