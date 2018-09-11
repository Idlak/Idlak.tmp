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


# Automatically generate the C++ modules (add the python modules at the end of file)

from . import pyIdlak_txp
from . import idargparse
from . import xmldoc

class CppTxpModule(object):
    """ Base class for the TxpModules that have underlying
        C++ versions

        The factory must set the _modidx and _modname
    """
    def __init__(self, idargs):
        """ Uses underlying C api to create a module """
        if type(idargs) != idargparse.TxpArgumentParser:
            raise ValueError("idargs must be a TxpArgumentParser")
        self._mod = pyIdlak_txp.PyIdlakModule_new(self._modidx, idargs.idlakopts)


    def __del__(self):
        """ Free C memory """
        pyIdlak_txp.PyIdlakModule_delete(self._mod)


    def process(self, doc):
        """ process the document in place """
        if not type(doc) is xmldoc.XMLDoc:
            raise ValueError("doc must be a XMLDoc")

        pyIdlak_txp.PyIdlakModule_process(self._mod, doc.idlak_doc)


    @property
    def name(self):
        """ Gets the name of the module """
        return self._modname


def _module_factory(modidx):
    modname = pyIdlak_txp.PyIdlakModule_name(modidx)
    new_module = type(modname, (CppTxpModule,),
                        {"_modidx" : modidx,
                         "_modname" : modname})
    return new_module


for _i in range(pyIdlak_txp.Empty, pyIdlak_txp.NumMods+1):
    if _i == pyIdlak_txp.Empty:
        continue
    _modcls = _module_factory(_i)
    # This puts the class name into the namespace so that
    #   it can be accessed by e.g. pyIdlak.txp.modules.Tokenise
    globals()[_modcls.__name__] = _module_factory(_i)


# Add Python modules here

from .normaliser.normaliser import Normalise
from .normaliser.norm_tokeniser import Norm_Tokenise
