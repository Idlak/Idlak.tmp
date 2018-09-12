# -*- coding: utf-8 -*-
# Copyright 2018 Cereproc Ltd. (author: Matthew Aylett
#                                       David Braude
#                                       Skaiste Butkute)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License.

# Tokeniser after normalising
from lxml import etree, objectify
from copy import deepcopy
from .. import idargparse, xmldoc, pyIdlak_txp, pytxplib


def splitNormalised(token):
    nnorm = token.get('nnorm')
    words = []
    if nnorm is not None:
        words = nnorm.split()

    if len(words) == 0:
        if 'prepunc' in token.attrib and token.getnext() is not None:
            token.getnext().set('prepunc', token.get('prepunc'))
        if 'pstpunc' in token.attrib and token.getprevious() is not None:
            token.getprevious().set('pstpunc', token.get('pstpunc'))
        token.getparent().remove(token)
        return

    elif len(words) == 1:
        token.set('norm', nnorm)
        token.attrib.pop('nnorm')
        return
    # replace the original token norm with first word
    token.set('norm', words[0])
    # remove the nnorm attribute
    token.attrib.pop('nnorm')
    # go through the rest of the list and save as separate tokens
    tk_parent = token.getparent()
    last_index = tk_parent.index(token)
    for w in words[1:]:
        # make a copy of original token
        new_tk = deepcopy(token)
        new_tk.set('norm', w)
        new_tk.text = ""
        if 'prepunc' in new_tk.attrib:
            new_tk.attrib.pop('prepunc')
        # append it after the previous token
        tk_parent.insert(last_index+1, new_tk)
        last_index = tk_parent.index(new_tk)


class Norm_Tokenise(object):

    def __init__(self, idargs):
        if type(idargs) != idargparse.TxpArgumentParser:
            raise ValueError("idargs must be a TxpArgumentParser")

    def process(self, doc):
        """ process the document in place """
        if not type(doc) is xmldoc.XMLDoc:
            raise ValueError("doc must be a XMLDoc")

        # xmldoc to lxml
        strin = doc.to_string()
        xmlin = etree.fromstring(strin)

        tokens = xmlin.xpath('.//tk|.//break')
        for t in tokens:
            splitNormalised(t)

        # lxml to xmldoc
        strout = str(etree.tostring(xmlin, encoding='utf8').decode('utf8'))
        doc.load_string(strout)
