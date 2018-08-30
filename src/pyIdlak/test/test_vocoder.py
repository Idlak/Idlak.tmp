#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 Cereproc Ltd. (author: Matthew Aylett
#                                       David Braude)
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

import numpy as np
import sys
import os
import subprocess
import tempfile

from os.path import join as pjoin

here = os.path.dirname(__file__)

sys.path.insert(0, pjoin(here, '..'))
import vocoder

"""
TODO:
    Switch to proper unittest module
    Test for PySPTK_mgc2sp
    Test for PySPTK_mlpg
"""

# Testing raw wrappers

SPTKpath = os.path.abspath(pjoin(here, '../../../tools/SPTK/bin'))
x2x = pjoin(SPTKpath, 'x2x')
mlsacheck = pjoin(SPTKpath, 'mlsacheck')
excite = pjoin(SPTKpath, 'excite')
mlsadf = pjoin(SPTKpath, 'mlsadf')

mcepfile = pjoin(here, 'test001.mcep')
f0file = pjoin(here, 'test001.f0')
bndapfile = pjoin(here, 'test001.bndap')

mceps = np.loadtxt(mcepfile)
f0s = np.loadtxt(f0file)

mcep_order = mceps.shape[1]
alpha = 0.55
srate = 48000
fftlen = 4096
fshift = 0.005


fperiod = fshift * srate
flat_mceps = mceps.flatten()


#################################
# Functions for creating inputs #
#################################

def make_stable_mceps(dirname):
    """ Convert the test mceps into stable mceps """
    mlsacheck_cmd = x2x + ' +af ' + mcepfile
    mlsacheck_cmd += ' | ' + mlsacheck + ' -l {0} -c 2 -r 0 -P 5 -m {1} -a {2} 2> /dev/null'.format(fftlen, mcep_order, alpha)
    mlsacheck_cmd += ' | ' + x2x + ' +fa%.10f'
    mlsacheck_cmd += ' > {0}/test.smceps '.format(dirname)
    p = subprocess.Popen(mlsacheck_cmd, cwd = here, shell = True)
    p.wait()
    return '{0}/test.smceps'.format(dirname)


def make_sptk_excitation(dirname):
    """ Create an SPTK only excitation """
    excite_cmd = "cat {0} | awk -v srate={1} '(NR > 2){{if ($1 > 0) print srate / $1; else print 0.0}}' ".format(f0file, srate)
    excite_cmd += ' | ' + x2x + ' +af '
    excite_cmd += ' | ' + excite + ' -p {0} '.format(int(fperiod))
    excite_cmd += ' | ' + x2x + ' +fa%.10f '
    excite_cmd += ' > {0}/test.exc '.format(dirname)
    p = subprocess.Popen(excite_cmd, cwd = here, shell = True)
    p.wait()
    return '{0}/test.exc'.format(dirname)


def sptk_to_float(filename):
    """ Use SPTK to convert to floating point format """
    float_cmd = x2x + ' +af {filename} > {filename}.float'.format(filename = filename)
    p = subprocess.Popen(float_cmd, cwd = here, shell = True)
    p.wait()
    return '{filename}.float'.format(filename = filename)


#################################
# SPTK Wrapper Tests            #
#################################

if True:
    print("PySPTK_mlsacheck ... ", end='', flush=True)
    mlsacheck_cmd = x2x + ' +af ' + mcepfile + ' | '
    mlsacheck_cmd += mlsacheck + ' -l {0} -c 2 -r 0 -P 5 -m {1} -a {2} 2> /dev/null | '.format(fftlen, mcep_order, alpha)
    mlsacheck_cmd += x2x + ' +fa%.10f'

    p = subprocess.Popen(mlsacheck_cmd, stdout = subprocess.PIPE, cwd = here, shell = True)
    sptk_stdout = p.stdout.read()
    sptk_stable_mceps = [float(x) for x in sptk_stdout.split()]

    stable_mceps = vocoder.c_api.PySPTK_mlsacheck(flat_mceps, mcep_order, alpha, fftlen, 2, 0, 5, 0.0, True)

    if len(stable_mceps) != len(sptk_stable_mceps):
        print("\t[ FAIL ] length mismatch")
    else:
        err_count = 0
        for i in range(len(stable_mceps)):
            if abs(sptk_stable_mceps[i] - stable_mceps[i]) > 1e-6:
                err_count += 1
        if err_count:
            print("\t[ FAIL ] {0} value(s) mismatched".format(err_count))
        else:
            print("\t[  OK  ]")

#################################################

if False:
    print("PySPTK_excite    ... ", end='', flush=True)
    excite_cmd = "cat {0} | awk -v srate={1} '(NR > 2){{if ($1 > 0) print srate / $1; else print 0.0}}' ".format(f0file, srate)
    excite_cmd += ' | ' + x2x + ' +af | '
    excite_cmd += excite + ' -p {0} | '.format(int(fperiod))
    excite_cmd += x2x + ' +fa%.10f'

    p = subprocess.Popen(excite_cmd, stdout = subprocess.PIPE, cwd = here, shell = True)
    sptk_stdout = p.stdout.read()
    sptk_excitation = [float(x) for x in sptk_stdout.split()]

    periods = srate * np.reciprocal(f0s[2:])
    periods[np.isinf(periods)] = 0
    periods = np.around(periods, 3) # to match the output of awk
    excitation = vocoder.c_api.PySPTK_excite(periods, int(fperiod), 1, False, 1)

    if len(excitation) != len(sptk_excitation):
        print("\t[ FAIL ] length mismatch")
    else:
        err_count = 0
        for i in range(len(excitation)):
            if abs(sptk_excitation[i] - excitation[i]) > 1e-3:
                err_count += 1
        if err_count:
            print("\t[ FAIL ] {0} value(s) mismatched".format(err_count))
        else:
            print("\t[  OK  ]")



#################################################

if False:
    print("PySPTK_mlsadf    ... ", end='', flush=True)
    with tempfile.TemporaryDirectory() as testdir:
        # Make required files so that inputs are the same
        smcepsfile = make_stable_mceps(testdir)
        smcepsfloat = sptk_to_float(smcepsfile)

        excfile = make_sptk_excitation(testdir)
        excfloat = sptk_to_float(excfile)

        mlsadf_cmd = mlsadf + ' -P 5 -m {0} -a {1} -p {2} {3} < {4} '.format(
                mcep_order, alpha, int(fperiod), smcepsfloat, excfloat )
        mlsadf_cmd += ' | ' + x2x + ' +fa%.10f '
        p = subprocess.Popen(mlsadf_cmd, stdout = subprocess.PIPE, cwd = here, shell = True)
        sptk_stdout = p.stdout.read()
        sptk_waveform = [float(x) for x in sptk_stdout.split()]

        excitation = np.loadtxt(excfile).flatten()
        smceps = np.loadtxt(smcepsfile).flatten()
        waveform = vocoder.c_api.PySPTK_mlsadf(smceps, excitation, mcep_order, alpha, int(fperiod), 1, 5, False, False, False, False)

        if len(waveform) != len(sptk_waveform):
            print("\t[ FAIL ] length mismatch")
        else:
            err_count = 0
            for i in range(len(waveform)):
                if abs(sptk_waveform[i] - waveform[i]) > 1e-3:
                    err_count += 1
            if err_count:
                print("\t[ FAIL ] {0} value(s) mismatched".format(err_count))
            else:
                print("\t[  OK  ]")


#################################
# Python Vocoder Tests          #
#################################

print("MCEPVocoder    ... ", end='', flush=True)
mcep_voc = vocoder.MCEPVocoder()
f0s = np.loadtxt(f0file).tolist()
mceps = np.loadtxt(mcepfile).tolist()

mcep_voc.vocode_mlsa(mceps, mcep_voc.gen_excitation(f0s))
mcep_voc.to_wav('test.wav')


print("\t[  OK  ]")


print("Finished testing vocoder")
