#!/bin/bash
# $1 - path to source images
# $2 - path to jpg output
# $3 - path to reconstruction output
# $4 - jpg quality
# $5 - metric to use; see eval_reconstruction.py
# $6 - image root
# $7 - caffe model file; can be omitted if default specified below

python $(dirname $0)/make_training_data.py -f $1 -o $2 --jpg $4

cmpath=${7:-$(dirname $0)/../snapshot/place_net_iter_50000.caffemodel} # Replace this with the default you want
cmfile=$(basename $cmpath)
cmdir="${cmpath%$cmfile}"
cmprefix="${cmfile%_iter_*}"
cmiter="${cmfile#*_iter_}"
cmiter="${cmiter%.caffemodel}"

python $(dirname $0)/train_project_net.py --reconstruct $2 --snapshot_dir $cmdir --snapshot_prefix $cmprefix --iters $cmiter
cp $6/output/* $3/

python $(dirname $0)/eval_reconstruction.py $1 $3 $5
