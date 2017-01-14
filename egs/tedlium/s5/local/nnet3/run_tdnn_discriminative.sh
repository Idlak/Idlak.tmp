#!/bin/bash

# This script does discriminative training on top of CE nnet3 system.
# note: this relies on having a cluster that has plenty of CPUs as well as GPUs,
# since the lattice generation runs in about real-time, so takes of the order of
# 1000 hours of CPU time.
#

#%WER 13.3 | 507 17792 | 89.1 8.2 2.8 2.4 13.3 86.0 | -0.207 | exp/nnet3/tdnn_smbr/decode_dev_epoch1.adj/score_12_1.0/ctm.filt.filt.sys
#%WER 12.4 | 507 17792 | 89.8 7.5 2.7 2.2 12.4 85.4 | -0.305 | exp/nnet3/tdnn_smbr/decode_dev_epoch1.adj_rescore/score_12_1.0/ctm.filt.filt.sys
#%WER 13.1 | 507 17792 | 89.2 8.0 2.8 2.3 13.1 85.4 | -0.244 | exp/nnet3/tdnn_smbr/decode_dev_epoch2.adj/score_13_1.0/ctm.filt.filt.sys
#%WER 12.4 | 507 17792 | 89.7 7.5 2.8 2.1 12.4 84.0 | -0.336 | exp/nnet3/tdnn_smbr/decode_dev_epoch2.adj_rescore/score_13_1.0/ctm.filt.filt.sys
#%WER 13.2 | 507 17792 | 89.2 8.1 2.7 2.4 13.2 85.8 | -0.332 | exp/nnet3/tdnn_smbr/decode_dev_epoch3.adj/score_13_1.0/ctm.filt.filt.sys
#%WER 12.5 | 507 17792 | 89.9 7.8 2.4 2.4 12.5 85.2 | -0.391 | exp/nnet3/tdnn_smbr/decode_dev_epoch3.adj_rescore/score_14_0.5/ctm.filt.filt.sys
#%WER 13.4 | 507 17792 | 88.9 8.3 2.7 2.4 13.4 86.0 | -0.342 | exp/nnet3/tdnn_smbr/decode_dev_epoch4.adj/score_13_1.0/ctm.filt.filt.sys
#%WER 12.7 | 507 17792 | 89.3 7.7 3.0 2.1 12.7 84.4 | -0.427 | exp/nnet3/tdnn_smbr/decode_dev_epoch4.adj_rescore/score_16_1.0/ctm.filt.filt.sys
#%WER 12.4 | 1155 27512 | 89.4 7.9 2.7 1.7 12.4 80.1 | -0.163 | exp/nnet3/tdnn_smbr/decode_test_epoch1.adj/score_13_1.0/ctm.filt.filt.sys
#%WER 11.4 | 1155 27512 | 90.5 6.9 2.6 2.0 11.4 78.9 | -0.269 | exp/nnet3/tdnn_smbr/decode_test_epoch1.adj_rescore/score_13_0.5/ctm.filt.filt.sys
#%WER 12.6 | 1155 27512 | 89.4 8.0 2.6 2.0 12.6 81.4 | -0.190 | exp/nnet3/tdnn_smbr/decode_test_epoch2.adj/score_13_1.0/ctm.filt.filt.sys
#%WER 11.5 | 1155 27512 | 90.2 7.0 2.8 1.7 11.5 79.8 | -0.301 | exp/nnet3/tdnn_smbr/decode_test_epoch2.adj_rescore/score_14_1.0/ctm.filt.filt.sys
#%WER 12.7 | 1155 27512 | 89.5 8.1 2.4 2.2 12.7 82.3 | -0.218 | exp/nnet3/tdnn_smbr/decode_test_epoch3.adj/score_14_0.5/ctm.filt.filt.sys
#%WER 11.6 | 1155 27512 | 90.4 7.1 2.5 2.0 11.6 80.4 | -0.345 | exp/nnet3/tdnn_smbr/decode_test_epoch3.adj_rescore/score_14_0.5/ctm.filt.filt.sys
#%WER 12.8 | 1155 27512 | 89.0 8.1 2.8 1.9 12.8 82.0 | -0.252 | exp/nnet3/tdnn_smbr/decode_test_epoch4.adj/score_15_1.0/ctm.filt.filt.sys
#%WER 11.7 | 1155 27512 | 90.1 7.3 2.6 1.8 11.7 79.4 | -0.383 | exp/nnet3/tdnn_smbr/decode_test_epoch4.adj_rescore/score_13_1.0/ctm.filt.filt.sys


set -uo pipefail

stage=1
train_stage=-10 # can be used to start training in the middle.
get_egs_stage=-10
use_gpu=true  # for training
cleanup=false  # run with --cleanup true --stage 6 to clean up (remove large things like denlats,
               # alignments and degs).

. ./cmd.sh
. ./path.sh
. ./utils/parse_options.sh

srcdir=exp/nnet3/tdnn
train_data_dir=data/train_sp_hires
online_ivector_dir=exp/nnet3/ivectors_train_sp
degs_dir=                     # If provided, will skip the degs directory creation
lats_dir=                     # If provided, will skip denlats creation

## Objective options
criterion=smbr
one_silence_class=true

dir=${srcdir}_${criterion}

## Egs options
frames_per_eg=150
frames_overlap_per_eg=30

## Nnet training options
effective_learning_rate=0.0000125
max_param_change=1
num_jobs_nnet=4
num_epochs=4
regularization_opts=          # Applicable for providing --xent-regularize and --l2-regularize options
minibatch_size=64
adjust_priors=true            # May need to be set to false
                              # because it does not help in some setups
modify_learning_rates=true
last_layer_factor=0.1

## Decode options
decode_start_epoch=1 # can be used to avoid decoding all epochs, e.g. if we decided to run more.

if $use_gpu; then
  if ! cuda-compiled; then
    cat <<EOF && exit 1
This script is intended to be used with GPUs but you have not compiled Kaldi with CUDA
If you want to use GPUs (and have them), go to src/, and configure and make on a machine
where "nvcc" is installed.  Otherwise, call this script with --use-gpu false
EOF
  fi
  num_threads=1
else
  # Use 4 nnet jobs just like run_4d_gpu.sh so the results should be
  # almost the same, but this may be a little bit slow.
  num_threads=16
fi

if [ ! -f ${srcdir}/final.mdl ]; then
  echo "$0: expected ${srcdir}/final.mdl to exist; first run run_tdnn.sh or run_lstm.sh"
  exit 1;
fi

if [ $stage -le 1 ]; then
  # hardcode no-GPU for alignment, although you could use GPU [you wouldn't
  # get excellent GPU utilization though.]
  nj=400 # have a high number of jobs because this could take a while, and we might
         # have some stragglers.
  steps/nnet3/align.sh  --cmd "$decode_cmd" --use-gpu false \
    --online-ivector-dir $online_ivector_dir \
     --nj $nj $train_data_dir data/lang $srcdir ${srcdir}_ali ;

fi

if [ -z "$lats_dir" ]; then
  lats_dir=${srcdir}_denlats
  if [ $stage -le 2 ]; then
    nj=50
    # this doesn't really affect anything strongly, except the num-jobs for one of
    # the phases of get_egs_discriminative.sh below.
    num_threads_denlats=6
    subsplit=40 # number of jobs that run per job (but 2 run at a time, so total jobs is 80, giving
    # total slots = 80 * 6 = 480.
    steps/nnet3/make_denlats.sh --cmd "$decode_cmd" --determinize true \
      --online-ivector-dir $online_ivector_dir \
      --nj $nj --sub-split $subsplit --num-threads "$num_threads_denlats" --config conf/decode.config \
      $train_data_dir data/lang $srcdir ${lats_dir} ;
  fi
fi

left_context=`nnet3-am-info $srcdir/final.mdl | grep "left-context:" | awk '{print $2}'`
right_context=`nnet3-am-info $srcdir/final.mdl | grep "right-context:" | awk '{print $2}'`

frame_subsampling_opt=
if [ -f $srcdir/frame_subsampling_factor ]; then
  frame_subsampling_opt="--frame-subsampling-factor $(cat $srcdir/frame_subsampling_factor)"
fi

cmvn_opts=`cat $srcdir/cmvn_opts`

if [ -z "$degs_dir" ]; then
  degs_dir=${srcdir}_degs

  if [ $stage -le 3 ]; then
    if [[ $(hostname -f) == *.clsp.jhu.edu ]] && [ ! -d ${srcdir}_degs/storage ]; then
      utils/create_split_dir.pl \
        /export/b{09,10,11,12}/$USER/kaldi-data/egs/swbd-$(date +'%m_%d_%H_%M')/s5/${srcdir}_degs/storage ${srcdir}_degs/storage
    fi
    # have a higher maximum num-jobs if
    if [ -d ${srcdir}_degs/storage ]; then max_jobs=10; else max_jobs=5; fi

    steps/nnet3/get_egs_discriminative.sh \
      --cmd "$decode_cmd --max-jobs-run $max_jobs --mem 20G" --stage $get_egs_stage --cmvn-opts "$cmvn_opts" \
      --adjust-priors $adjust_priors \
      --online-ivector-dir $online_ivector_dir \
      --left-context $left_context --right-context $right_context \
      $frame_subsampling_opt \
      --frames-per-eg $frames_per_eg --frames-overlap-per-eg $frames_overlap_per_eg \
      $train_data_dir data/lang ${srcdir}_ali $lats_dir $srcdir/final.mdl $degs_dir ;
  fi
fi

if [ $stage -le 4 ]; then
  steps/nnet3/train_discriminative.sh --cmd "$decode_cmd" \
    --stage $train_stage \
    --effective-lrate $effective_learning_rate --max-param-change $max_param_change \
    --criterion $criterion --drop-frames true \
    --num-epochs $num_epochs --one-silence-class $one_silence_class --minibatch-size $minibatch_size \
    --num-jobs-nnet $num_jobs_nnet --num-threads $num_threads \
    --regularization-opts "$regularization_opts" \
    --adjust-priors $adjust_priors \
    --modify-learning-rates $modify_learning_rates --last-layer-factor $last_layer_factor \
    ${degs_dir} $dir
fi

graph_dir=exp/tri3/graph
if [ $stage -le 5 ]; then
  for x in `seq $decode_start_epoch $num_epochs`; do
    for decode_set in dev test; do
      (
      num_jobs=`cat data/${decode_set}_hires/utt2spk|cut -d' ' -f2|sort -u|wc -l`
      iter=epoch$x.adj

      steps/nnet3/decode.sh --nj $num_jobs --cmd "$decode_cmd" --iter $iter \
        --online-ivector-dir exp/nnet3/ivectors_${decode_set} \
        $graph_dir data/${decode_set}_hires $dir/decode_${decode_set}${iter:+_$iter} || exit 1;

      steps/lmrescore_const_arpa.sh --cmd "$decode_cmd" \
        data/lang_test data/lang_rescore data/${decode_set}_hires \
        $dir/decode_${decode_set}${iter:+_$iter} \
        $dir/decode_${decode_set}${iter:+_$iter}_rescore || exit 1;
      ) &
    done
  done
fi
wait;

if [ $stage -le 6 ] && $cleanup; then
  # if you run with "--cleanup true --stage 6" you can clean up.
  rm ${lats_dir}/lat.*.gz || true
  rm ${srcdir}_ali/ali.*.gz || true
  steps/nnet2/remove_egs.sh ${srcdir}_degs || true
fi


exit 0;
