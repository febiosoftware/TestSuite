#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, glob, subprocess, difflib

#===========================  Test Suite =======================================
# Requires Python 2.4 or greater.
# This script runs the FEBio test suite problems in the directory
# Testing/Verify and saves the results in the file results.txt.  It then
# compares the results with the standard results file results_'plat'.txt
# where plat is one of lnx, lnx32, osx, alt or win.  If there are any
# differences, they are printed to stdout using the linux diff format.
# The standard results were produced using the Pardiso solver.  The test
# suite can be run using different solvers by chaning the solver in the file
# FEBio/febio.xml.
#===============================================================================

# Define FEBio directory and executable
os.chdir("..")
febio_dir = os.getcwd()
files = glob.glob("febio.*")
files.sort()
febio = os.path.join(febio_dir, files[0])
plat = files[0][6:]
if plat not in ['lnx', 'lnx32', 'osx', 'alt', 'exe']:
	print "FEBio executable not found"
	print "This script must be run from the FEBio/Testing subdirectory"
	sys.exit()
if plat == 'exe':
        plat = 'win'

# Use one thread
os.environ['OMP_NUM_THREADS'] = '1'

# open the results and output files
os.chdir("Testing")
results = open("results.txt", "w")

# Define the test problems list.
os.chdir("Verify")
test = glob.glob("*.feb")
test.sort()

# keep counters
norms = 0			# nr of normal terminations
nerrs = 0			# nr of error terminations

#run the test problems
for f in test:
	# strip the '.feb' from the input file name
	base = f[:4]
	# define the log and plt files
	logname = base + '.log'
	pltname = base + '.plt'
	# open the dummy output file
	dummy = open("dummy.txt", "w")

	# run the FEBio problem
	# we grab the exit value for termination status
	command = [febio, '-i', f, '-o', logname, '-p', pltname]
	val = subprocess.call(command, stdout=dummy)

	# create a variable that will store the results of the test
	# 0: file
	# 1: Normal/Error termination status
	# 2: Number of time steps
	# 3: Number of iterations
	# 4: Number of RHS evaluations
	# 5: Number of reformations
	# 6: Plot file size
	result = [base, "", 0, 0, 0, 0, 0]
	
	# check the return value
	if val==0:
		result[1] = 'Normal'
		norms = norms + 1
	else:
		result[1] = 'Error'
		nerrs = nerrs + 1
		
	#search the log file for the convergence info
	try:
		flog = open(logname, 'rt')
		
		for line in flog:
			if  line.find("Number of time steps completed"        ) != -1: result[2] = int(line[55:])
			if  line.find("Total number of equilibrium iterations") != -1: result[3] = int(line[55:])
			if  line.find("Total number of right hand evaluations") != -1: result[4] = int(line[55:])
			if  line.find("Total number of stiffness reformations") != -1: result[5] = int(line[55:])
		flog.close()
		result[6] = os.path.getsize(pltname)
	except IOError:
		result[1] = 'Fail'
	except OSError:
		result[1] = 'Fail'
	print result
	results.write(str(result) + '\n')
	dummy.close()

# print a summary to the log file
results.write("\nSummary:\n")
results.write("\tNormal termination : " + str(norms) + "\n")
results.write("\tError termination  : " + str(nerrs) + "\n")
results.close()

# compare results.txt with results_'plat'.txt
os.chdir("..")
results = open("results.txt", "r")
results_std = open("results_" + plat + "_std.txt", "r")
for line in difflib.unified_diff(results.readlines(), results_std.readlines(), n=0):
        sys.stdout.write(line)
results.close()
results_std.close()
