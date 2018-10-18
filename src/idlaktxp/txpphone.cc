// idlaktxp/txphone.cc

// Copyright 2012 CereProc Ltd.  (Author: Skaiste Butkute)

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

// This is a very simple part of speech tagger. It could be improved by taking
// note of breaks caused by punctuation

#include "idlaktxp/txpphone.h"

namespace kaldi {

bool TxpPhone::Parse(const std::string &tpdb) {
  bool r;
  r = TxpXmlData::Parse(tpdb);
  if (!r)
    KALDI_WARN << "Error reading part of phoneme file: " << tpdb;
  return r;
}

const TxpPhoneDescr* TxpPhone::GetPhone(const char* name) {
  PhoneMap::iterator phone_lkp;
  phone_lkp = phonemes_.find(std::string(name));
  if (phone_lkp != phonemes_.end()) return &(phone_lkp->second);
  return NULL;
}

void TxpPhone::StartElement(const char* name, const char** atts) {
  TxpPhoneDescr p_descr;
  if (!strcmp(name, "phone")) {
    SetAttribute("name", atts, &phon_name_);
  } else if (!strcmp(name, "description")) {
    p_descr.name = phon_name_;
    SetAttribute("word_example", atts, &(p_descr.word_example));
    SetAttribute("pron_example", atts, &(p_descr.pron_example));
    SetAttribute("ipa", atts, &(p_descr.ipa));
    phonemes_.insert(PhoneItem(phon_name_, p_descr));
  }
}

}  // namespace kaldi
