#!/usr/bin/env python3
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

import unittest

import numpy as np
import sys
import os
import subprocess
import tempfile
import wave

from os.path import join as pjoin

here = os.path.dirname(__file__)

sys.path.insert(0, pjoin(here, '..', '..'))
import pyIdlak
from pyIdlak import vocoder

"""
TODO:
    Test for PySPTK_mgc2sp
    Test for PySPTK_mlpg
"""

# Testing raw wrappers

SPTKpath = os.path.abspath(pjoin(here, '../../../tools/SPTK/bin'))
x2x         = pjoin(SPTKpath, 'x2x')
mlsacheck   = pjoin(SPTKpath, 'mlsacheck')
excite      = pjoin(SPTKpath, 'excite')
mlsadf      = pjoin(SPTKpath, 'mlsadf')

class TestIdlakPythonVocoder(unittest.TestCase):

    alpha = 0.55
    srate = 48000
    fshift = 0.005
    fftlen = 4096
    pade_order = 5

    mcepfile  = pjoin(here, 'testdata', 'test001.mcep')
    f0file    = pjoin(here, 'testdata', 'test001.f0')
    bndapfile = pjoin(here, 'testdata', 'test001.bndap')

    def setUp(self):
        self.fperiod = int(self.fshift * self.srate)
        self.mceps   = np.loadtxt(self.mcepfile)
        self.f0s     = np.loadtxt(self.f0file)
        self.bndaps  = np.loadtxt(self.bndapfile)
        self.mcep_order = self.mceps.shape[1]

    """ Calls to SPTK binaries to making inputs """

    def _make_stable_mceps(self, dirname):
        """ Convert the test mceps into stable mceps """
        mlsacheck_cmd = x2x + ' +af ' + self.mcepfile
        mlsacheck_cmd += ' | ' + mlsacheck + ' -l {0} -c 2 -r 0 -P 5 -m {1} -a {2} 2> /dev/null'.format(self.fftlen, self.mcep_order, self.alpha)
        mlsacheck_cmd += ' | ' + x2x + ' +fa%.6f'
        mlsacheck_cmd += ' > {0}/test.smceps '.format(dirname)
        p = subprocess.Popen(mlsacheck_cmd, cwd = here, shell = True)
        p.wait()
        return '{0}/test.smceps'.format(dirname)


    def _make_pitch_periods(self, dirname):
        pitch_cmd = "cat {0}".format(self.f0file)
        pitch_cmd += " | awk -v srate={0} '(NR > 2){{if ($1 > 0) printf \"%0.6f\\n\", srate / $1; else print 0.0}}' ".format(self.srate)
        pitch_cmd += ' > {0}/test.pperiods '.format(dirname)
        p = subprocess.Popen(pitch_cmd, cwd = here, shell = True)
        p.wait()
        return '{0}/test.pperiods'.format(dirname)


    def _make_sptk_excitation(self, dirname):
        excite_cmd = "cat {0}".format(self.f0file)
        excite_cmd += " | awk -v srate={0} '(NR > 2){{if ($1 > 0) printf \"%0.6f\\n\", srate / $1; else print 0.0}}' ".format(self.srate)
        excite_cmd += ' | ' + x2x + ' +af '
        excite_cmd += ' | ' + excite + ' -p {0} '.format(self.fperiod)
        excite_cmd += ' | ' + x2x + ' +fa%.6f '
        excite_cmd += ' > {0}/test.exc '.format(dirname)
        p = subprocess.Popen(excite_cmd, cwd = here, shell = True)
        p.wait()
        return '{0}/test.exc'.format(dirname)


    def _sptk_to_float(self, filename):
        """ Use SPTK to convert to floating point format """
        float_cmd = x2x + ' +af {0} > {0}.float'.format(filename)
        p = subprocess.Popen(float_cmd, cwd = here, shell = True)
        p.wait()
        return '{0}.float'.format(filename)


    """ Test cases start here """

    def test_PySPTK_mlsacheck(self):
        """ Wrapper of SPTK mlsacheck binary """
        with tempfile.TemporaryDirectory() as testdir:
            smcepsfile = self._make_stable_mceps(testdir)
            sptk_stable_mceps = np.loadtxt(smcepsfile)
            idlak_stable_mceps = vocoder.c_api.PySPTK_mlsacheck(
                            self.mceps.flatten(),
                            self.mcep_order,
                            self.alpha,
                            self.fftlen,
                            2,
                            0,
                            self.pade_order,
                            0.0,
                            True)
            self.assertEqual(len(sptk_stable_mceps), len(idlak_stable_mceps),
                             "lengths are not equal")
            for sptk_val, idlak_val in zip(sptk_stable_mceps, idlak_stable_mceps):
                self.assertAlmostEqual(sptk_val, idlak_val,
                             delta = 1e-6, msg = "values are not the same")


    def test_PySPTK_excite(self):
        """ Wrapper of SPTK excite binary """
        with tempfile.TemporaryDirectory() as testdir:
            pperiodsfile = self._make_pitch_periods(testdir)
            excitationfile = '{0}/test.exc'.format(testdir)
            excite_cmd = 'cat {0} '.format(pperiodsfile)
            excite_cmd += ' | ' + x2x + ' +af '
            excite_cmd += ' | ' + excite + ' -p {0} '.format(self.fperiod)
            excite_cmd += ' | ' + x2x + ' +fa%.6f '
            excite_cmd += ' > {0}'.format(excitationfile)
            p = subprocess.Popen(excite_cmd, cwd = here, shell = True)
            p.wait()
            sptk_excite = np.loadtxt(excitationfile)

            periods = np.loadtxt(pperiodsfile).tolist()
            idlak_excite = vocoder.c_api.PySPTK_excite(periods, self.fperiod, 1, False, 1)
            self.assertEqual(len(sptk_excite), len(idlak_excite),
                             "lengths are not equal")
            for sptk_val, idlak_val in zip(sptk_excite, idlak_excite):
                # excluded the unvoiced regions
                if not(abs(sptk_val) == 1 and abs(idlak_val) == 1):
                    self.assertAlmostEqual(sptk_val, idlak_val,
                                delta = 1e-3, msg = "values are not the same")


    def test_PySPTK_mlsadf(self):
        """ Wrapper of SPTK mlsadf binary """
        with tempfile.TemporaryDirectory() as testdir:
            smcepsfile = self._make_stable_mceps(testdir)
            smcepsfloat = self._sptk_to_float(smcepsfile)

            excfile = self._make_sptk_excitation(testdir)
            excfloat = self._sptk_to_float(excfile)

            sptk_waveformfile = '{0}/test.syn'.format(testdir)
            mlsadf_cmd = mlsadf + ' -P 5 -m {0} -a {1} -p {2} {3} < {4} '.format(
                    self.mcep_order, self.alpha, self.fperiod, smcepsfloat, excfloat)
            mlsadf_cmd += ' | ' + x2x + ' +fa%.6f '
            mlsadf_cmd += ' > {0} '.format(sptk_waveformfile)
            p = subprocess.Popen(mlsadf_cmd, cwd = here, shell = True)
            p.wait()
            sptk_waveform = np.loadtxt(sptk_waveformfile)

            sptk_excite = np.loadtxt(excfile)
            sptk_smceps = np.loadtxt(smcepsfile).flatten()
            idlak_waveform = vocoder.c_api.PySPTK_mlsadf(sptk_smceps, sptk_excite,
                                                         self.mcep_order,
                                                         self.alpha,
                                                         self.fperiod,
                                                         1,
                                                         self.pade_order,
                                                         False, False, False, False)

            self.assertEqual(len(sptk_waveform), len(idlak_waveform),
                             "lengths are not equal")
            for sptk_val, idlak_val in zip(sptk_waveform, idlak_waveform):
                self.assertAlmostEqual(sptk_val, idlak_val,
                             places = 1, msg = "values are not the same")


    def test_MCEPVocoder(self):
        with tempfile.TemporaryDirectory() as testdir:
            mcep_voc = vocoder.MCEPVocoder()
            f0s    = self.f0s.tolist()[2:] # To match SPTK
            mceps  = self.mceps.tolist()
            bndaps = self.bndaps.tolist()

            no_frames = min([len(mceps), len(f0s), len(bndaps)]) - 1
            no_samples = int(no_frames * self.fshift * self.srate)

            # Basic Vocoding
            wavfile = pjoin(testdir, 'test.wav')
            mcep_voc.apply_mlsa(mceps, mcep_voc.gen_excitation(f0s))
            mcep_voc.to_wav(wavfile)
            self.assertTrue(os.path.isfile(wavfile),
                            "output file not created")

            with wave.open(wavfile, 'rb') as testwav:
                self.assertEqual(testwav.getnframes(), no_samples,
                                 "number of samples mismatch")
                waveform = [x for x in testwav.readframes(no_samples)]
                rms = np.sqrt(np.mean(np.square(waveform)))
                self.assertGreater(rms, 0.0,
                                   "Waveform seems to be silent")


if __name__ == '__main__':
    unittest.main()
