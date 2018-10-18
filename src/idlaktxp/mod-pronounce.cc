// idlaktxp/mod-pronounce.cc

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

#include "idlaktxp/mod-pronounce.h"

namespace kaldi {

TxpPronounce::TxpPronounce() : TxpModule("pronounce") {}

TxpPronounce::~TxpPronounce() {
}

bool TxpPronounce::Init(const TxpParseOptions &opts) {
  opts_ = &opts;
  tpdb_ = opts.GetTpdb();
  lex_.Init(opts, std::string(GetOptValue("arch")));
  lts_.Init(opts, std::string(GetOptValue("arch")));
  phone_.Init(opts, std::string(GetOptValue("arch")));
  if (lex_.Parse(tpdb_) && lts_.Parse(tpdb_) && phone_.Parse(tpdb_)) return true;
  return false;
}

bool TxpPronounce::Process(pugi::xml_document* input) {
  pugi::xml_node parent, child;
  pugi::xpath_node_set tks = input->document_element().select_nodes("//tk");
  const char* lex_entry;
  const char* lex_pron;
  const char* word;
  std::string utfchar, word_str, altprons;
  TxpLexiconLkp lexlkp;
  int32 i;
  tks.sort();
  for (pugi::xpath_node_set::const_iterator it = tks.begin();
       it != tks.end();
       ++it) {
    pugi::xml_node node = (*it).node();
    word = node.attribute("norm").value();
    if (std::string(word).compare("") == 0)
        word = node.attribute("tknorm").value();
    lexlkp.Reset();
    // Check to see if token is first daughter of a lex tag
    parent = node.parent();
    lex_entry = NULL;
    lex_pron = NULL;
    while (parent) {
      if (!strcmp(parent.name(), "lex")) {
        if ((*(parent.select_nodes("descendant::tk[1]").begin())).node()
            == node) {
          lex_entry = parent.attribute("entry").value();
          lex_pron = parent.attribute("pron").value();
        }
      }
      parent = parent.parent();
    }
    word_str = std::string(word);
    // If pron is set use that pron
    if (lex_pron && *lex_pron) {
      node.append_attribute("pron").set_value(lex_pron);
    } else {
      // standard lookup of word
      AppendPron(lex_entry, std::string(word), &lexlkp);
      // in the received pronounciation lookup phonemes and check if they
      // exist in the phoneme set
      int32 st_phon_pos = 0, end_phon_pos = 0;
      std::string sub_word = lexlkp.pron.substr(st_phon_pos);
      std::string phone_2_chk = "";
      while (sub_word.length() > 0) {
        end_phon_pos = sub_word.find(" ");
        if (end_phon_pos == std::string::npos) {
          end_phon_pos = sub_word.length()-1;
          phone_2_chk = sub_word;
        } else
          phone_2_chk = sub_word.substr(0, end_phon_pos);

        // if the phoneme has a stress, remove it
        if (isdigit(phone_2_chk.substr(phone_2_chk.length()-1)[0])) {
          phone_2_chk = phone_2_chk.substr(0, phone_2_chk.length()-1);
        }

        // if a phoneme turns out to be an empty string, then it is wrong and
        // the pronounciation is removed.
        if (phone_2_chk.compare("") == 0) {
            lexlkp.pron = "";
            break;
        }

        // if no phoneme is found, pronounciation is removed
        const TxpPhoneDescr* found_phone = phone_.GetPhone(phone_2_chk.c_str());
        if (found_phone == NULL) {
            KALDI_ERR << "Phoneme " << phone_2_chk << " from word " << word << " could not be found";
            lexlkp.pron = "";
            break;
        }

        st_phon_pos = end_phon_pos + 1;
        sub_word = sub_word.substr(st_phon_pos);
      }

      node.append_attribute("pron").set_value(lexlkp.pron.c_str());
      if (lexlkp.lts) {
        node.append_attribute("lts").set_value("true");
      } else if (!lexlkp.lts && lexlkp.altprons.size() > 1) {
        altprons.clear();
        for (i = 0; i < lexlkp.altprons.size(); i++) {
          if (i) altprons = altprons + ", ";
          altprons = altprons + lexlkp.altprons[i];
        }
        node.append_attribute("altprons").set_value(altprons.c_str());
      }
    }
  }
  return true;
}

void TxpPronounce::AppendPron(const char* entry,
                              const std::string &word,
                              TxpLexiconLkp* lexlkp) {
  bool found = false;
  if (!lexlkp->pron.empty()) lexlkp->pron += " ";
  if (entry) {
    found = lex_.GetPron(word, std::string(entry), lexlkp);
    if (!found) {
      found = lex_.GetPron(word, std::string(""), lexlkp);
    }
  } else {
    found = lex_.GetPron(word, std::string(""), lexlkp);
  }
  if (!found)
    found = lts_.GetPron(word, lexlkp);
}

}  // namespace kaldi
