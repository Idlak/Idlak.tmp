#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2018 Cereproc Ltd. (author: Matthew Aylett)
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

# load pyidlak python library
import sys, os, argparse, re
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
import pyIdlak

USAGE = """
Normalise xml input text
Usage: python pyidlaktxp.py [options] xml_input xml_output\n"
     e.g.: python pyidlaktxp.py --cex --tpdb=../../idlak-data --general-lang=en --general-acc=ga ../../src/idlaktxp/test_data/mod-test001.xml output.xml
     e.g.: cat  ../../src/idlaktxp/test_data/mod-test001.xml | python pyidlaktxp.py --pretty --tpdb=../../idlak-data --general-lang=en --general-acc=ga - - > output.xml
"""

PYTHONUSAGE = ""

PYTHONOPTS = ['--cex']

# python only expects options in form --opt[=xxx]
def split_args():
    idlak = [sys.argv[0]]
    python = []
    for a in sys.argv[1:]:
        opt = re.match("^(--[a-zA-Z]+).*", a)
        if opt:
            if opt.group(1) in PYTHONOPTS:
                python.append(a)
            else:
                idlak.append(a)
        else:
            idlak.append(a)
    return python, idlak

def main():
    # remove python opts from argv
    pythonargv, idlakargv = split_args()
    # create a python opts parser to deal with python arguments
    arg_parser = argparse.ArgumentParser(
            description="Python arguments type --help to see Idlak options")
    arg_parser.add_argument(
        "--cex",
        action='store_true',
        help="Add linguistic context extraction features for TTS sythesis")
    pythonargs = vars(arg_parser.parse_args(pythonargv))

    # create an Idlak opts parser for the Idlak arguments
    opts = pyIdlak.PyTxpParseOptions_new(USAGE)
    pyIdlak.PyTxpParseOptions_Read(opts, idlakargv)
    if pyIdlak.PyTxpParseOptions_NumArgs(opts) < 2:
        pyIdlak.PyTxpParseOptions_PrintUsage(opts)
        print 'PYTHON USAGE'
        arg_parser.print_usage()
        sys.exit()
        
    filein = pyIdlak.PyTxpParseOptions_GetArg(opts, 1)
    fileout = pyIdlak.PyTxpParseOptions_GetArg(opts, 2)

    # initialise all the modules
    modules = []
    modules.append(pyIdlak.PyIdlakModule_new(pyIdlak.Tokenise, opts))
    modules.append(pyIdlak.PyIdlakModule_new(pyIdlak.PosTag, opts))
    modules.append(pyIdlak.PyIdlakModule_new(pyIdlak.Pauses, opts))
    modules.append(pyIdlak.PyIdlakModule_new(pyIdlak.Phrasing, opts))
    modules.append(pyIdlak.PyIdlakModule_new(pyIdlak.Pronounce, opts))
    modules.append(pyIdlak.PyIdlakModule_new(pyIdlak.Syllabify, opts))
    if pythonargs['cex']:
        modules.append(pyIdlak.PyIdlakModule_new(pyIdlak.ContextExtraction, opts))

    # create a Pugi XML document
    doc = pyIdlak.PyPugiXMLDocument_new()
    if filein == '-':
        input = sys.stdin.read()
    else:
        if not os.path.isfile(filein):
            print "Can't open input XML file"
            sys.exit()
        else:
            input = open(filein).read()
    pyIdlak.PyPugiXMLDocument_LoadString(doc, input)

    # run the modules over it in order
    for m in modules:
        pyIdlak.PyIdlakModule_process(m, doc)
    # output XMl generated
    buf = pyIdlak.PyPugiXMLDocument_SavePretty(doc)
    if fileout == '-':
        sys.stdout.write(pyIdlak.PyIdlakBuffer_get(buf))
    else:
        fp = open(fileout, 'w')
        fp.write(pyIdlak.PyIdlakBuffer_get(buf))
        
    # clean up    
    pyIdlak.PyTxpParseOptions_delete(opts)
    pyIdlak.PyPugiXMLDocument_delete(doc)
    for m in modules:
        pyIdlak.PyIdlakModule_delete(m)
    
if __name__ == "__main__":
    main()
