#!/bin/bash

# Bash script to run the FEBio test suite.  Produces a file called 'host'_results.csv, where 'host' is the
# name of the host machine or win if running Cygwin on Windows.  All tests should give a normal termiation.
# The script assumes that the febio executable is in the FEBio/bin directory.

# Cygwin notes:
#	This script assumes that the test suite directory exists on a mapped linux (samba) network drive
#	called 's' under Windows.  It also assumes that the test suite files (.feb files) have a unix line
#	termination and creates a temporary dos line terminated file.  If this is not the case in your
#	implementation, edit this script accordingly.

host=${HOSTNAME%%.*}
root=~
if [ $HOSTTYPE == "i386" ]; then
	plat=osx
elif [ $HOSTTYPE == "ia64" ]; then
	plat=alt
elif [ $HOSTTYPE == "i686" ]; then
	root=/cygdrive/s
	host=win
	plat=exe
elif [ $HOSTTYPE == "x86_64" ]; then
	plat=lnx
fi
febio=${root}/mrl/FEBio/bin/febio.$plat

echo 'File,Equations,Specified Time Steps,Solve Time,Elapsed Time,Steps Completed,Termination' > ${host}'_results.csv'

if [ ! -d platform/$host ]; then
	mkdir platform/$host
fi

for dir in $(ls -1p Input/ | grep /); do
	echo 'dir = ' $dir
	cd Input/$dir
	for infile in $(ls *.feb); do
		if [ $host == 'win' ]; then
			awk 'sub("$", "\r")' $infile > ${infile%%.*}_win.feb
			input=${infile%%.*}_win.feb
		else
			input=$infile
		fi
		echo $input
		$febio -i $input > /dev/null
		log=${input%%.*}.log
		plt=${input%%.*}.plt
		eqns=$(awk '/Nr of equations/ {print $6; exit}' $log)
		tmsteps=$(awk '/Number of timesteps/ {print $6}' $log)
		solve_tm=$(awk '/Time in solver/ {print $4}' $log)
		elapse_tm=$(awk '/Elapsed time/ {print $4}' $log)
		steps=$(awk '/steps completed/ {print $8}' $log)
		if [ -n "$(grep 'E R R O R' $log)" ]; then
			term=Error
		elif [ -n "$(grep 'N O R M A L' $log)" ]; then
			term=Normal
		else
			term=''
		fi
		echo $input,$eqns,$tmsteps,$solve_tm,$elapse_tm,$steps,$term >> ../../${host}'_results.csv'
		mv $log ../../platform/$host
		rm $plt
		if [ $host == 'win' ]; then
			rm $input
		fi
	done
	cd ../..
done
