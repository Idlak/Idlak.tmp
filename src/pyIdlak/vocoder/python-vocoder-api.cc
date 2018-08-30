// pyIdlak/python-vocoder-api.cc

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

#include <cmath>
#include <cstring>
#include <string>
#include <vector>
#include <cstdio>

extern "C" {
#include "SPTK.h"
}

#include "python-vocoder-api.h"
#include "python-vocoder-lib.h"

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
                      bool output_phase, int output_format) {

  std::vector<double> spectrum;

  // Convert arg names to SPTK names
  int m = order, l = fftlen, otype = output_format;
  double *c, *x, *y;
  bool norm = norm_cepstrum,
       phase = output_phase;

  x = dgetmem(l + l + m + 1);
  y = x + l;
  c = y + l;

  int no = l / 2 + 1;
  double logk = 20.0 / log(10.0);

  std::vector<double>::const_iterator INPUT_it = INPUT.begin();
  while (vreadf(c, m + 1, INPUT, &INPUT_it) == m + 1) {
    if (norm)
      ignorm(c, c, m, gamma);
      
    mgc2sp(c, m, alpha, gamma, x, y, l);
    
    if (phase) {
      switch (otype) {
        case 1:
          for (int i = no; i--;)
            x[i] = y[i];
          break;
        case 2:
          for (int i = no; i--;)
            x[i] = y[i] * 180 / PI;
          break;
        default:
          for (int i = no; i--;)
            x[i] = y[i] / PI;
          break;
      }
    } else {
      switch (otype) {
        case 1:
          break;
        case 2:
          for (int i = no; i--;)
            x[i] = exp(x[i]);
          break;
        case 3:
          for (int i = no; i--;)
            x[i] = exp(2 * x[i]);
          break;
        default:
          for (int i = no; i--;)
            x[i] *= logk;
          break;
      }
    }
    
    for (int t = 0; t < no; t++) {
      spectrum.push_back(x[t]);
    }
  }
  
  delete x;
  return spectrum;
}


// Adapted from SPTK source code
const double PADE4_THRESH1 = 4.5;
const double PADE4_THRESH2 = 6.2;
const double PADE5_THRESH1 = 6.0;
const double PADE5_THRESH2 = 7.65;

static void mlsacheck(double *mceps, int m, int fftlen, int frame,
               double a, double r, int c, double *stable_mceps, bool quiet)
{
   int i;
   double gain, *x, *y, *mag = NULL, max = 0.0;

   x = dgetmem(fftlen);
   y = dgetmem(fftlen);

   fillz(x, sizeof(*x), fftlen);
   fillz(y, sizeof(*y), fftlen);

   /* calculate gain factor */
   for (i = 0, gain = 0.0; i <= m; i++) {
      x[i] = mceps[i];
      gain += x[i] * pow(-a, i);
   }

   /* gain normalization */
   x[0] -= gain;

   /* check stability */
   if (c == 0 || c == 2 || c == 3) {    /* usual mode */
      mag = dgetmem(fftlen);
      fillz(mag, sizeof(*mag), fftlen);
      fftr(x, y, fftlen);
      for (i = 0; i < fftlen; i++) {
         mag[i] = sqrt(x[i] * x[i] + y[i] * y[i]);
         if (mag[i] > max)
            max = mag[i];
      }
   } else {                     /* fast mode */
      for (i = 0; i <= m; i++)
         max += x[i];
   }

   /* modification MLSA filter coefficients */
   if (max > r) {
      /* output ascii report */
      if (!quiet)
        fprintf(stderr,
                "[No. %d] is unstable frame (maximum = %f, threshold = %f)\n",
                frame, max, r);

      /* modification */
      if (c == 2) {             /* clipping */
         for (i = 0; i < fftlen; i++) {
            if (mag[i] > r) {
               x[i] *= r / mag[i];
               y[i] *= r / mag[i];
            }
         }
      } else if (c == 3) {      /* scaling */
         for (i = 0; i < fftlen; i++) {
            x[i] *= r / max;
            y[i] *= r / max;
         }
      } else if (c == 4) {      /* fast mode */
         for (i = 0; i <= m; i++)
            x[i] *= r / max;
      }
   }

   /* output MLSA filter coefficients */
   if (c == 0 || c == 1 || max <= r) {  /* no modification */
      memcpy(stable_mceps, mceps,  (m + 1)*sizeof(*mceps));
   } else {
      if (c == 2 || c == 3)
         ifft(x, y, fftlen);
      x[0] += gain;
      memcpy(stable_mceps, x,  (m + 1)*sizeof(*x));
   }

   free(x);
   free(y);
   if (c == 0 || c == 2 || c == 3)
      free(mag);
}

std::vector<double> PySPTK_mlsacheck(const std::vector<double> &INPUT, int order,
                                     double all_pass_constant, int fftlen, int check_type,
                                     int stable_condition, int pade_order, double threshold,
                                     bool quiet) {

  std::vector<double> coeffs;
  int m = order, pd = pade_order, c = check_type;
  double a = all_pass_constant, r;

  if (c != 0 && c != 1 && c != 2 && c != 3 && c != 4) {
    fprintf(stderr, "ERROR: check_type is not in 0, 1, 2, 3, 4\n");
    return coeffs;
  }
  if (stable_condition != 0 && stable_condition != 1) {
    fprintf(stderr, "ERROR: stable_condition is not in 0, 1\n");
    return coeffs;
  }
  switch (pd) {
    case 4:
      if (stable_condition == 0)
        r = PADE4_THRESH1;
      else
        r = PADE4_THRESH2;
      break;
    case 5:
      if (stable_condition == 0)
        r = PADE5_THRESH1;
      else
        r = PADE5_THRESH2;
      break;
    default:
      fprintf(stderr, "ERROR: Order of Pade approximation should be 4 or 5!\n");
      return coeffs;
  }
  if (threshold != 0.0)
    r = threshold;

  double * mceps = dgetmem(m + 1);
  double * stable_mceps = dgetmem(m + 1);
  int frame = 0;
  std::vector<double>::const_iterator INPUT_it = INPUT.begin();
  while (vreadf(mceps, m + 1, INPUT, &INPUT_it) == m + 1) {
    mlsacheck(mceps, m, fftlen, frame, a, r, c, stable_mceps, quiet);
    for (int t = 0; t < m + 1; t++) {
      coeffs.push_back(stable_mceps[t]);
    }
    frame++;
  }
  free(mceps);
  free(stable_mceps);
  return coeffs;
}

// Adapted from SPTK
std::vector<double> PySPTK_mlsadf(const std::vector<double> &MCEPS, const std::vector<double> &EXCITATION,
                                  int order, double all_pass_constant,
                                  int frame_period, int interpolation_period, int pade_order,
                                  bool bflag, bool nogain, bool transpose_filter, bool inverse_filter) {
  std::vector<double> waveform;
  
  int m = order,  pd = pade_order,  fprd = frame_period, iprd = interpolation_period;
  bool ngain = nogain,  transpose = transpose_filter,  inverse = inverse_filter;
  double a = all_pass_constant;
  
  if ((pd < 4) || (pd > 5)) {
    fprintf(stderr, "ERROR: Order of Pade approximation should be 4 or 5!\n");
    return waveform;
  }
  
  // Note in the original mceps were in fpc and excitation in fp
  
  double *c = dgetmem(3 * (m + 1) + 3 * (pd + 1) + pd * (m + 2));
  double *cc = c + m + 1;
  double *inc = cc + m + 1;
  double *d = inc + m + 1;
  
  std::vector<double>::const_iterator MCEPS_it = MCEPS.begin();
  std::vector<double>::const_iterator EXCITATION_it = EXCITATION.begin();
  
  if (vreadf(c, m + 1, MCEPS, &MCEPS_it) != m + 1)
    return waveform;
  if (!bflag)
    mc2b(c, c, m, a);

  int i, j;
  double x;
  if (inverse) {
    if (!ngain) {
      for (i = 0; i <= m; i++)
        c[i] *= -1;
    } else {
      c[0] = 0;
      for (i = 1; i <= m; i++)
        c[i] *= -1;
    }
  }

  bool filter_finished = false;
  while (!filter_finished) {
    if (vreadf(cc, m + 1, MCEPS, &MCEPS_it) != m + 1) {
      filter_finished = true;
      break;
    }
    if (!bflag)
      mc2b(cc, cc, m, a);
    if (inverse) {
      if (!ngain) {
        for (i = 0; i <= m; i++)
          cc[i] *= -1;
      } else {
        cc[0] = 0;
        for (i = 1; i <= m; i++)
          cc[i] *= -1;
      }
    }

    for (i = 0; i <= m; i++)
      inc[i] = (cc[i] - c[i]) * (double) iprd / (double) fprd;

    for (j = fprd, i = (iprd + 1) / 2; j--;) {
      if (vreadf(&x, 1, EXCITATION, &EXCITATION_it) != 1) {
        filter_finished = true;
        break;
      }

      if (!ngain)
        x *= exp(c[0]);
      if (transpose)
        x = mlsadft(x, c, m, a, pd, d);
      else
        x = mlsadf(x, c, m, a, pd, d);

      waveform.push_back(x);

      if (!--i) {
        for (i = 0; i <= m; i++)
          c[i] += inc[i];
        i = iprd;
      }
    }

    if (!filter_finished)
      movem(cc, c, sizeof(*cc), m + 1);
  }

  free(c);
  return waveform;
}





