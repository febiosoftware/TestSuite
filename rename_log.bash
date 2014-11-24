#!/bin/bash
# Copies the log file to the standard log file

if [ $# == 0 ]; then
	echo "Usage: enter the root name of the problem, e.g., co04"
	exit
fi

cp -v pardiso_$1.log pardiso_$1_std.log