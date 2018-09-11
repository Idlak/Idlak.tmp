#!/usr/bin/env python3
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


import os
import sys

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

    # Create an Idlak option parser & parse the command line
    args = txp.TxpArgumentParser(usage = USAGE)

    args.add_argument("--cex", action='store_true',
            help = "Add linguistic context extraction features for TTS synthesis")

    args.parse_args()

    # Check that the input and output have been specified
    if args.no_args != 2:
        sys.stderr.write("Script requires extactly 2 arguments\n")
        args.print_usage()
        sys.exit(1)

    filein = args.get_arg(1)
    fileout = args.get_arg(2)

    # Initialise all the modules that will be run
    modules = []
    modules.append(txp.modules.Tokenise(args))
    modules.append(txp.modules.PosTag(args))
    modules.append(txp.modules.Normalise(args))
    modules.append(txp.modules.Norm_Tokenise(args))
    modules.append(txp.modules.Pauses(args))
    modules.append(txp.modules.Phrasing(args))
    modules.append(txp.modules.Pronounce(args))
    modules.append(txp.modules.Syllabify(args))
    if args.get('cex'):
        modules.append(txp.modules.ContextExtraction(args))

    # Create an Idlak XML document
    if filein == '-':
        inputxml = sys.stdin.read()
    else:
        if not os.path.isfile(filein):
            sys.stderr.write("Can't open input XML file '{0}\n".format(filein))
            sys.exit(1)
        else:
            inputxml = open(filein).read()

    doc = txp.XMLDoc(inputxml)

    # Run the modules over it in order
    for txp_module in modules:
        txp_module.process(doc)

    # Output generated XML
    if fileout == '-':
        sys.stdout.write(doc.to_string())
    else:
        with open(fileout, 'w') as fp:
            fp.write(doc.to_string())


if __name__ == "__main__":
    main()
