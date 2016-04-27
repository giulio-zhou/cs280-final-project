#!/bin/bash

mkdir $3/$4
mkdir $3/$4/compressed_img
mkdir $3/$4/src_img
touch $3/$4/train_img.txt
touch $3/$4/train_label.txt

python make_training_data.py -f $1 -o temp --jpg $2

# Create training set and its labels in two directories
for f in temp/*
do
    python patches.py $f $3/$4/compressed_img
done
rm -r temp

for f in $1/*
do
    python patches.py $f $3/$4/src_img
done

# Copy all of the image file paths to text files
for f in $(ls $3/$4/compressed_img)
do
    echo "$4/compressed_img/$f 0" >> $3/$4/train_label.txt
done

for f in $(ls $3/$4/src_img)
do
    echo "$4/src_img/$f 0" >> $3/$4/train_img.txt
done
