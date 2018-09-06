# -*- coding: utf-8 -*-
# Copyright 2018 Cereproc Ltd. (author: Matthew Aylett,
#                                       David Braude)
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
import argparse

from ..pylib import c_api as pyIdlak_pylib
from . import pyIdlak_txp



# helper functions PyTxpParseOptions
def PyTxpParseOptions_GetOpt(pypo, opt_name):
    return pyIdlak_txp.PyTxpParseOptions_value(pypo, opt_name)

def PyTxpParseOptions_GetConfig(pypo):
    keys = pyIdlak_txp.PyTxpParseOptions_keys(pypo)
    config = {}
    for k in keys:
      config[k] = pyIdlak_txp.PyTxpParseOptions_value(pypo, k)
    return config
