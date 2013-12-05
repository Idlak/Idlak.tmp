#!/bin/bash

# This is neural net training on top of adapted 40-dimensional features.
# This version of the script uses GPUs.  We distinguish it by putting "_gpu"
# at the end of the directory name.
#
# Since we're using one quarter the number of jobs (num-jobs-nnet) as the
# run_4c.sh script, we halve the learning rate (generally speaking, splitting
# the difference like this is probably a good idea.)


parallel_opts="-l gpu=1,hostname=g*"  # This is suitable for the CLSP network, you'll likely have to change it.

. cmd.sh

dir=exp/nnet4c_gpu_pnorm_lr016004_dim1200600
(  steps/nnet2/train_pnorm.sh  --num-epochs 20 \
     --num-jobs-nnet 4 --num-threads 1 --parallel-opts "$parallel_opts" \
     --num-epochs-extra 10 --add-layers-period 1 \
     --num-hidden-layers 2 \
     --mix-up 4000 \
     --initial-learning-rate 0.016 --final-learning-rate 0.004 \
     --cmd "$decode_cmd" \
     --pnorm-input-dim 1200 \
     --pnorm-output-dim 600 \
     --stage -5 \
     data/train data/lang exp/tri3b_ali $dir 

   steps/nnet2/decode.sh --config conf/decode.config --cmd "$decode_cmd" --nj 20 \
     --transform-dir exp/tri3b/decode \
     exp/tri3b/graph data/test $dir/decode 

   steps/nnet2/decode.sh --config conf/decode.config --cmd "$decode_cmd" --nj 20 \
     --transform-dir exp/tri3b/decode_ug \
     exp/tri3b/graph_ug data/test $dir/decode_ug

)


