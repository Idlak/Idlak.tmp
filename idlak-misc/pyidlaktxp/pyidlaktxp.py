#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2018 Cereproc Ltd. (author: Matthew Aylett
#                                       David Braude )
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

# Python wrapped version of idlaktxp

import sys, os, argparse, re, cStringIO

# load pyidlak python library
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
from pyIdlak import txp

USAGE = """
Normalise xml input text
Usage: ./pyidlaktxp.py [options] xml_input xml_output\n"
     e.g.: ./pyidlaktxp.py --cex --tpdb=../../idlak-data --general-lang=en --general-acc=ga ../../src/idlaktxp/test_data/mod-test001.xml output.xml
     e.g.: cat  ../../src/idlaktxp/test_data/mod-test001.xml | ./pyidlaktxp.py --tpdb=../../idlak-data --general-lang=en --general-acc=ga - - > output.xml
"""


def main():

    # create a python opts parser to deal with python arguments
    arg_parser = txp.PyTxpArgumentParser(usage = USAGE)

    arg_parser.add_argument("--cex", action='store_true',
            help = "Add linguistic context extraction features for TTS synthesis")

    pythonargv, opts = arg_parser.parse_args()
    pythonargs = vars(pythonargv)

    #create an Idlak opts parser for the Idlak arguments
    if txp.PyTxpParseOptions_NumArgs(opts) < 2:
        sys.stderr.write("Error processing arguments:\n")
        txp.PyTxpParseOptions_PrintUsage(opts)
        sys.exit(1)

    filein = txp.PyTxpParseOptions_GetArg(opts, 1)
    fileout = txp.PyTxpParseOptions_GetArg(opts, 2)

    # initialise all the modules
    modules = []
    modules.append(txp.PyIdlakModule_new(txp.Tokenise, opts))
    modules.append(txp.PyIdlakModule_new(txp.PosTag, opts))
    modules.append(txp.PyIdlakModule_new(txp.Pauses, opts))
    modules.append(txp.PyIdlakModule_new(txp.Phrasing, opts))
    modules.append(txp.PyIdlakModule_new(txp.Pronounce, opts))
    modules.append(txp.PyIdlakModule_new(txp.Syllabify, opts))
    if pythonargs['cex']:
        modules.append(txp.PyIdlakModule_new(txp.ContextExtraction, opts))

    # create a Pugi XML document
    doc = txp.PyPugiXMLDocument_new()
    if filein == '-':
        inputxml = sys.stdin.read()
    else:
        if not os.path.isfile(filein):
            print "Can't open input XML file"
            sys.exit(1)
        else:
            inputxml = open(filein).read()
    txp.PyPugiXMLDocument_LoadString(doc, inputxml)

    # run the modules over it in order1
    for m in modules:
        txp.PyIdlakModule_process(m, doc)

    # output generated XML
    buf = txp.PyPugiXMLDocument_SavePretty(doc)
    if fileout == '-':
        sys.stdout.write(txp.PyIdlakBuffer_get(buf))
    else:
        with open(fileout, 'w') as fp:
            fp.write(txp.PyIdlakBuffer_get(buf))

    # clean up
    txp.PyPugiXMLDocument_delete(doc)
    for m in modules:
        txp.PyIdlakModule_delete(m)

if __name__ == "__main__":
    main()
