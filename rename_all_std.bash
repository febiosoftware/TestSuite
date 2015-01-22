#!/bin/bash
# Usage: rename all log or rename all xplt to std file.

if [ $# == 0 ]; then
	echo "Usage: To rename all log or rename all xplt to standard file."
	echo "rename_all_std.bash log or rename_all_std.bash xplt"
	exit
fi

rm *_std.$1

for input in $(ls *.$1); do
    cp -v $input ./${input%.*}_std.$1
done
