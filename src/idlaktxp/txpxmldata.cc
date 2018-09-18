// idlaktxp/txpxmldata.cc

// Copyright 2012 CereProc Ltd.  (Author: Matthew Aylett)

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

#include "idlaktxp/txpxmldata.h"

namespace kaldi {

TxpXmlData::~TxpXmlData() {
  if (parser_) {
    XML_ParserFree(parser_);
  }
}

void TxpXmlData::Init(const TxpParseOptions &opts, const std::string &type,
                      const std::string &name) {
  opts_ = &opts;
  type_ = type;
  name_ = name;
  parser_ = XML_ParserCreate("UTF-8");
  ::XML_SetUserData(parser_, this);
  ::XML_SetElementHandler(parser_, StartElementCB, EndElementCB);
  ::XML_SetCharacterDataHandler(parser_, CharHandlerCB);
  ::XML_SetStartCdataSectionHandler(parser_, StartCDataCB);
  ::XML_SetEndCdataSectionHandler(parser_, EndCDataCB);
}

void TxpXmlData::StartElementCB(void *userData, const char *name,
                            const char **atts) {
  reinterpret_cast<TxpXmlData*>(userData)->StartElement(name, atts);
}

void TxpXmlData::EndElementCB(void *userData, const char *name) {
  reinterpret_cast<TxpXmlData*>(userData)->EndElement(name);
}

void TxpXmlData::CharHandlerCB(void *userData, const char* data, int32 len) {
  reinterpret_cast<TxpXmlData*>(userData)->CharHandler(data, len);
}

void TxpXmlData::StartCDataCB(void *userData) {
  reinterpret_cast<TxpXmlData*>(userData)->StartCData();
}

void TxpXmlData::EndCDataCB(void *userData) {
  reinterpret_cast<TxpXmlData*>(userData)->EndCData();
}

bool TxpXmlData::Parse(const std::string &tpdb) {
  return Parse(tpdb, std::string(""));
}

bool TxpXmlData::Parse(const std::string &tpdb, const std::string &fname) {
  const char *lang, *region, *acc, *spk;
  bool binary, fileopen = false;
  enum XML_Status r;
  Input ki;
  std::string dataroot;
  tpdb_ = tpdb;
  fname_.clear();
  // if no fname specified use architecture and default type name
  if (!fname.empty()) fname_ = fname;
  else fname_ = type_ + "-" + name_ + ".xml";
  // get general settings from the configuration
  lang = GetOptValue("lang");
  region = GetOptValue("region");
  acc = GetOptValue("acc");
  spk = GetOptValue("spk");
  if (!lang) {
    KALDI_ERR << "No language specified: i.e. --general-lang=en";
  }
  // if fname specified override architecture and default type name
  // and only accept this file (no default names)
  if (!fname.empty()) {
    fname_ = fname;
  } else {
    // first search for architecture file <type_>-<name_>.xml
    fname_ = type_ + "-" + name_ + ".xml";
  }
  
  // If we are in a kaldi flat directory structure look for the file
  // first as fname_ and second as default value
  if (ki.Open((tpdb + "/idlak-data-flat").c_str())) {
    path_ = tpdb_;
    // search in this directory only
    if (!ki.Open((path_ + "/" + fname_).c_str(), &binary)) {
      KALDI_WARN << "Can't find xml data:" << path_ << "/" << fname_;
    }
  } else {
    if (spk && *spk) {
      path_ = tpdb_ + "/" + lang + "/" + acc + "/" + spk;
      fileopen = ki.Open((path_ + "/" + fname_).c_str(), &binary);
    }
    if (!fileopen && acc && *acc) {
      path_ = tpdb_ + "/" + lang + "/" + acc;
      fileopen = ki.Open((path_ + "/" + fname_).c_str(), &binary);
    }
    if (!fileopen && region && *region) {
      path_ = tpdb_ + "/" + lang + "/" + region;
        fileopen = ki.Open((path_ + "/" + fname_).c_str(), &binary);
    }
    if (!fileopen) {
      path_ = tpdb_ + "/" + lang;
      fileopen = ki.Open((path_ + "/" + fname_).c_str(), &binary);      
    }
    if (!fileopen)  KALDI_WARN << "Can't find xml data in " <<
                        "speaker/accent/region/language directories:" <<
                        "tpdb root:" << path_ << " fname:" << fname_;
  }
  
  // if still not found and fname is not overridden
  // try to open a default data file
  if (!fileopen && fname.empty() && name_ != "default") {
    fname_.clear();
    fname_ = type_ + "-default.xml";
    if (ki.Open((tpdb + "/idlak-data-flat").c_str())) {
      path_ = tpdb_;
      // search in this directory only
      if (!ki.Open((path_ + "/" + fname_).c_str(), &binary)) {
        KALDI_ERR << "Can't find xml data:" << path_ << "/" << fname_;
      }
    } else {
      if (spk && *spk) {
        path_ = tpdb_ + "/" + lang + "/" + acc + "/" + spk;
        fileopen = ki.Open((path_ + "/" + fname_).c_str(), &binary);
      }
      if (!fileopen && acc && *acc) {
        path_ = tpdb_ + "/" + lang + "/" + acc;
        fileopen = ki.Open((path_ + "/" + fname_).c_str(), &binary);
      }
      if (!fileopen && region && *region) {
        path_ = tpdb_ + "/" + lang + "/" + region;
        fileopen = ki.Open((path_ + "/" + fname_).c_str(), &binary);
      }
      if (!fileopen) {
        path_ = tpdb_ + "/" + lang;
        fileopen = ki.Open((path_ + "/" + fname_).c_str(), &binary);      
      }
    }
  }
  
  if (!fileopen) KALDI_ERR << "Can't find xml data in speaker/accent/region/language directories:" <<
                     "tpdb root:" << tpdb_ << " fname:" << fname_;
  
  KALDI_VLOG(1) << "Loading: " << path_ << "/" << fname_;
  while (getline(ki.Stream(), buffer_)) {
    // Reappend line break to get correct error reporting
    buffer_.append("\n");
    r = XML_Parse(parser_, buffer_.c_str(), buffer_.length(), false);
    if (r == XML_STATUS_ERROR) {
      KALDI_WARN << "Expat XML Parse error: " <<
          XML_ErrorString(::XML_GetErrorCode(parser_))
                 << " Line: " << ::XML_GetCurrentLineNumber(parser_)
                 << " Col:" << XML_GetCurrentColumnNumber(parser_);
      return false;
    }
  }
  XML_Parse(parser_, "", 0, true);
  ki.Close();
  return true;
}

int32 TxpXmlData::SetAttribute(const char* name, const char** atts,
                         std::string* val) {
  int32 i = 0;
  val->clear();
  while (atts[i]) {
    if (!strcmp(atts[i], name)) *val = atts[i + 1];
    i += 2;
  }
  return i / 2;
}

const char* TxpXmlData::GetOptValue(const char* key) {
  return opts_->GetValue("general", key);
}

}  // namespace kaldi
