# -*- coding: utf-8 -*-
# Copyright 2018 Cereproc Ltd. (author: David Braude)
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
import io
import argparse

from . import pyIdlak_txp
from . import pytxplib

class TxpArgumentParser(argparse.ArgumentParser):
    """ An option parser that combines Python and Idlak parsers """

    def __init__(self, usage):

        self._idlakopts = None
        self._pythonargs = None
        self._usage = copy.copy(usage)

        iopts = pyIdlak_txp.PyTxpParseOptions_new("")
        default_config = pytxplib.PyTxpParseOptions_GetConfig(iopts)
        pyIdlak_txp.PyTxpParseOptions_delete(iopts)
        epilog = "Idlak TXP arguments:\n"
        for k, v in default_config.items():
            epilog += '  --{0:30}  default: "{1}"\n'.format(k, v)

        super(TxpArgumentParser, self).__init__(
            usage = usage,
            epilog = epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter,)

        # getting a list of idlak options and saving them into
        # the parser so they cannot be duplicated by accident
        # The help message is a bit unclear so it has been removed
        # and manually created in the epilog
        self._idlakargs = {}
        self._default_config = {}
        idlak_arg_group = self.add_argument_group()
        for k, v in default_config.items():
            argname = '--' + k
            dest = k.replace('-','_')
            self._idlakargs[dest] = argname
            self._default_config[dest] = v
            idlak_arg_group.add_argument(argname, default = v, dest = dest,
                                         help=argparse.SUPPRESS)


    def __del__(self):
        """ Clean up the txp option parser """
        if not self._idlakopts is None:
            pyIdlak_txp.PyTxpParseOptions_delete(self._idlakopts)
            self._idlakopts = None


    def parse_args(self, *args):
        """ Parse the args or if none parse the commandline """
        if not args:
            args = None
        super(TxpArgumentParser, self).parse_known_args(args)
        self._pythonargs, idlakargv = super(TxpArgumentParser, self).parse_known_args(args)
        idlak_args = [sys.argv[0]]
        for dest, argname in self._idlakargs.items():
            if vars(self._pythonargs)[dest] != self._default_config[dest]:
                idlak_args.append('{0}={1}'.format(argname, vars(self._pythonargs)[dest]))
        idlak_args += idlakargv
        if not self._idlakopts is None:
            pyIdlak_txp.PyTxpParseOptions_delete(self._idlakopts)
        self._idlakopts = pyIdlak_txp.PyTxpParseOptions_new("")
        pyIdlak_txp.PyTxpParseOptions_Read(self._idlakopts, idlak_args)

        return self._pythonargs, self._idlakopts



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



