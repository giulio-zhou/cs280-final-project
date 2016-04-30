#!/bin/bash
# Execute this script to start training (useful for remembering/organizing params)
bash setup_ext_mnt.sh
# bash create_data.sh ../data/srcnn_data/ 30 ../data/ train
# bash create_data.sh ../data/Set14/ 30 ../data/ val
python -u train_project_net.py --gpu 0 --cudnn --image_root ../data/ --lr 0.0000001 --decay 0 \
                               --iters 30000 --snapshot_dir /mnt/snapshot > log/training_log.txt 2>&1 &
