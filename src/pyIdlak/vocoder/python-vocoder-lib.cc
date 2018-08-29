// pyIdlak/python-vocoder-api.cc

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

#include <cmath>
#include <string>
#include <vector>
#include <cstdio>

extern "C" {
#include "SPTK.h"
}

#include "python-vocoder-api.h"
#include "python-vocoder-lib.h"

int vreadf(double *ptr, const int nitems,
           const std::vector<double> &vec, std::vector<double>::const_iterator * pos) {
  int no_read;
  for(no_read = 0; (*pos != vec.end()) && (no_read < nitems); no_read++, (*pos)++) {
    ptr[no_read] = **pos;
  }
  return no_read;
}