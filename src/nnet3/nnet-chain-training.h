// nnet3/nnet-chain-training.h

// Copyright    2015  Johns Hopkins University (author: Daniel Povey)

// See ../../COPYING for clarification regarding multiple authors
//
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

#ifndef KALDI_NNET3_NNET_CHAIN_TRAINING_H_
#define KALDI_NNET3_NNET_CHAIN_TRAINING_H_

#include "nnet3/nnet-example.h"
#include "nnet3/nnet-computation.h"
#include "nnet3/nnet-compute.h"
#include "nnet3/nnet-optimize.h"
#include "nnet3/nnet-chain-example.h"
#include "nnet3/nnet-training.h"

namespace kaldi {
namespace nnet3 {


/**
   This class is for single-threaded training of neural nets using the 'chain'
   model.
*/
class NnetChainTrainer {
 public:
  NnetChainTrainer(const NnetTrainerOptions &nnet_config,
                   const chain::ChainTrainingOptions &chain_config,
                   const fst::StdVectorFst &den_fst,
                   Nnet *nnet);

  // train on one minibatch.
  void Train(const NnetChainExample &eg);

  // Prints out the final stats, and return true if there was a nonzero count.
  bool PrintTotalStats() const;

  ~NnetChainTrainer();
 private:
  void ProcessOutputs(const NnetChainExample &eg,
                      NnetComputer *computer);

  const NnetTrainerOptions nnet_config_;
  const chain::ChainTrainingOptions chain_config_;
  chain::ChainDenGraph den_graph_;
  CuMatrix<BaseFloat> cu_weights_;  // derived from trans_model_.
  Nnet *nnet_;
  Nnet *delta_nnet_;  // Only used if momentum != 0.0.  nnet representing
                      // accumulated parameter-change (we'd call this
                      // gradient_nnet_, but due to natural-gradient update,
                      // it's better to consider it as a delta-parameter nnet.
  CachingOptimizingCompiler compiler_;

  // This code supports multiple output layers, even though in the
  // normal case there will be just one output layer named "output".
  // So we store the objective functions per output layer.
  int32 num_minibatches_processed_;

  unordered_map<std::string, ObjectiveFunctionInfo, StringHasher> objf_info_;
};


} // namespace nnet3
} // namespace kaldi

#endif // KALDI_NNET3_NNET_CHAIN_TRAINING_H_
