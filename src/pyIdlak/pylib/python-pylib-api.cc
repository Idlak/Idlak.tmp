// pyIdlak/pylib/python-pylib-api.cc

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

#include <vector>
#include "util/simple-options.h"

#include "idlakfeat/feature-aperiodic.h"

#include "python-pylib-api.h"
#include "pyIdlak_internal.h"


PySimpleOptions * PySimpleOptions_new(enum IDLAK_OPT_TYPES opttype) {
  PySimpleOptions * pyopts = new PySimpleOptions;
  pyopts->po_ = new kaldi::SimpleOptions;
  pyopts->opttype_ = opttype;
  
  switch (opttype) {
    case AperiodicEnergyOptions: {
        auto aprdopts = new kaldi::AperiodicEnergyOptions;
        aprdopts->Register(pyopts->po_);
        pyopts->opts_ = static_cast<void*>(aprdopts);
        break;
    }
    case NONE:
        break;
  };

  return pyopts;
}


std::vector<std::string> PySimpleOptions_option_names(PySimpleOptions * pyopts) {
  std::vector<std::string> ret;
  for (auto const& x : pyopts->po_->GetOptionInfoList())
    ret.push_back(x.first);
  return ret;
}


// Return Python types
const char * PySimpleOptions_option_pytype(PySimpleOptions * pyopts, const char * key) {
  enum kaldi::SimpleOptions::OptionType otype;
  std::string keystr(key);
  if (!pyopts->po_->GetOptionType(keystr, &otype))
    return nullptr;

  switch (otype) {
    case kaldi::SimpleOptions::kBool:
      return "bool";

    case kaldi::SimpleOptions::kInt32:
    case kaldi::SimpleOptions::kUint32:
      return "int";

    case kaldi::SimpleOptions::kFloat:
    case kaldi::SimpleOptions::kDouble:
      return "float";

    case kaldi::SimpleOptions::kString:
      return "str";
  }
  return "unknown";
}


bool PySimpleOptions_get_numeric(PySimpleOptions * pyopts, const std::string &key, double *OUTPUT) {

  if(pyopts->po_->GetOption(key, OUTPUT)) {
    return true;
  }

  float tfloat;
  if(pyopts->po_->GetOption(key, &tfloat)) {
    *OUTPUT = tfloat;
    return true;
  }

  int32 tint32;
  if(pyopts->po_->GetOption(key, &tint32)) {
    *OUTPUT = tint32;
    return true;
  }

  uint32 tuint32;
  if(pyopts->po_->GetOption(key, &tuint32)) {
    *OUTPUT = tuint32;
    return true;
  }

  bool tbool;
  if(pyopts->po_->GetOption(key, &tbool)) {
    *OUTPUT = tbool;
    return true;
  }

  *OUTPUT = 0.0;
  return false;
}


bool PySimpleOptions_get_string(PySimpleOptions * pyopts, const std::string &key, std::string *OUTPUT) {
    if(pyopts->po_->GetOption(key, OUTPUT))
        return true;
    return false;
}



bool PySimpleOptions_set_float(PySimpleOptions * pyopts, const std::string &key, double value) {
    if(pyopts->po_->SetOption(key, value))
        return true;
    return false;
}
bool PySimpleOptions_set_int(PySimpleOptions * pyopts, const std::string &key, int value) {
    if(pyopts->po_->SetOption(key, value))
        return true;
    return false;
}
bool PySimpleOptions_set_bool(PySimpleOptions * pyopts, const std::string &key, bool value) {
    if(pyopts->po_->SetOption(key, value))
        return true;
    return false;
}
bool PySimpleOptions_set_str(PySimpleOptions * pyopts, const std::string &key, const std::string &value) {
    if(pyopts->po_->SetOption(key, value))
        return true;
    return false;
}


void PySimpleOptions_delete(PySimpleOptions * pyopts) {

    switch (pyopts->opttype_) {
        case AperiodicEnergyOptions: {
            delete static_cast<kaldi::AperiodicEnergyOptions*>(pyopts->opts_);
            break;
        }
        case NONE:
            break;
    };

    delete pyopts->po_;
    delete pyopts;
}


PyIdlakBuffer * PyIdlakBuffer_newfromstr(const char * data) {
  PyIdlakBuffer * pybuf;
  if (data) {
    pybuf = new PyIdlakBuffer;
    pybuf->len_ = strlen(data);
    pybuf->data_ = new char[pybuf->len_];
    strcpy(pybuf->data_, data);
  }
  return pybuf;
}

void PyIdlakBuffer_delete(PyIdlakBuffer * pybuf) {
  if (pybuf) {
    delete pybuf->data_;
    delete pybuf;
  }
}

const char * PyIdlakBuffer_get(PyIdlakBuffer * pybuf) {
  if (pybuf) return pybuf->data_;
  return NULL;
}