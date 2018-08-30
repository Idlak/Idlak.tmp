// pyIdlak/python-vocode-mlpg.cc

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

// The mlpg binary has a lot of internal functions that will makes it unwieldy
// to include in the vocode-api

// Adapted from SPTK source code

#include <cmath>
#include <string>
#include <vector>
#include <cstdio>

extern "C" {
#include "SPTK.h"
}

#include "python-vocoder-api.h"
#include "python-vocoder-lib.h"


// Structures from SPTK
typedef struct _DWin {
   int num;                     /* number of static + deltas */
   char **fn;                   /* delta window coefficient file */
   int **width;                 /* width [0..num-1][0(left) 1(right)] */
   double **coef;               /* coefficient [0..num-1][length[0]..length[1]] */
   int maxw[2];                 /* max width [0(left) 1(right)] */
} DWin;

typedef struct _SMatrix {
   double **mseq;               /* sequence of mean vector */
   double **ivseq;              /* sequence of invarsed variance vector */
   double ***P;                 /* matrix P[th][tv][m] */
   double **c;                  /* parameter c */
   double **pi;
   double **k;
   int t;                       /* time index */
   int length;                  /* matrix length (must be power of 2) */
   unsigned int mask;           /* length - 1 */
} SMatrix;

typedef struct _PStream {
   int vSize;                   /* data vector size */
   int order;                   /* order of cepstrum */
   int range;
   DWin dw;
   double *mean;                /* input mean vector */
   double *ivar;                /* input inversed variance vector */
   double *par;                 /* output parameter vector */
   int iType;                   /* type of input PDFs */
   /*   0: ( m       , U      ) */
   /*   1: ( m       , U^{-1} ) */
   /*   2: ( mU^{-1} , U^{-1} ) */
   SMatrix sm;
} PStream;


// Constants from SPTK
typedef double real;

const double INFTY = 1.0e+38;
const double INFTY2 = 1.0e+19;
const double INVINF = 1.0e-38;
const double INVINF2 = 1.0e-19;

const int WLEFT = 0;
const int WRIGHT = 1;
const int LENGTH = 256;

/*  Required Functions  */
void init_pstream(PStream * pst);
void init_dwin(PStream * pst);
double *dcalloc(int x, int xoff);
double **ddcalloc(int x, int y, int xoff, int yoff);
double ***dddcalloc(int x, int y, int z, int xoff, int yoff, int zoff);
double *mlpg(PStream * pst);
int doupdate(PStream * pst, int d);
void calc_pi(PStream * pst, int d);
void calc_k(PStream * pst, int d);
void update_P(PStream * pst);
void update_c(PStream * pst, int d);

#define sign(x)  ((x) >= 0.0 ? 1 : -1)
#define finv(x)  (abs(x) <= INVINF2 ? sign(x)*INFTY : (abs(x) >= INFTY2 ? 0 : 1.0/(x)))
#define min(x, y) ((x)<(y) ? (x) : (y))

std::vector<double> PySPTK_mlpg(const std::vector<double> &INPUT, int order,
                                const std::vector<std::string> &window_filenames, int input_type,
                                int influence_range) {
  std::vector<double> parameters;
  
  PStream pst;
  pst.order = order;
  pst.range = influence_range;
  pst.iType = input_type;
  pst.dw.num = window_filenames.size();
  pst.dw.fn = (char **) calloc(sizeof(char *), pst.dw.num);

  for (int i = 0; i < window_filenames.size(); i++) {
    pst.dw.fn[i] = const_cast<char*>(window_filenames[0].c_str());
  }

  init_pstream(&pst);

  int nframe = 0;
  int delay = pst.range + pst.dw.maxw[WRIGHT];
  
  std::vector<double>::const_iterator INPUT_it = INPUT.begin();
  while (vreadf(pst.mean, pst.vSize * 2, INPUT, &INPUT_it) == pst.vSize * 2) {
    if (pst.dw.num == 1) {
      for (int i = 0; i < pst.order + 1; i++) {
        parameters.push_back(pst.mean[i]);
      }
    } else {
      if (pst.iType == 0) {
          for (int i = 0; i < pst.vSize; i++)
              pst.ivar[i] = finv(pst.ivar[i]);
      }

      mlpg(&pst);

      if (nframe >= delay) {
        for (int i = 0; i < pst.order + 1; i++) {
          parameters.push_back(pst.par[i]);
        }
      }
    }
    nframe++;
  }

  if (pst.dw.num > 1) {
    for (int i = 0; i < pst.vSize; i++) {
      pst.mean[i] = 0.0;
      pst.ivar[i] = 0.0;
    }
    for (int i = 0; i < min(nframe, delay); i++) {
      mlpg(&pst);
      for (int i = 0; i < pst.order + 1; i++) {
        parameters.push_back(pst.par[i]);
      }
    }
  }

  return parameters;
}




void init_pstream(PStream * pst)
{
   void init_dwin(PStream *);
   double *dcalloc(int, int);
   double **ddcalloc(int, int, int, int);
   double ***dddcalloc(int, int, int, int, int, int);
   int half, full;
   int i, m;

   init_dwin(pst);

   half = pst->range * 2;
   full = pst->range * 4 + 1;

   pst->vSize = (pst->order + 1) * pst->dw.num;

   pst->sm.length = LENGTH;
   while (pst->sm.length < pst->range + pst->dw.maxw[WRIGHT])
      pst->sm.length *= 2;

   pst->mean = dcalloc(pst->vSize * 2, 0);
   pst->ivar = pst->mean + pst->vSize;

   pst->sm.mseq = ddcalloc(pst->sm.length, pst->vSize, 0, 0);
   pst->sm.ivseq = ddcalloc(pst->sm.length, pst->vSize, 0, 0);

   pst->sm.c = ddcalloc(pst->sm.length, pst->order + 1, 0, 0);
   pst->sm.P = dddcalloc(full, pst->sm.length, pst->order + 1, half, 0, 0);

   pst->sm.pi =
       ddcalloc(pst->range + pst->dw.maxw[WRIGHT] + 1, pst->order + 1,
                pst->range, 0);
   pst->sm.k =
       ddcalloc(pst->range + pst->dw.maxw[WRIGHT] + 1, pst->order + 1,
                pst->range, 0);

   for (i = 0; i < pst->sm.length; i++)
      for (m = 0; m < pst->vSize; m++)
         pst->sm.ivseq[i][m] = 0.0;

   for (i = 0; i < pst->sm.length; i++)
      for (m = 0; m <= pst->order; m++)
         pst->sm.P[0][i][m] = INFTY;

   pst->sm.t = pst->range - 1;
   pst->sm.mask = pst->sm.length - 1;

   return;
}


void init_dwin(PStream * pst)
{
   double *dcalloc(int, int);
   int i;
   int fsize, leng;
   FILE *fp;

   /* memory allocation */
   if ((pst->dw.width = (int **) calloc(pst->dw.num, sizeof(int *))) == NULL) {
      fprintf(stderr, "ERROR: Cannot allocate memory!\n");
      return;
   }
   for (i = 0; i < pst->dw.num; i++)
      if ((pst->dw.width[i] = (int *) calloc(2, sizeof(int))) == NULL) {
         fprintf(stderr, "ERROR: Cannot allocate memory!\n");
         return;
      }
   if ((pst->dw.coef =
        (double **) calloc(pst->dw.num, sizeof(double *))) == NULL) {
      fprintf(stderr, "ERROR: Cannot allocate memory!\n");
      return;
   }

   /* window for static parameter */
   pst->dw.width[0][WLEFT] = pst->dw.width[0][WRIGHT] = 0;
   pst->dw.coef[0] = dcalloc(1, 0);
   pst->dw.coef[0][0] = 1;

  /* set delta coefficients */
  for (i = 1; i < pst->dw.num; i++) {
    /* read from file */
    const char * rb = "rb"; // LEGACY C COMPATABILITY
    fp = getfp(pst->dw.fn[i], const_cast<char*>(rb));

    /* check the number of coefficients */
    fseek(fp, 0L, 2);
    fsize = ftell(fp) / sizeof(real);
    fseek(fp, 0L, 0);

    /* read coefficients */
    pst->dw.coef[i] = dcalloc(fsize, 0);
    freadf(pst->dw.coef[i], sizeof(**(pst->dw.coef)), fsize, fp);

    /* set pointer */
    leng = fsize / 2;
    pst->dw.coef[i] += leng;
    pst->dw.width[i][WLEFT] = -leng;
    pst->dw.width[i][WRIGHT] = leng;
    if (fsize % 2 == 0)
      pst->dw.width[i][WRIGHT]--;
  }


   pst->dw.maxw[WLEFT] = pst->dw.maxw[WRIGHT] = 0;
   for (i = 0; i < pst->dw.num; i++) {
      if (pst->dw.maxw[WLEFT] > pst->dw.width[i][WLEFT])
         pst->dw.maxw[WLEFT] = pst->dw.width[i][WLEFT];
      if (pst->dw.maxw[WRIGHT] < pst->dw.width[i][WRIGHT])
         pst->dw.maxw[WRIGHT] = pst->dw.width[i][WRIGHT];
   }

   return;
}


double *dcalloc(int x, int xoff)
{
   double *ptr;

   if ((ptr = (double *) calloc(x, sizeof(*ptr))) == NULL) {
      fprintf(stderr, "ERROR: Cannot allocate memory!\n");
      return nullptr;
   }
   ptr += xoff;
   return (ptr);
}


double **ddcalloc(int x, int y, int xoff, int yoff)
{
   double *dcalloc(int, int);
   double **ptr;
   int i;

   if ((ptr = (double **) calloc(x, sizeof(*ptr))) == NULL) {
      fprintf(stderr, "ERROR: Cannot allocate memory!\n");
      return nullptr;
   }
   for (i = 0; i < x; i++)
      ptr[i] = dcalloc(y, yoff);
   ptr += xoff;
   return (ptr);
}


double ***dddcalloc(int x, int y, int z, int xoff, int yoff, int zoff)
{
   double **ddcalloc(int, int, int, int);
   double ***ptr;
   int i;

   if ((ptr = (double ***) calloc(x, sizeof(*ptr))) == NULL) {
      fprintf(stderr, "ERROR: Cannot allocate memory!\n");
      return nullptr;
   }
   for (i = 0; i < x; i++)
      ptr[i] = ddcalloc(y, z, yoff, zoff);
   ptr += xoff;
   return (ptr);
}

/*--------------------------------------------------------------------*/

double *mlpg(PStream * pst)
{
   int doupdate(PStream *, int);
   void calc_pi(PStream *, int);
   void calc_k(PStream *, int);
   void update_P(PStream *);
   void update_c(PStream *, int);
   int tmin, tmax;
   int d, m, u;

   pst->sm.t++;
   tmin = (pst->sm.t - pst->range) & pst->sm.mask;
   tmax = (pst->sm.t + pst->dw.maxw[WRIGHT]) & pst->sm.mask;

   for (u = -pst->range * 2; u <= pst->range * 2; u++) {
      for (m = 0; m <= pst->order; m++)
         pst->sm.P[u][tmax][m] = 0.0;
   }
   for (m = 0; m < pst->vSize; m++) {
      pst->sm.mseq[tmax][m] = pst->mean[m];
      pst->sm.ivseq[tmax][m] = pst->ivar[m];
   }
   for (m = 0; m <= pst->order; m++) {
      if (pst->iType != 2)
         pst->sm.c[tmax][m] = pst->mean[m];
      else
         pst->sm.c[tmax][m] = pst->mean[m] * finv(pst->ivar[m]);
      pst->sm.P[0][tmax][m] = finv(pst->ivar[m]);
   }

   for (d = 1; d < pst->dw.num; d++) {
      if (doupdate(pst, d)) {
         calc_pi(pst, d);
         calc_k(pst, d);
         update_P(pst);
         update_c(pst, d);
      }
   }
   pst->par = pst->sm.c[tmin];
   return (pst->par);
}


int doupdate(PStream * pst, int d)
{
   int j;

   if (pst->sm.ivseq[pst->sm.t & pst->sm.mask][(pst->order + 1) * d] == 0.0)
      return (0);
   for (j = pst->dw.width[d][WLEFT]; j <= pst->dw.width[d][WRIGHT]; j++)
      if (pst->sm.P[0][(pst->sm.t + j) & pst->sm.mask][0] == INFTY)
         return (0);
   return (1);
}


void calc_pi(PStream * pst, int d)
{
   int j, m, u;

   for (m = 0; m <= pst->order; m++)
      for (u = -pst->range; u <= pst->dw.maxw[WRIGHT]; u++) {
         pst->sm.pi[u][m] = 0.0;
         for (j = pst->dw.width[d][WLEFT]; j <= pst->dw.width[d][WRIGHT]; j++)
            pst->sm.pi[u][m] +=
                pst->sm.P[u -
                          j][(pst->sm.t +
                              j) & pst->sm.mask][m] * pst->dw.coef[d][j];
      }

   return;
}


void calc_k(PStream * pst, int d)
{
   int j, m, u;
   double *ivar, x;

   ivar = pst->sm.ivseq[pst->sm.t & pst->sm.mask] + (pst->order + 1) * d;
   for (m = 0; m <= pst->order; m++) {
      x = 0.0;
      for (j = pst->dw.width[d][WLEFT]; j <= pst->dw.width[d][WRIGHT]; j++)
         x += pst->dw.coef[d][j] * pst->sm.pi[j][m];
      x = ivar[m] / (1.0 + ivar[m] * x);
      for (u = -pst->range; u <= pst->dw.maxw[WRIGHT]; u++) {
         pst->sm.k[u][m] = pst->sm.pi[u][m] * x;
      }
   }

   return;
}


void update_P(PStream * pst)
{
   int m, u, v;

   for (m = 0; m <= pst->order; m++)
      for (u = -pst->range; u <= pst->dw.maxw[WRIGHT]; u++)
         for (v = u; v <= pst->dw.maxw[WRIGHT]; v++) {
            pst->sm.P[v - u][(pst->sm.t + u) & pst->sm.mask][m] -=
                pst->sm.k[v][m] * pst->sm.pi[u][m];
            if (v != u)
               pst->sm.P[u - v][(pst->sm.t + v) & pst->sm.mask][m] =
                   pst->sm.P[v - u][(pst->sm.t + u) & pst->sm.mask][m];
         }

   return;
}


void update_c(PStream * pst, int d)
{
   int j, m, u;
   double *mean, *ivar, x;

   ivar = pst->sm.ivseq[pst->sm.t & pst->sm.mask] + (pst->order + 1) * d;
   mean = pst->sm.mseq[pst->sm.t & pst->sm.mask] + (pst->order + 1) * d;
   for (m = 0; m <= pst->order; m++) {
      x = mean[m];
      if (pst->iType == 2)
         x *= finv(ivar[m]);
      for (j = pst->dw.width[d][WLEFT]; j <= pst->dw.width[d][WRIGHT]; j++)
         x -= pst->dw.coef[d][j] * pst->sm.c[(pst->sm.t + j) & pst->sm.mask][m];
      for (u = -pst->range; u <= pst->dw.maxw[WRIGHT]; u++)
         pst->sm.c[(pst->sm.t + u) & pst->sm.mask][m] += pst->sm.k[u][m] * x;
   }

   return;
}

