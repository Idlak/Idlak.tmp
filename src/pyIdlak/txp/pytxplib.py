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


class PyTxpArgumentParser(argparse.ArgumentParser):
    """ An option parser that combines Python and Idlak parsers """

    def __init__(self, usage):
        super(IdlakArgumentParser, self).__init__(add_help = False, usage= '')
        self._idlakopts = None
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
        pythonargs, idlakargv = super(IdlakArgumentParser, self).parse_known_args(args)
        idlakargv.insert(0, sys.argv[0])
        # Create an Idlak opts parser for the Idlak arguments
        if not self._idlakopts is None:
            pyIdlak_txp.PyTxpParseOptions_delete(self._idlakopts)
        self._idlakopts = pyIdlak_txp.PyTxpParseOptions_new(self._usage + self._get_py_help())
        pyIdlak_txp.PyTxpParseOptions_Read(self._idlakopts, idlakargv)
        return pythonargs, self._idlakopts


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



# utility functions to access wrapped code

# helper functions PyTxpParseOptions
def PyTxpParseOptions_GetOpt(pypo, opt_name):
    configbuf = pyIdlak_txp.PyTxpParseOptions_PrintConfig(pypo)
    configstr = pyIdlak_txp.PyIdlakBuffer_get(configbuf)
    pyIdlak_txp.PyIdlakBuffer_delete(configbuf)
    lines = configstr.split('\n')
    for l in lines:
        pat = re.match("\s*([a-z_\-]+) = '([a-z_\-]+)'\s*", l)
        if pat and pat.group(1) == opt_name:
            return pat.group(2)


def PyTxpParseOptions_GetConfig(pypo):
    configbuf = pyIdlak_txp.PyTxpParseOptions_PrintConfig(pypo)
    configstr = pyIdlak_txp.PyIdlakBuffer_get(configbuf)
    pyIdlak_txp.PyIdlakBuffer_delete(configbuf)
    lines = configstr.split('\n')
    config = {}
    for l in lines:
        pat = re.match("\s*([a-z_\-]+) = '([a-z_\-]*)'\s*", l)
        if pat:
            config[pat.group(1)] = pat.group(2)
    return config
