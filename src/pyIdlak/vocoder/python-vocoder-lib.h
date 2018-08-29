// pyIdlak/python-vocode-lib.h

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


// Some useful functions that should not be exposed

#ifndef KALDI_PYIDLAK_TXP_PYTHON_VOCODER_LIB_H_
#define KALDI_PYIDLAK_TXP_PYTHON_VOCODER_LIB_H_

// Replacement for freadf
int vreadf(double *ptr, const int nitems,
           const std::vector<double> &vec, std::vector<double>::const_iterator * pos);

#endif // KALDI_PYIDLAK_TXP_PYTHON_VOCODER_LIB_H_
