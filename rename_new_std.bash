#!/bin/bash
# Usage: rename log or rename plt

if [ $# == 0 ]; then
	echo "Usage: rename_new_std.bash new"
	echo "Where 'new' is the name of the new model"
	echo "E.g. rename_new_std.bash co01"
	exit
fi

for input in $(ls *$1.log); do
	cp -v $input ./${input%.*}_std.log
done
