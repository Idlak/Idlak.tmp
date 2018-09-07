// pyIdlak/pylib/python-pylib-api.h

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

// Note that this is intended to be internal to pyIdlak and not exposed.

#ifndef KALDI_PYIDLAK_PYLIB_PYTHON_PYLIB_API_H_
#define KALDI_PYIDLAK_PYLIB_PYTHON_PYLIB_API_H_

#include "pyIdlak_types.h"

// Add to this as needed
enum IDLAK_OPT_TYPES {
  NONE = 0,
  AperiodicEnergyOptions = 1
};


PySimpleOptions * PySimpleOptions_new(enum IDLAK_OPT_TYPES opttype);
void PySimpleOptions_delete(PySimpleOptions *  pyopts);

std::vector<std::string> PySimpleOptions_option_names(PySimpleOptions * pyopts);
const char * PySimpleOptions_option_pytype(PySimpleOptions * pyopts, const char * key);

bool PySimpleOptions_get_numeric(PySimpleOptions * pyopts, const std::string &key, double *OUTPUT);
bool PySimpleOptions_get_string(PySimpleOptions * pyopts, const std::string &key, std::string * OUTPUT);

bool PySimpleOptions_set_float(PySimpleOptions * pyopts, const std::string &key, double value);
bool PySimpleOptions_set_int(PySimpleOptions * pyopts, const std::string &key, int value);
bool PySimpleOptions_set_bool(PySimpleOptions * pyopts, const std::string &key, bool value);
bool PySimpleOptions_set_str(PySimpleOptions * pyopts, const std::string &key, const std::string &value);

PyIdlakBuffer * PyIdlakBuffer_newfromstr(const char * data);
void PyIdlakBuffer_delete(PyIdlakBuffer * pybuf);
const char * PyIdlakBuffer_get(PyIdlakBuffer * pybuf);

#endif // KALDI_PYIDLAK_PYLIB_PYTHON_PYLIB_API_H_
