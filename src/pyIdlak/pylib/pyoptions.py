# -*- coding: utf-8 -*-
# Copyright 2018 Cereproc Ltd. (author: Matthew Aylett
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

# Note that this is intended to be internal to pyIdlak and not exposed.

import pydoc
from . import pyIdlak_pylib as c_api

class PyOptions:

    def __init__(self, opttype = c_api.NONE):
        """ Create a Kaldi options object """
        self._pyopts = c_api.PySimpleOptions_new(opttype)
        self._types = {}
        names = c_api.PySimpleOptions_option_names(self._pyopts)
        for n in names:
            opttype = c_api.PySimpleOptions_option_pytype(self._pyopts, n)
            self._types[n] = pydoc.locate(opttype)


    def get(self, key):
        """ Get a value from the Kaldi option object """
        if key not in self._types:
            raise KeyError(key)

        opttype = self._types[key]
        if opttype == str:
            found, val = c_api.PySimpleOptions_get_string(self._pyopts, key)
        else:
            found, val = c_api.PySimpleOptions_get_numeric(self._pyopts, key)

        if found:
            return opttype(val)
        else:
            raise KeyError(key)


    def set(self, key, val):
        """ Set a value in the Kalsi options object """
        if key not in self._types:
            raise KeyError(key)

        opttype = self._types[key]
        v = opttype(val)
        if opttype == str:
            success = c_api.PySimpleOptions_set_str(self._pyopts, key, v)
        elif opttype == float:
            success = c_api.PySimpleOptions_set_float(self._pyopts, key, v)
        elif opttype == int:
            success = c_api.PySimpleOptions_set_int(self._pyopts, key, v)
        elif opttype == bool:
            success = c_api.PySimpleOptions_set_bool(self._pyopts, key, v)

        if not success:
            raise KeyError(key)

    @property
    def kaldiopts(self):
        """ Get the C wrapper structure """
        return self._pyopts

    @property
    def options(self):
        """ List of available options """
        return list(self._types.keys())

    def __del__(self):
        c_api.PySimpleOptions_delete(self._pyopts)