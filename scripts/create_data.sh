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
for f in $(find $3/$4/compressed_img -name '*.jpg' | sort)
do
    echo "${f#$3/} 0" >> $3/$4/$4_img.txt
done

for f in $(find $3/$4/src_img -name '*.bmp' | sort)
do
    echo "${f#$3/} 0" >> $3/$4/$4_label.txt
done
