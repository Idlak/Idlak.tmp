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
#include "nnet/nnet-pdf-prior.h"

#include "python-pylib-api.h"
#include "pyIdlak_internal.h"


PySimpleOptions * PySimpleOptions_new(enum IDLAK_OPT_TYPES opttype) {
  PySimpleOptions * pyopts = new PySimpleOptions;
  pyopts->po_ = new kaldi::SimpleOptions;
  PySimpleOptions_register(pyopts, opttype);
  return pyopts;
}


void PySimpleOptions_register(PySimpleOptions * pyopts, enum IDLAK_OPT_TYPES opttype) {
  if (!pyopts) {
    return;
  }
  switch (opttype) {
    case AperiodicEnergyOptions: {
      if (!pyopts->aprd_) {
        pyopts->aprd_ = new kaldi::AperiodicEnergyOptions;
        pyopts->aprd_->Register(pyopts->po_);
      }
      break;
    }
    case nnet1_PdfPriorOptions: {
      if (!pyopts->pdf_prior_) {
        pyopts->pdf_prior_ = new kaldi::nnet1::PdfPriorOptions;
        pyopts->pdf_prior_->Register(pyopts->po_);
      }
      break;
    }
    case NnetForwardOptions: {
      if (!pyopts->nnet_fwd_) {
        pyopts->nnet_fwd_ = new PyNnetForwardOptions;
        pyopts->nnet_fwd_->Register(pyopts->po_);
      }
      break;
    }
    case ApplyCMVNOptions: {
      if (!pyopts->apply_cmvn_) {
        pyopts->apply_cmvn_ = new PyApplyCMVNOptions;
        pyopts->apply_cmvn_->Register(pyopts->po_);
      }
      break;
    }
    case NONE:
      break;
  }
}


void PySimpleOptions_delete(PySimpleOptions * pyopts) {
  if (pyopts->aprd_) delete pyopts->aprd_;
  if (pyopts->pdf_prior_) delete pyopts->pdf_prior_;
  if (pyopts->nnet_fwd_) delete pyopts->nnet_fwd_;
  if (pyopts->apply_cmvn_) delete pyopts->apply_cmvn_;
  delete pyopts;
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





PyIdlakBuffer * PyIdlakBuffer_newfromstr(const char * data) {
  PyIdlakBuffer * pybuf = new PyIdlakBuffer;
  pybuf->len_ = 0;
  pybuf->data_ = nullptr;
  if (data) {
    pybuf->len_ = strlen(data) + 1;
    pybuf->data_ = new char[pybuf->len_];
    if (pybuf->data_)
      strcpy(pybuf->data_, data);
    else
      fprintf(stderr, "Failed to allocate memory\n");
  }
  return pybuf;
}

void PyIdlakBuffer_delete(PyIdlakBuffer * pybuf) {
  if (pybuf) {
    if( pybuf->data_)
      delete pybuf->data_;
    delete pybuf;
  }
}

const char * PyIdlakBuffer_get(PyIdlakBuffer * pybuf) {
  if (pybuf) return pybuf->data_;
  return NULL;
}
