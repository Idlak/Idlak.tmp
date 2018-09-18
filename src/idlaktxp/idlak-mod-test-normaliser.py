#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 Cereproc Ltd. (author: Matthew Aylett
#                                       David Braude
#                                       Skaiste Butkute )
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

# This python scripts runs the normaliser, provided with output from postag

import os
import sys
from optparse import OptionParser
from lxml import etree
# load normaliser python library
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from pyIdlak.txp.normaliser.normaliser import Normrules, splitNormalised, loadhrules

def main():
    # from parameters get rule directory
    parser = OptionParser()
    parser.add_option("-t", "--tpdb", default="../../idlak-data/")
    parser.add_option("-l", "--lang", default="en")
    parser.add_option("-a", "--acc", default="ga")
    parser.add_option("-i", "--input")
    parser.add_option("-o", "--output")
    opts, args = parser.parse_args()

    if not opts.input:
        parser.error("Input filename required")
    if not opts.output:
        parser.error("Output filename required")

    xmlin = etree.parse(opts.input)
    ruledir = os.path.join(opts.tpdb, opts.lang, "normrules-default")
    hrules_fn = os.path.join(opts.tpdb, opts.lang, "hrules-default.py")
    hrules = loadhrules(hrules_fn)

    normrules = Normrules(ruledir, hrules)
    tokens = xmlin.xpath('.//tk|.//break')
    normrules.runrulesets(tokens)

    for tk in tokens:
        if 'norm' not in tk.attrib and 'tknorm' in tk.attrib:
            tk.set('norm', tk.get('tknorm'))
        splitNormalised(tk)

    xmlin.write(opts.output, pretty_print=True, xml_declaration=True,   encoding="utf-8")

if __name__ == "__main__":
    main()
