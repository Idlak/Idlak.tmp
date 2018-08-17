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

import re
import sys
import copy
import cStringIO
import argparse

import pyIdlak_txp
import pytxplib

class TxpArgumentParser(argparse.ArgumentParser):
    """ An option parser that combines Python and Idlak parsers """

    def __init__(self, usage):
        super(TxpArgumentParser, self).__init__(add_help = False, usage= '')
        self._idlakopts = None
        self._pythonargs = None
        self._usage = copy.copy(usage)


    def __del__(self):
        """ Clean up the txp option parser """
        if not self._idlakopts is None:
            pyIdlak_txp.PyTxpParseOptions_delete(self._idlakopts)
            self._idlakopts = None


    def parse_args(self, *args):
        """ Parse the args or if none parse the commandline """
        if not args:
            args = None
        self._pythonargs, idlakargv = super(TxpArgumentParser, self).parse_known_args(args)
        idlakargv.insert(0, sys.argv[0])
        # Create an Idlak opts parser for the Idlak arguments
        if not self._idlakopts is None:
            pyIdlak_txp.PyTxpParseOptions_delete(self._idlakopts)
        self._idlakopts = pyIdlak_txp.PyTxpParseOptions_new(self._usage + self._get_py_help())
        pyIdlak_txp.PyTxpParseOptions_Read(self._idlakopts, idlakargv)
        return self._pythonargs, self._idlakopts


    def _get_py_help(self):
        """ Gets the python help """
        _stdout = sys.stdout
        _stringio = cStringIO.StringIO()
        sys.stdout = _stringio
        self.print_help()
        usage = _stringio.getvalue()
        _stringio.close()
        sys.stdout = _stdout
        return usage


    def get(self, opt_name, default = None):
        """ Returns an option from the appropriate parser """

        if type(opt_name) != str:
            raise ValueError('opt_name is not str')

        if not self._pythonargs is None:
            if opt_name in vars(self._pythonargs):
                return vars(self._pythonargs)[opt_name]

        if not self._idlakopts is None:
            val = pytxplib.PyTxpParseOptions_GetOpt(self._idlakopts, opt_name)
            if not val is None:
                return val

        return default


    def get_idlak_config(self):
        """ Gets the Idlak configuration """
        if not self._idlakopts is None:
            return pytxplib.PyTxpParseOptions_GetConfig(self._idlakopts)
        return {}


    @property
    def no_args(self):
        """ Gets the number of arguments after the the two parsers have run """
        if not self._idlakopts is None:
            return pyIdlak_txp.PyTxpParseOptions_NumArgs(self._idlakopts)
        return 0

    @property
    def idlakopts(self):
        return self._idlakopts

    def get_arg(self, argidx):
        """ Gets a unprocessed argument by index """
        if type(argidx) != int:
            raise ValueError('argidx is not int')
        if argidx > self.no_args:
            raise IndexError('argidx is out of range')

        if not self._idlakopts is None:
            return pyIdlak_txp.PyTxpParseOptions_GetArg(self._idlakopts, argidx)

        return None


    def print_usage(self):
        """ Prints the usage statement """
        pyIdlak_txp.PyTxpParseOptions_PrintUsage(self._idlakopts)




