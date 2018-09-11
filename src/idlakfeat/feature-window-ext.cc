// idlakfeat/feature-window-ext.cc

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

#include "idlakfeat/feature-window-ext.h"

namespace kaldi {

void ExtractWaveformRemainder(const VectorBase<BaseFloat> &wave,
                              const FrameExtractionOptions &opts,
                              Vector<BaseFloat> *wave_remainder) {
  int32 frame_shift = opts.WindowShift();
  int32 num_frames = NumFrames(wave.Dim(), opts);
  // offset is the amount at the start that has been extracted.
  int32 offset = num_frames * frame_shift;
  KALDI_ASSERT(wave_remainder != NULL);
  int32 remaining_len = wave.Dim() - offset;
  wave_remainder->Resize(remaining_len);
  KALDI_ASSERT(remaining_len >= 0);
  if (remaining_len > 0)
    wave_remainder->CopyFromVec(SubVector<BaseFloat>(wave, offset, remaining_len));
}

}  // namespace kaldi