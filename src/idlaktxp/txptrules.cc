// idlaktxp/txptrules.cc

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

#include "idlaktxp/txptrules.h"
#include "idlaktxp/txputf8.h"

namespace kaldi {

TxpTrules::TxpTrules()
    : incdata_(false),
      cdata_buffer_(""),
      lkp_item_(NULL),
      lkp_open_(NULL),
      rgxwspace_(NULL),
      rgxsep_(NULL),
      rgxpunc_(NULL),
      rgxalpha_(NULL),
      rgxwspace_default_(NULL) {
}

TxpTrules::~TxpTrules() {
  RgxMap::iterator it;
  RgxVector::iterator itv;
  LookupMapMap::iterator itmap;
  for (it = rgxs_.begin(); it != rgxs_.end(); it++) {
    pcre_free(const_cast<pcre *>(it->second));
  }
  for (itmap = lkps_.begin(); itmap != lkps_.end(); itmap++) {
    delete (itmap->second);
  }
  for (itv = tokrgxs_.begin(); itv != tokrgxs_.end(); itv++) {
    pcre_free(const_cast<pcre *>(*itv));
  }
  pcre_free(const_cast<pcre *>(lkp_item_));
  pcre_free(const_cast<pcre *>(lkp_open_));
}

void TxpTrules::Init(const TxpParseOptions &opts, const std::string &name) {
  TxpPcre pcre;
  TxpXmlData::Init(opts, "trules", name);
  lkp_item_ = pcre.Compile("[\n\\s]*(u?[\\'\\\"](.*?)[\\'\\\"]\\s*:\\s*u?[\\'\\\"](.*?)[\\'\\\"])[\n\\s]*[,}][\n\\s]*");// NOLINT
  lkp_open_ = pcre.Compile("[\n\\s]*{");

  rgxs_.insert(RgxItem("whitespace", pcre.Compile("^([ \n\t\r]+)")));
  rgxs_.insert(RgxItem("punctuation", pcre.Compile("^([\\(\\)\\[\\]\\{\\}\\\"'!\\?\\.,;:\\|]*)(.*?)([\\(\\)\\[\\]\\{\\}\\\"'!\\?\\.,;:\\|]*)$")));
  rgxs_.insert(RgxItem("alpha", pcre.Compile("^[a-zA-Z_']+$")));
  MakeLkp(&lkps_, "downcase", "{\"A\":\"a\", \"B\":\"b\", \"C\":\"c\", \"D\":\"d\", \"E\":\"e\", \"F\":\"f\", \"G\":\"g\", \"H\":\"h\", \"I\":\"i\", \"J\":\"j\", \"K\":\"k\", \"L\":\"l\", \"M\":\"m\", \"N\":\"n\", \"O\":\"o\", \"P\":\"p\", \"Q\":\"q\", \"R\":\"r\", \"S\":\"s\", \"T\":\"t\", \"U\":\"u\", \"V\":\"v\", \"W\":\"w\", \"X\":\"x\", \"Y\":\"y\", \"Z\":\"z\"}");// NOLINT
  MakeLkp(&lkps_, "convertillegal", "{\"À\":\"A\", \"Á\":\"A\", \"Â\":\"A\", \"Ã\":\"A\", \"Å\":\"A\", \"Æ\":\"AE\", \"à\":\"a\", \"á\":\"a\", \"â\":\"a\", \"ã\":\"a\", \"å\":\"a\", \"æ\":\"ae\", \"Ç\":\"C\", \"ç\":\"c\", \"È\":\"E\", \"É\":\"E\", \"Ê\":\"E\", \"Ë\":\"E\", \"è\":\"e\", \"é\":\"e\", \"ê\":\"e\", \"ë\":\"e\", \"Ì\":\"I\", \"Í\":\"I\", \"Î\":\"I\", \"Ï\":\"I\", \"ì\":\"i\", \"í\":\"i\", \"î\":\"i\", \"ï\":\"i\", \"Ñ\":\"N\", \"ñ\":\"n\", \"Ò\":\"O\", \"Ó\":\"O\", \"Ô\":\"O\", \"Õ\":\"O\", \"Ø\":\"O\", \"ò\":\"o\", \"ó\":\"o\", \"ô\":\"o\", \"õ\":\"o\", \"ø\":\"o\", \"Ù\":\"U\", \"Ú\":\"U\", \"Û\":\"U\", \"Ű\":u\"Ü\", \"ù\":\"u\", \"ú\":\"u\", \"û\":\"u\", \"ű\":u\"ü\", \"Ý\":\"Y\", \"ý\":\"y\"}");// NOLINT
  MakeLkp(&lkps_, "utfpunc2ascii", "{\"‘\":\"'\", \"’\":\"'\", \"‛\":\"'\", '“':'\"', '”':'\"',\"΄\":\"'\", \"´\":\"'\", \"`\":\"'\", \"…\":\".\", \"„\":'\"', '–':'-', '–':'-', '–':'-', '—':'-', \"＇\":\"'\"}");// NOLINT
}


bool TxpTrules::Parse(const std::string &tpdb) {
  TxpPcre pcre_funcs;
  const pcre* rgx;
  bool r;
  r = TxpXmlData::Parse(tpdb);
  if (r) {
    rgx = GetRgx("whitespace");
    if (rgx) rgxwspace_ = rgx;
    rgx = GetRgx("punctuation");
    if (rgx) rgxpunc_ = rgx;
    rgx = GetRgx("alpha");
    if (rgx) rgxalpha_ = rgx;
    // default to tokenising on whitespace only
    tokrgxs_.push_back(pcre_funcs.Compile("^(.*)"));
 } else {
    KALDI_WARN << "Error reading normaliser rule file: " << tpdb;
  }
  return r;
}

const std::string* TxpTrules::Lkp(const std::string & name,
                                  const std::string & key) {
  std::string namekey;
  LookupMapMap::iterator itmap;
  LookupMap::iterator it, tmp;
  itmap = lkps_.find(name);
  if (itmap != lkps_.end()) {
    it = (itmap->second)->find(key);
    if (it != (itmap->second)->end()) return &(it->second);
    else return NULL;
  }
  return NULL;
}

const pcre* TxpTrules::GetRgx(const std::string & name) {
  RgxMap::iterator it;
  it = rgxs_.find(name);
  if (it != rgxs_.end())
    return it->second;
  else
    return NULL;
}

// Tokenise on whitespace
const char* TxpTrules::ConsumeWhitespaceToken(const char* input,
                                              std::string* token,
                                              std::string* wspace) {
  TxpPcre pcre;
  TxpUtf8 utf8;
  int32 clen;
  const char *p, *w;
  // Check for initial whitespace
  *wspace = "";
  *token = "";
  w = pcre.Consume(rgxwspace_, input);
  if (w) {
    pcre.SetMatch(0, wspace);
    return w;
  }
  // Go through utf8 chars until we find whitespace
  p = input;
  while (*p) {
    clen = utf8.Clen(p);
    token->append(p, clen);
    // increment to next char
    p += clen;
    w = pcre.Consume(rgxwspace_, p);
    if (w) {
      pcre.SetMatch(0, wspace);
      return w;
    }
  }
  return p;
}

void TxpTrules::ReplaceUtf8Punc(const std::string & tkin,
                                std::string* tkout) {
  const char* p;
  const std::string* r;
  TxpUtf8 utf8;
  int32 clen;
  p = tkin.c_str();
  *tkout = "";
  while (*p) {
    clen = utf8.Clen(p);
    r = Lkp(std::string("utfpunc2ascii"), std::string(p, clen));
    if (r)
      tkout->append(*r);
    else
      tkout->append(p, clen);
    p += clen;
  }
}

const char* TxpTrules::ConsumePunc(const char* input,
                                   std::string* punc) {
  TxpPcre pcre;
  const char* p;
  p = pcre.Consume(rgxpunc_, input);
  if (p) {
    pcre.SetMatch(0, punc);
    return p;
  } else {
    return NULL;
  }
}

const char* TxpTrules::ConsumeToken(const char* input,
                                    std::string* token) {
  TxpPcre pcre;
  const char* p;
  TxpUtf8 utf8;
  int32 clen;
  RgxVector::iterator it;
  // go through token regexes until we match
  for(it = tokrgxs_.begin(); it != tokrgxs_.end(); it++) {
    p = pcre.Consume(*(it), input);
    if (p) {
      pcre.SetMatch(0, token);
      return p;
    } 
  }
  // otherwise throw out the first character as a token
  clen = utf8.Clen(input);
  *token = std::string(input, clen);
  return input + clen;
}


void TxpTrules::NormCaseCharacter(std::string* norm,
                                  TxpTrulesCaseInfo & caseinfo) {
  const char* p;
  const std::string* r;
  std::string c;
  std::string result;
  int32 clen, j = 0;
  bool alpha;
  TxpUtf8 utf8;
  TxpPcre pcre;
  p = norm->c_str();
  while (*p) {
    alpha = false;
    clen = utf8.Clen(p);
    c = std::string(p, clen);
    if (pcre.Execute(GetRgx(std::string("alpha")), c)) {
      alpha = true;
      caseinfo.lowercase = true;
    }
    r = Lkp(std::string("convertillegal"), c);
    if (r) {
      c = *r;
      caseinfo.foreign = true;
      alpha = true;
    }
    r = Lkp(std::string("downcase"), c);
    if (r) {
      caseinfo.uppercase = true;
      alpha = true;
      c = *r;
    }
    if (r && j > 0) caseinfo.capitalised = false;
    if (!r && j == 0) caseinfo.capitalised = false;
    if (!alpha) {
      caseinfo.symbols = true;
      caseinfo.capitalised = false;
    }
    result.append(c);
    p += clen;
    j += 1;
  }
  *norm = result;
}

bool TxpTrules::IsAlpha(const std::string &token) {
  TxpPcre pcre;
  if (pcre.Execute(rgxalpha_, token.c_str())) return true;
  return false;
}

void TxpTrules::StartElement(const char* name, const char** atts) {
  // save name and type for procesing cdata
  if (!strcmp(name, "lookup") || !strcmp(name, "regex")) {
    elementtype_ = name;
    SetAttribute("name", atts, &elementname_);
  }
}

void TxpTrules::EndElement(const char* name) {
}

void TxpTrules::StartCData() {
  cdata_buffer_.clear();
  incdata_ = true;
}

// TODO(MPA): Add checking (i.e. max match on regex, duplications, empty keys)
void TxpTrules::EndCData() {
  const char* error;
  int erroffset;
  incdata_ = false;
  RgxMap::iterator it;
  if (elementtype_ == "lookup") {
    MakeLkp(&lkps_, elementname_, cdata_buffer_);
  } else if (elementtype_ == "regex") {
    if (elementname_.find("token", 0) == 0) {
      tokrgxs_.push_back(pcre_compile(cdata_buffer_.c_str(),
                                      PCRE_UTF8, &error,
                                      &erroffset, NULL));
    } else {
      // if already present replace
      it = rgxs_.find(elementname_);
      if (it != rgxs_.end()) {
        pcre_free(const_cast<pcre *>(it->second));
        rgxs_.erase(it);
      }
      rgxs_.insert(RgxItem(elementname_, pcre_compile(cdata_buffer_.c_str(),
                                                      PCRE_UTF8, &error,
                                                      &erroffset, NULL)));
    }
  }
}

void TxpTrules::CharHandler(const char* data, int32 len) {
  if (incdata_) cdata_buffer_.append(data, len);
}

// private member to format lookup table from xml cdata
int32 TxpTrules::MakeLkp(LookupMapMap *lkps,
                           const std::string &name,
                           const std::string &cdata) {
  TxpPcre pcre;
  int32 pplen;
  std::string key;
  std::string val;
  std::string tmp;
  const char* pp, *npp;

  LookupMapMap::iterator itmap;
  // see if we have already created the LookupMap 
  itmap = lkps->find(name);
  if (itmap != lkps->end()) {
    // if so delete it and replace with the new one
    delete (itmap->second);
    lkps->erase(itmap);
  }
  // add a new lookup table
  lkps->insert(LookupMapItem(name, new LookupMap));
  itmap = lkps->find(name);
  
  pp = cdata.c_str();
  pplen = cdata.length();
  // consume opening {
  pp = pcre.Consume(lkp_open_, pp, pplen);
  // no bracket! ignore
  if (!pp) pp = cdata.c_str();
  while (*pp) {
    npp = pcre.Consume(lkp_item_, pp, pplen);
    if (npp) {
      pcre.SetMatch(1, &key);
      pcre.SetMatch(2, &val);
      (itmap->second)->insert(LookupItem(key, val));
      pplen -= npp - pp;
      pp = npp;
    } else {
      return false;
    }
  }
  return true;
}



}  // namespace kaldi
