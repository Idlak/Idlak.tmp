// pyIdlak/python-vocode-api.h

// Copyright 2018 CereProc Ltd.  (Authors: David Braude
//                                         Matthew Aylett)

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


// This wrapper replicates some SPTK binaries as Python functions
//  The results of which are in flattened arrays. The documentation
//  has been modified from the original SPTK documentation available 
//  at http://sp-tk.sourceforge.net/

#ifndef KALDI_PYIDLAK_TXP_PYTHON_VOCODE_API_H_
#define KALDI_PYIDLAK_TXP_PYTHON_VOCODE_API_H_

/*
excite - generate excitation

  excite generates an excitation sequence from the pitch period information in INPUT,
  and returns the result. When the pitch period is nonzero (i.e. voiced), the excitation
  sequence consists of a pulse train at that pitch. When the pitch period is zero
  (i.e. unvoiced), the excitation sequence consists of Gaussian or Msequence noise.

  Input and output data are in float format.
*/
std::vector<double> PySPTK_excite(const std::vector<double> &INPUT,
                      int frame_period, int interpolation_period, bool gauss, int seed);



/*
mgc2sp - transform mel-generalized cepstrum to spectrum

Please see the documentation at http://sp-tk.sourceforge.net/

Note that the "-c", "-u", and "-o" options have been removed and set to the default
*/
std::vector<double> PySPTK_mgc2sp(const std::vector<double> &INPUT,
                      double alpha, double gamma, int order, bool norm_cepstrum, int fftlen,
                      bool output_phase);


// std::vector<double> PySPTK_mlpg();
// std::vector<double> PySPTK_mlsacheck();
// std::vector<double> PySPTK_mgc2sp();
// std::vector<double> PySPTK_mlsadf();

#endif // KALDI_PYIDLAK_TXP_PYTHON_VOCODE_API_H_
