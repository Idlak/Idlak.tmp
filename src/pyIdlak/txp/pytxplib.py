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
import pyIdlak_txp

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
