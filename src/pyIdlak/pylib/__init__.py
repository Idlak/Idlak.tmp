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

# SWIG wrapped API
from . import pyIdlak_pylib as c_api

from .pyIdlak_pylib import (
        NONE,
        AperiodicEnergyOptions,
        PdfPriorOptions,
        NnetForwardOptions,
        ApplyCMVNOptions,
        DeltaFeaturesOptions,
        PyReadKaldiDoubleMatrix,
        PyKaldiMatrixBaseFloat_frmlist,
        PyKaldiMatrixBaseFloat_tolist,
        PyKaldiMatrixDouble_frmlist,
        PyKaldiMatrixDouble_tolist
    )

from .pyoptions import PyOptions

from .utils import (
        get_rspecifier_keys,
        get_matrix_by_key,
    )
