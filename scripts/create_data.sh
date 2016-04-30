#!/bin/bash
# $1 - path to directory containing images to be compressed
# $2 - JPG quality [0-100]
# $3 - image_root
# $4 - [train, val, test], choose one

mkdir $3/$4
mkdir $3/$4/compressed_img
mkdir $3/$4/src_img

python make_training_data.py -f $1 -o temp --jpg $2

# Create training set and its labels in two directories
for f in temp/*
do
    python patches.py $f $3/$4/compressed_img
done
rm -r temp

for f in $1/*
do
    python patches.py $f $3/$4/src_img 6
done

# Copy all of the image file paths to text files
for f in $(ls $3/$4/compressed_img)
do
    # Get last file in directory for row and col
    last=$(ls $3/$4/compressed_img/$f | tail -1)
    cc="${last#*_}"
    cc=$((${cc%.*}+1))
    rr=$((${last%_*}+1))
    for im in $(ls $3/$4/compressed_img/$f)
    do
        echo "$4/compressed_img/$f/$im $rr $cc" >> $3/$4/$4_img.txt
    done
done

for f in $(ls $3/$4/src_img)
do
    # Get last file in directory for row and col
    last=$(ls $3/$4/src_img/$f | tail -1)
    cc="${last#*_}"
    cc=$((${cc%.*}+1))
    rr=$((${last%_*}+1))
    for im in $(ls $3/$4/src_img/$f)
    do
        echo "$4/src_img/$f/$im $rr $cc" >> $3/$4/$4_label.txt
    done
done
