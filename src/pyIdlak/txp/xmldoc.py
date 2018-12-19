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


import copy

from ..pylib import c_api as pyIdlak_pylib
from . import pyIdlak_txp

class XMLDoc(object):

    def __init__(self, xmlstr = None):
        """ If initialised with text will automatically load """
        self._doc = pyIdlak_txp.PyPugiXMLDocument_new()
        if type(xmlstr) == str:
            self.load_string(xmlstr)


    def __del__(self):
        """ Clean up underlying memory """
        if not self._doc is None:
            pyIdlak_txp.PyPugiXMLDocument_delete(self._doc)


    def load_string(self, xmlstr):
        """ Loads a string containing XML """
        pyIdlak_txp.PyPugiXMLDocument_LoadString(self._doc, str(xmlstr))


    def to_string(self):
        """ Get the XML in string format """
        buf = pyIdlak_txp.PyPugiXMLDocument_SavePretty(self._doc)
        xmlstr = copy.copy(pyIdlak_pylib.PyIdlakBuffer_get(buf))
        pyIdlak_pylib.PyIdlakBuffer_delete(buf)
        return xmlstr

    @property
    def idlak_doc(self):
        """ Get the underlying Idlak PugiXML document """
        return self._doc
