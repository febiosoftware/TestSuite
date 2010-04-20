#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os, glob, platform, shutil, sys, subprocess, difflib
#
# This is the test suite script for our nightly build and test suite run.
# This script runs a list of FEBio files and checks the results
# The test results are stored in an output file
#===============================================================================

# Determine the operating system and host name
host = platform.node().split('.')[0]
opsys = platform.machine()
platform = sys.platform
print 'host = ' + host
print 'opsys = ' + opsys

# Set the default solvers
#solvers = ['pardiso']
solvers = ['pardiso', 'skyline', 'superlu']

# Set the platform and specific solvers
if opsys == 'i386':
	plat = 'osx'
elif opsys == 'ia64':
	plat = 'alt'
	solvers = ['pardiso', 'superlu', 'psldlt']
elif opsys == 'x86_64':
	plat = 'lnx'
elif platform == 'win32':
	plat = 'exe'
elif opsys == 'i686':
	plat = 'lnx32'

# Use one thread
os.environ['OMP_NUM_THREADS'] = '1'

# open the results file
res_name = "results_" + plat
results = open(res_name + ".txt", "w")

# Define FEBio directory, executable, and library
# Assumes that this script is run from FEBio/Testing
# and that the executable is in FEBio/bin
os.chdir("..")
febio_dir = os.getcwd()
febio = febio_dir + '/bin/febio.' + plat
febio_lib = febio_dir + '/lib/fecore_' + plat + '.a'

# Define the log and plt output directory
out_dir = '/scratch/rawlins/febio_test/'

# Do an svn update on nemo
if host == 'nemo':
	subprocess.call(['svn', 'up'])

# Compile FEBio
shutil.copy(febio, febio.split('.')[0] + '_old.' + plat)
shutil.copy(febio_lib, febio_lib.split('.')[0] + '_old.a')
command =['make', '-f', 'make.mk', 'clean' + plat]
subprocess.call(command)
command =['make', '-f', 'make.mk', plat]
subprocess.call(command)

# Define the test problems list.
os.chdir(febio_dir + "/Testing/Verify")
test = glob.glob("*.feb")
test.sort()
#test = ['ac01.feb', 'co01.feb']

# keep counters
norms = 0			# nr of normal terminations
nerrs = 0			# nr of error terminations

# exempt problems
exempt = ['skylineco32','skylineco34'] # These problems require nonsymmetric matrices

#run the test problems
for solver in solvers:
	for f in test:
		# strip the '.feb' from the input file name
		base = f[:4]
		if solver + base not in exempt:
			# define the log and plt files
			logname = out_dir + solver + '_' + base + '.log'
			pltname = out_dir + solver + '_' + base + '.plt'
			# open the dummy file
			dummy = open(out_dir + "dummy.txt", "w")
			# run the FEBio problem
			# we grab the exit value for termination status
			# TODO: check if the redirection will work on windows
			#command = febio + ' -i ' + f + ' -o ' + logname + ' -p ' + pltname + \
			#	' -cnf ~/FEBio/' + solver + '.xml' + ' >& ../dummy.out'
			command = [febio, '-i', f, '-o', logname, '-p', pltname, \
				'-cnf', febio_dir + '/' + solver + '.xml']
			#print command
			val = subprocess.call(command, stdout=dummy)

			# create a variable that will store the results of the test
			# 0: solver
			# 1: file
			# 2: Normal/Error termination status
			# 3: Number of time steps
			# 4: Number of iterations
			# 5: Number of RHS evaluations
			# 6: Number of reformations
			# 7: Plot file size
			result = [solver, base, "", 0, 0, 0, 0, 0]
			
			# check the return value
			if val==0:
				result[2] = 'Normal'
				norms = norms + 1
			else:
				result[2] = 'Error'
				nerrs = nerrs + 1
				
			#search the log file for the convergence info
			try:
				flog = open(logname, 'rt')
				
				for line in flog:
					if  line.find("Number of time steps completed"        ) != -1: result[3] = int(line[55:])
					if  line.find("Total number of equilibrium iterations") != -1: result[4] = int(line[55:])
					if  line.find("Total number of right hand evaluations") != -1: result[5] = int(line[55:])
					if  line.find("Total number of stiffness reformations") != -1: result[6] = int(line[55:])
				flog.close()
				result[7] = os.path.getsize(pltname)
			except IOError:
				result[2] = 'Fail'
			except OSError:
				result[2] = 'Fail'
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
results = open(res_name + ".txt", "r")
std_name = res_name + "_std"
std = open(std_name + ".txt", "r")
for line in difflib.unified_diff(results.readlines(), std.readlines(), n=0):
        sys.stdout.write(line)
results.close()
std.close()