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

import sys, os, re

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
    arg_parser = txp.TxpArgumentParser(usage = USAGE)

    arg_parser.add_argument("--cex", action='store_true',
            help = "Add linguistic context extraction features for TTS synthesis")

    pythonargv, opts = arg_parser.parse_args()
    pythonargs = vars(pythonargv)

    #create an Idlak opts parser for the Idlak arguments
    if arg_parser.no_args != 2:
        sys.stderr.write("Script requires extactly 2 arguments\n")
        arg_parser.print_usage()
        sys.exit(1)

    filein = arg_parser.get_arg(1)
    fileout = arg_parser.get_arg(2)

    # initialise all the modules
    modules = []
    modules.append(txp.modules.Tokenise(arg_parser))
    modules.append(txp.modules.PosTag(arg_parser))
    modules.append(txp.modules.Pauses(arg_parser))
    modules.append(txp.modules.Phrasing(arg_parser))
    modules.append(txp.modules.Pronounce(arg_parser))
    modules.append(txp.modules.Syllabify(arg_parser))
    if pythonargs['cex']:
        modules.append(txp.modules.ContextExtraction(arg_parser))

    # create a Pugi XML document
    doc = txp.c_api.PyPugiXMLDocument_new()
    if filein == '-':
        inputxml = sys.stdin.read()
    else:
        if not os.path.isfile(filein):
            print "Can't open input XML file"
            sys.exit(1)
        else:
            inputxml = open(filein).read()
    txp.c_api.PyPugiXMLDocument_LoadString(doc, inputxml)

    # run the modules over it in order1
    for m in modules:
        m.process(doc)

    # output generated XML
    buf = txp.c_api.PyPugiXMLDocument_SavePretty(doc)
    if fileout == '-':
        sys.stdout.write(txp.c_api.PyIdlakBuffer_get(buf))
    else:
        with open(fileout, 'w') as fp:
            fp.write(txp.c_api.PyIdlakBuffer_get(buf))

    # clean up
    txp.c_api.PyPugiXMLDocument_delete(doc)

if __name__ == "__main__":
    main()
