#!/usr/bin/env python
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

import __future__

try:
  import numpy as np
except:
  print("numpy is required for testing the vocoder")

import sys
import os
import subprocess

from os.path import join as pjoin

here = os.path.dirname(__file__)

sys.path.insert(0, pjoin(here, '..'))
import vocoder



# Testing raw wrappers

SPTKpath = os.path.abspath(pjoin(here, '../../../tools/SPTK/bin'))
x2x = pjoin(SPTKpath, 'x2x')
mlsacheck = pjoin(SPTKpath, 'mlsacheck')
excite = pjoin(SPTKpath, 'excite')


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

#################################################

if True:
    print("Testing PySPTK_mlsacheck against SPTK")
    # mlsacheck -l $fftlen -c 2 -r 0 -P 5 -m $order -a $alpha

    # SPTK version
    mlsacheck_cmd = x2x + ' +af ' + mcepfile + ' | '
    mlsacheck_cmd += mlsacheck + ' -l {0} -c 2 -r 0 -P 5 -m {1} -a {2} 2> /dev/null | '.format(fftlen, mcep_order, alpha)
    mlsacheck_cmd += x2x + ' +fa%.10f'

    p = subprocess.Popen(mlsacheck_cmd, stdout = subprocess.PIPE, cwd = here, shell = True)
    sptk_stdout = p.stdout.read()
    sptk_stable_mceps = map(float, sptk_stdout.split())


    stable_mceps = vocoder.c_api.PySPTK_mlsacheck(flat_mceps, mcep_order, alpha, fftlen, 2, 0, 5, 0.0)

    if len(stable_mceps) != len(sptk_stable_mceps):
        print("\tFAIL: length mismatch")
        exit(1)

    print("\tPySPTK_mlsacheck: lengths are the same")

    err_count = 0
    for i in range(len(stable_mceps)):
        if abs(sptk_stable_mceps[i] - stable_mceps[i]) > 1e-6:
            err_count += 1

    if err_count:
        print("\tPySPTK_mlsacheck: {0} value(s) mismatched".format(err_count))
        exit(1)

    print("\tPySPTK_mlsacheck: values are the same")

#################################################


print("Testing PySPTK_excite against SPTK")

excite_cmd = "cat {0} | awk -v srate={1} '(NR > 2){{if ($1 > 0) print srate / $1; else print 0.0}}' ".format(f0file, srate)
excite_cmd += ' | ' + x2x + ' +af | '
excite_cmd += excite + ' -p {0} | '.format(int(fperiod))
excite_cmd += x2x + ' +fa%.10f'

p = subprocess.Popen(excite_cmd, stdout = subprocess.PIPE, cwd = here, shell = True)
sptk_stdout = p.stdout.read()
sptk_excitation = map(float, sptk_stdout.split())

periods = srate * np.reciprocal(f0s[2:])
periods[np.isinf(periods)] = 0
periods = np.around(periods, 3) # to match the output of awk
excitation = vocoder.c_api.PySPTK_excite(periods, int(fperiod), 1, False, 1)

if len(excitation) != len(sptk_excitation):
    print("\tFAIL: PySPTK_excite: length mismatch")
    exit(1)
print("\tPySPTK_excite: lengths are the same")

err_count = 0
for i in range(len(excitation)):
    if abs(sptk_excitation[i] - excitation[i]) > 1e-5:
        err_count += 1
        print sptk_excitation[i] , excitation[i]

if err_count:
    print("\tFAIL: PySPTK_excite: {0} value(s) mismatched".format(err_count))
    exit(1)

print("\tPySPTK_excite: values are the same")


#################################################


print("Finished testing vocoder")
