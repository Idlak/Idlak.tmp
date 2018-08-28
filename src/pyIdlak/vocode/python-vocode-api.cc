// pyIdlak/python-api.cc

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
#include <vector>
#include <cstdio>

extern "C" {
#include "SPTK.h"
}

#include "python-vocode-api.h"


// Adapted from SPTK source code
std::vector<double> PySPTK_excite(const std::vector<double> &INPUT, int frame_period, int interpolation_period, bool gauss, int seed) {

  // Translating to the names used within SPTK
  int fprd = frame_period,
      iprd = interpolation_period;

  unsigned long next = seed;
  if (gauss & (seed != 1))
      next = srnd((unsigned int) seed);

  std::vector<double> excitation;

  if (!INPUT.size())
     return excitation;

  double p1, p2, pc, inc, x;

  pc = p1 = INPUT[0];
  for (int s = 1; s < INPUT.size(); s++) {
    p2 = INPUT[s];

    if ((p1 != 0.0) && (p2 != 0.0))
      inc = (p2 - p1) * (double) iprd / (double) fprd;
    else {
      inc = 0.0;
      pc = p2;
      p1 = 0.0;
    }

    int i = (iprd + 1) / 2;
    for (int j = fprd; j--;) {
      if (p1 == 0.0) {
        if (gauss)
          x = (double) nrandom(&next);
        else
          x = mseq();
      } else {
        if ((pc += 1.0) >= p1) {
          x = sqrt(p1);
          pc = pc - p1;
        } else
          x = 0.0;
      }

      excitation.push_back(x);

      if (!--i) {
        p1 += inc;
        i = iprd;
      }
    }
    p1 = p2;
  }

  return excitation;
}


// Adapted from SPTK source code
std::vector<double> PySPTK_mgc2sp(const std::vector<double> &INPUT,
                      double alpha, double gamma, int order, bool norm_cepstrum, int fftlen,
                      bool output_phase) {

  std::vector<double> spectrum;

  // Convert arg names to SPTK names
  int m = order, l = fftlen, no, i;
  double *c, *x, *y, logk;
  bool norm = norm_cepstrum,
       phase = output_phase;

  x = dgetmem(l + l + m + 1);
  y = x + l;
  c = y + l;

  no = l / 2 + 1;
  logk = 20.0 / log(10.0);

  for (int s = 0; s < INPUT.size(); s += (m+1) ) {
    for (int sidx = s, t = 0; sidx < (s + m + 1); sidx++, t++) {
      if (sidx >= INPUT.size())
        return spectrum;
      c[t] = INPUT[sidx];
    }
    
    if (norm)
      ignorm(c, c, m, gamma);
      
    mgc2sp(c, m, alpha, gamma, x, y, l);
    
    if (phase) {
      for (i = no; i--;)
        x[i] = y[i] / PI;
    }
    else {
      for (i = no; i--;)
        x[i] *= logk;
    }
    
    for (int t = 0; t < no; t++) {
      spectrum.push_back(x[t]);
    }
  }
  
  delete x;
  return spectrum;
}






