// cudamatrix/cu-value.h

// Copyright      2013  Johns Hopkins University (author: Daniel Povey)

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//  http://www.apache.org/licenses/LICENSE-2.0
//
// THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
// WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
// MERCHANTABLITY OR NON-INFRINGEMENT.
// See the Apache 2 License for the specific language governing permissions and
// limitations under the License.



#ifndef KALDI_CUDAMATRIX_CU_VALUE_H_
#define KALDI_CUDAMATRIX_CU_VALUE_H_

#include <cudamatrix/cu-device.h>

namespace kaldi {

/// The following class is used to simulate non-const
/// references to Real, e.g. as returned by the non-const operator ().
/// Note: this class uses the default assignment and constructor
/// operators.  This class is also used as a convenient way of
/// reading a single Real value from the device.
template<class Real>
class CuValue {
 public:
  CuValue(Real *data): data_(data) { }
  inline Real operator = (Real r) { // assignment from Real
#if HAVE_CUDA == 1
    if (CuDevice::Instantiate().Enabled()) {
      CU_SAFE_CALL(cudaMemcpy(data_, &r, sizeof(Real), cudaMemcpyHostToDevice));
      return r;
    } else
#endif
    {
      *data_ = r;
      return r;
    }
  }
  inline operator Real () const { // assignment to Real
#if HAVE_CUDA == 1
  if (CuDevice::Instantiate().Enabled()) {
    Real value;
    CU_SAFE_CALL(cudaMemcpy(&value, data_,
                            sizeof(Real), cudaMemcpyDeviceToHost));
    return value;
  } else
#endif
    return *data_;
  }
 private:
  Real *data_;
}; // class CuValue<Real>


}  // namespace



#endif  // KALDI_CUDAMATRIX_CU_VALUE_H_
