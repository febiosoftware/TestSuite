#!/bin/bash
# Usage: rename log or rename plt

if [ $# == 0 ]; then
	echo "Usage: rename log or rename plt"
	exit
fi

for input in $(ls *.$1); do
    cp -v $input ./${input%.*}_std.$1
done
