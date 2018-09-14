// idlakfeat/feature-window-ext.h

// Copyright 2018  CereProc Ltd. (author: David Braude)

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

#ifndef SRC_IDLAKFEAT_FEATURE_WINDOW_EXT_H_
#define SRC_IDLAKFEAT_FEATURE_WINDOW_EXT_H_

#include <map>
#include <string>

#include "matrix/matrix-lib.h"
#include "util/common-utils.h"
#include "base/kaldi-error.h"
#include "feat/feature-window.h"

namespace kaldi {

// ExtractWaveformRemainder is useful if the waveform is coming in segments.
// It extracts the bit of the waveform at the end of this block that you
// would have to append the next bit of waveform to, if you wanted to have
// the same effect as everything being in one big block.
// NOTE: This was removed from Kaldi, but we have not yet refactored it out
void ExtractWaveformRemainder(const VectorBase<BaseFloat> &wave,
                              const FrameExtractionOptions &opts,
                              Vector<BaseFloat> *wave_remainder);

}  // namespace kaldi

#endif //SRC_IDLAKFEAT_FEATURE_WINDOW_EXT_H_