// pyIdlak/pylib/pyIdlak_typemaps.i

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


// Note that this is intended to ensure all compiled moduoles use the same typemaps

%include <std_string.i>
%include <std_vector.i>
%include <argcargv.i>
%include <std_complex.i>
%include <typemaps.i>

namespace std {
   %template(IntVector) vector<int>;
   %template(DoubleVector) vector<double>;
   %template(ComplexDoubleVector) vector<std::complex<double>>;
   %template(StringVector) vector<string>;
   %template(ConstCharVector) vector<const char*>;
};

%apply (int ARGC, char **ARGV) { (int argc, char *argv[]) }

%{
#include "matrix/matrix-lib.h"
typedef kaldi::Matrix<kaldi::BaseFloat> KaldiMatrixWrap_BaseFloat;
typedef kaldi::Matrix<double> KaldiMatrixWrap_double;
%}

%{
#include "pyIdlak/pylib/pyIdlak_io.h"
%}
%include "pyIdlak_io.h"
