#!/bin/bash
# Usage: rename log or rename plt to std file.

if [ $# == 0 ]; then
	echo "Usage: rename log or rename plt to standard file."
	exit
fi

for input in $(ls *.$1); do
    cp -v $input ./${input%.*}_std.$1
done
