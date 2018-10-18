// idlaktxp/txpphone.h

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

#ifndef KALDI_IDLAKTXP_TXPPHONE_H_
#define KALDI_IDLAKTXP_TXPPHONE_H_

// This file defines greedy part of speech tagger class which
// determines pos tags for each normalised word and the tag set
// class which hold definitions of tag types

#include <map>
#include <utility>
#include <string>
#include <vector>
#include "base/kaldi-common.h"
#include "idlaktxp/idlak-common.h"
#include "idlaktxp/txpxmldata.h"

namespace kaldi {

struct TxpPhoneDescr;

/// Phoneme name to description map
typedef std::map<std::string, TxpPhoneDescr> PhoneMap;
typedef std::pair<std::string, TxpPhoneDescr> PhoneItem;

/// Part of speech tagger
/// see /ref idlaktxp_pos
class TxpPhone: public TxpXmlData {
 public:
  explicit TxpPhone() {}
  ~TxpPhone() {}
  void Init(const TxpParseOptions &opts, const std::string &name) {
    TxpXmlData::Init(opts, "phone", name);
  }
  bool Parse(const std::string &tpdb);
  /// Return the part of speech for word current with previous
  /// context POS prev
  const TxpPhoneDescr* GetPhone(const char* phone_name);

 private:
  void StartElement(const char* name, const char** atts);
  /// Map of phonemes, can be searched by name, i.e. the phoneme itself
  PhoneMap phonemes_;
  /// name of currently parsed phoneme
  std::string phon_name_;
};

struct TxpPhoneDescr {
public:
    /// phoneme
    std::string name;
    // word example
    std::string word_example;
    // pron example
    std::string pron_example;
    // ipa
    std::string ipa;
};

}  // namespace kaldi

#endif  // KALDI_IDLAKTXP_TXPPHONE_H_
