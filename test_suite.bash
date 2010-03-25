#!/bin/bash

# Bash script to run the FEBio test suite on the Altix.  Produces a file called results.txt.

plat=alt
febio=../../febio.$plat
output=results.txt
export OMP_NUM_THREADS=1

echo 'File,Equations,Specified Time Steps,Steps Completed,Equil Iter,RH Eval,Stiff Reform,Plt Size,Termination' > $output

cd Verify
for input in $(ls *.feb); do
	$febio -i $input > /dev/null
	log=${input%%.*}.log
	plt=${input%%.*}.plt
	eqns=$(awk '/Nr of equations/ {print $6; exit}' $log)
	tmsteps=$(awk '/Number of timesteps/ {print $6}' $log)
	solve_tm=$(awk '/Time in solver/ {print $4}' $log)
	elapse_tm=$(awk '/Elapsed time/ {print $4}' $log)
	steps=$(awk '/steps completed/ {print $8}' $log)
	eq_it=$(awk '/Total number of equilibrium/ {print $8}' $log)
	rh_eval=$(awk '/Total number of right hand/ {print $9}' $log)
	st_re=$(awk '/Total number of stiffness/ {print $8}' $log)
	plt_size=$(ls -l $plt | cut -f6 -d' ')
	if [ -n "$(grep 'E R R O R' $log)" ]; then
		term=Error
	elif [ -n "$(grep 'N O R M A L' $log)" ]; then
		term=Normal
	else
		term='Fail'
	fi
	echo ${input%%.*}, $term
	echo $input,$eqns,$tmsteps,$steps,$eq_it,$rh_eval,$st_re,$plt_size,$term >> ../$output
done

# Compare with standard results
cd ..
diff $output results_$plat.txt