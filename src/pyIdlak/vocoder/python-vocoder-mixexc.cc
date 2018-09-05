// pyIdlak/vocoder/python-vocode-mixexc.cc

// Copyright 2018 CereProc Ltd.  (Authors: David Braude)


// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//  http://www.apache.org/licenses/LICENSE-2.0
//
// THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
// WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
// MERCHANTABLITY OR NON-INFRINGEMENT.
// See the Apache 2 License for the specific language governing permissions and
// limitations under the License.
//

// Mixed excitation functions


#include "idlakfeat/feature-aperiodic.h"
#include "pyIdlak/pylib/pyIdlak_internal.h"

#include "python-vocoder-api.h"
#include "python-vocoder-lib.h"


std::vector<double> PyVocoder_get_aperiodic_band_starts(PySimpleOptions * pyopts) {
    std::vector<double> band_starts;
    kaldi::AperiodicEnergyOptions *opts = static_cast<kaldi::AperiodicEnergyOptions*>(pyopts->opts_);
    kaldi::AperiodicEnergy ap_energy(*opts);

    int nobands = ap_energy.Dim();
    for (int i = 0; i < nobands; i++)
        band_starts.push_back(static_cast<double>(ap_energy.GetBandStarts()(i)));

    return band_starts;
}


std::vector<double> PyVocoder_get_aperiodic_band_centers(PySimpleOptions * pyopts) {
    std::vector<double> band_centers;
    kaldi::AperiodicEnergyOptions *opts = static_cast<kaldi::AperiodicEnergyOptions*>(pyopts->opts_);
    kaldi::AperiodicEnergy ap_energy(*opts);

    int nobands = ap_energy.Dim();
    for (int i = 0; i < nobands; i++)
        band_centers.push_back(static_cast<double>(ap_energy.GetBandCenters()(i)));

    return band_centers;
}


std::vector<double> PyVocoder_get_aperiodic_band_ends(PySimpleOptions * pyopts) {
    std::vector<double> band_ends;
    kaldi::AperiodicEnergyOptions *opts = static_cast<kaldi::AperiodicEnergyOptions*>(pyopts->opts_);
    kaldi::AperiodicEnergy ap_energy(*opts);

    int nobands = ap_energy.Dim();
    for (int i = 0; i < nobands; i++)
        band_ends.push_back(static_cast<double>(ap_energy.GetBandEnds()(i)));

    return band_ends;
}