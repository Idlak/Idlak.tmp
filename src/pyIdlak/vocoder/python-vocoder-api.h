// pyIdlak/python-vocoder-api.h

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

#ifndef KALDI_PYIDLAK_TXP_PYTHON_VOCODER_API_H_
#define KALDI_PYIDLAK_TXP_PYTHON_VOCODER_API_H_

// TODO: Value checking and throwing errors
// TODO: ENUMs as appropriate

/*
excite - generate excitation

  excite generates an excitation sequence from the pitch period information in INPUT,
  and returns the result. When the pitch period is nonzero (i.e. voiced), the excitation
  sequence consists of a pulse train at that pitch. When the pitch period is zero
  (i.e. unvoiced), the excitation sequence consists of Gaussian or Msequence noise.

*/
std::vector<double> PySPTK_excite(const std::vector<double> &INPUT,
                      int frame_period, int interpolation_period, bool gauss, int seed);



/*
mgc2sp - transform mel-generalized cepstrum to spectrum

Please see the documentation at http://sp-tk.sourceforge.net/ for an explation of this
process.

Note that the following options have been removed and set to default:
  "-c" gamma can be set by gamme = 1 / int(c)
  "-u" input can be divided by gamma before being sent to function
*/
std::vector<double> PySPTK_mgc2sp(const std::vector<double> &INPUT,
                      double alpha, double gamma, int order, bool norm_cepstrum, int fftlen,
                      bool output_phase, int output_format);


/*
mlpg -  obtains parameter sequence from PDF sequence

Please see the documentation at http://sp-tk.sourceforge.net/ for an explation of this
process.

The input vector is:
  means_t0, delta means_t0, delta delta means_t0 ... , variance_t0, d variance_t0, dd variance_t0 ...
  means_t1, delta means_t1, delta delta means_t1 ... , variance_t1, d variance_t1, dd variance_t1 ...
  ...

Note that the changes to the following options:
  "-r" has been removed
  "-d" only works with filenames
  "-l" has been removed as order is required instead
*/
std::vector<double> PySPTK_mlpg(const std::vector<double> &INPUT, int order,
                                const std::vector<std::string> &window_filenames, int input_type,
                                int influence_range);


/*
mlsacheck - Check stability of MLSA filter coefficients

Please see the documentation at http://sp-tk.sourceforge.net/ for an explation of this
process.

Pade order can be 4 or 5

if the threshold is 0.0 then it depends on the pade order and stability condition
  r=0,P=4 : R=4.5
  r=1,P=4 : R=6.2
  r=0,P=5 : R=6.0
  r=1,P=5 : R=7.65
*/
std::vector<double> PySPTK_mlsacheck(const std::vector<double> &INPUT, int order,
                                     double all_pass_constant, int fftlen, int check_type,
                                     int stable_condition, int pade_order, double threshold);



/*
mlsadf - MLSA digital filter for speech synthesis

Please see the documentation at http://sp-tk.sourceforge.net/ for an explation of this
process.

Notes:

Pade order can be 4 or 5

if bflag is set output filter coefficient b(m) (coefficients which are linear
transformed from mel-cepstrum)

if nogain is set then the filtering is performed without gain
*/
std::vector<double> PySPTK_mlsadf(const std::vector<double> &MCEPS, const std::vector<double> &EXCITATION,
                                  int order, double all_pass_constant,
                                  int frame_period, int interpolation_period, int pade_order,
                                  bool bflag, bool nogain, bool transpose_filter, bool inverse_filter);


#endif // KALDI_PYIDLAK_TXP_PYTHON_VOCODER_API_H_
