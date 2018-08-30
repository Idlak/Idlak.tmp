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

import enum
import wave
import struct
from . import pyIdlak_vocoder
from . import excitation



class Vocoder():
    """ Contains common io operations and required properties """

    def __init__(self, srate = 48000):
        self.set_srate(srate)
        self._waveform = None


    def set_srate(self, srate):
        """ Sets the sample rate of the vocoder """
        srate = int(srate)
        if srate <= 0:
            raise ValueError("sample rate must be a positive integer")
        self._srate = srate


    def to_wav(self, wavfn):
        """ Save the vocoded waveform into a file,

            Uses wave from the Python standard library,
            raises ValueError if the wave form has not been
            created yet.
        """
        if self._waveform is None:
            raise ValueError('No waveform to save')

        wav = wave.open(wavfn, 'wb')
        wav.setnchannels(1)
        wav.setsampwidth(2) # always using signed integer output
        wav.setframerate(self.srate)
        for w in self._waveform:
            wout = max(min(int(w), 32000), -32000) # ensures in range
            write_data = struct.pack("<h", int(w))
            wav.writeframes(write_data)

        wav.close()

    @property
    def srate(self):
        return self._srate


class MCEPExcitation(enum.Enum):
    AUTO = 0
    SPTK = 1


class MCEPVocoder(Vocoder):
    """  Vocoder for MCEP features """

    def __init__(self, srate = 48000, order = 60, alpha = 0.55, fftlen = 4096,
                 fshift = 0.005, pade_order = 5):
        super().__init__(srate = srate)
        self.set_order(order)
        self.set_alpha(alpha)
        self.set_fftlen(fftlen)
        self.set_fshift(fshift)
        self.set_pade_order(pade_order)

        # These values never really need to change but are here to be
        # overridden if you want but are here to be overridden if you want to
        # run some experiments

        # Excitation
        self.iperiod = 1
        self.gauss = False
        self.seed = 1

        # Stablisation
        self.quiet_stablisation = True
        self.stable_condition = 0
        self.stability_threshold = 0.0 # auto

        # MLSA
        self.save_bcoeffs = False
        self.no_gain = False
        self.transpose_filter = False
        self.inverse_filter = False


    def vocode_mlsa(self, mceps, excite, stablise_mceps = True):
        """ Takes the mceps and vocodes them using the given excitation """

        flat_mceps = []
        for idx, mframe in enumerate(mceps):
            if not len(mframe) == self.order + 1:
                raise ValueError(
                    "frame {0} is not of order {1} + gain".format(
                        idx, self.order))
            flat_mceps.extend([float(x) for x in mframe])

        if stablise_mceps:
            smceps = pyIdlak_vocoder.PySPTK_mlsacheck(
                flat_mceps, self.order, self.alpha, self.fftlen, 2,
                self.stable_condition, self.pade_order,
                self.stability_threshold, self.quiet_stablisation)
        else:
            smceps = flat_mceps

        fperiod = int(self.srate * self.fshift)
        self._waveform = pyIdlak_vocoder.PySPTK_mlsadf(
            smceps, excite, self.order, self.alpha, fperiod, self.iperiod,
            self.pade_order, self.save_bcoeffs, self.no_gain,
            self.transpose_filter, self.inverse_filter)

        return self._waveform


    def gen_excitation(self, f0s, bndaps = None,
                       exc_type = MCEPExcitation.AUTO):
        """ Generates an excitation signal for use with an MCEP vocoder """
        if exc_type == MCEPExcitation.AUTO:
            if bndaps is None:
                exc_type = MCEPExcitation.SPTK
            else:
                # If it can't find anything else use SPTK
                exc_type = MCEPExcitation.SPTK

        if exc_type == MCEPExcitation.SPTK:
            exc = excitation.SPTK_excitation(f0s, self.srate, self.fshift,
                                             self.iperiod, self.gauss,
                                             self.seed)

        return exc


    def set_order(self, order):
        """ Set the MCEP Order """
        order = int(order)
        if order <= 0:
            raise ValueError("MCEP order must be a positive integer")
        self._order = order

    def set_alpha(self, alpha):
        """ Set the all pass constant value """
        alpha = float(alpha)
        self._alpha = alpha

    def set_fftlen(self, fftlen):
        """ Set the FFT length """
        fftlen = int(fftlen)
        if fftlen <= 0:
            raise ValueError("FFT length must be a positive integer")
        self._fftlen = fftlen

    def set_fshift(self, fshift):
        """ Set the frame shift """
        fshift = float(fshift)
        if fshift <= 0:
            raise ValueError("Frame shift must be positive")
        self._fshift = fshift

    def set_pade_order(self, pade_order):
        """ Set the order for the pade approximation """
        pade_order = int(pade_order)
        if pade_order not in [4, 5]:
            raise ValueError("Pade order not supported use 4 or 5")
        self._pade = pade_order

    @property
    def order(self):
        return self._order

    @property
    def alpha(self):
        return self._alpha

    @property
    def fftlen(self):
        return self._fftlen

    @property
    def fshift(self):
        return self._fshift

    @property
    def pade_order(self):
        return self._pade

