#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os, glob, platform, shutil, sys, subprocess, difflib, datetime
#
# This is the test suite script.
# This script runs a list of FEBio files and checks the results
# The test results are stored in an output file
#===============================================================================

# Determine the operating system and host name
opsys = platform.machine()
platform = sys.platform
print 'opsys = ' + opsys

# Set the default solvers
#solvers = ['pardiso']
solver = 'pardiso'

# Set the platform and specific solvers
if opsys == 'i386':
	plat = 'osx'
elif opsys == 'ia64':
	plat = 'alt'
elif opsys == 'x86_64':
	plat = 'lnx64'
elif platform == 'win32':
	plat = 'exe'
elif opsys == 'i686':
	plat = 'lnx32'

# Use one thread
os.environ['OMP_NUM_THREADS'] = '1'

# open the results file
test_dir = "/home/sci/bhayden/Testing"
os.chdir(test_dir)
res_name = "examples"
std_name = res_name + "_std"
results = open(res_name + ".txt", "w")

# Define FEBio directory, executable, and library
# Assumes that this script is run from FEBio/Testing
# and that the executable is in FEBio/bin
febio_dir = "/home/sci/bhayden/FEBio"
os.chdir(febio_dir)
febio = febio_dir + '/bin/febio.' + plat
febio_lib = febio_dir + '/lib/fecore_' + plat + '.a'

# Define the log and plt output directory
out_dir = '/scratch/bhayden/examples_test/'

# Print the svn revision number in the results file
version = subprocess.Popen(["svnversion"], stdout=subprocess.PIPE).communicate()[0]
results.write("svn version : " + version + "\n")

# Define the test problems list.
os.chdir(test_dir + "/Examples")
test = glob.glob("*.feb")
test.sort()
#test = [ 'Ei-adhesion.feb' ]

# keep counters
norms = 0			# nr of normal terminations
nerrs = 0			# nr of error terminations

# These problems are new, newly modified, or deleted
new      = []
modified = []
deleted  = []
# Open the nightly_std file and a temporary nightly_std file
b_new = 0
b_del = 0
if len(new) + len(modified) != 0: b_new = 1
if len(deleted) != 0: b_del = 1
if b_new or b_del:
	f_std_tmp = test_dir + "/" + plat + "_ex_std_tmp.txt"
	f_std = test_dir + "/" + std_name + ".txt"
	std_tmp = open(f_std_tmp, "w")
	std = open(f_std, "r")
	std_line = std.readline()
	while std_line[0] != "[":
		std_tmp.write(std_line)
		std_line = std.readline()

# These problems use the new plot file format:
xplt = ['bp11', 'bp12', 'bp13', 'bp14', 'bs02', 'bs03', 'twist_cyl']

#run the test problems
for f in test:
	# strip the '.feb' from the input file name
	base = f.split('.')[0]
	if base in xplt: pext = '.xplt'
	else: pext = '.plt'
	# define the log and plt files
	logname = out_dir + base + '.log'
	logstd = out_dir + base + '_std.log'
	pltname = out_dir + base + pext
	diffname = out_dir + base + '_diff.txt'
	# open the dummy file
	dummyname = out_dir + "dummy.txt"
	dummy = open(dummyname, "w")
	# run the FEBio problem
	# we grab the exit value for termination status
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
        # 8: Log diff file size
        # 9: Solve time percent difference (new-old)/old
        #10: Elapsed time percent difference (new-old)/old
	result = [solver, base, "", 0, 0, 0, 0, 0, 0, 0, 0]
	
	# check the return value
	if val==0:
		result[2] = 'Normal'
		norms = norms + 1
	else:
		result[2] = 'Error'
		nerrs = nerrs + 1
		
	# create std log for new and modified problems
	if base in new or base in modified:
		shutil.copy(logname, logstd)
		
	#search the log file for the convergence info
	try:
		flog = open(logname, 'rt')
		fstd = open(logstd, 'r')
		diff = open(diffname, 'w')
		
		for line in flog:
			if  line.find("Number of time steps completed"        ) != -1: result[3] = int(line[55:])
			if  line.find("Total number of equilibrium iterations") != -1: result[4] = int(line[55:])
			if  line.find("Total number of right hand evaluations") != -1: result[5] = int(line[55:])
			if  line.find("Total number of stiffness reformations") != -1: result[6] = int(line[55:])
			if  line.find("Time in solver") != -1:
				slv_hr  = int(line[17:18])
				slv_min = int(line[19:21])
				slv_sec = int(line[22:24])
				new_slv_time = slv_hr*3600 + slv_min*60 + slv_sec
			if  line.find("Elapsed time") != -1:
				el_hr  = int(line[16:17])
				el_min = int(line[18:20])
				el_sec = int(line[21:23])
				new_el_time = el_hr*3600 + el_min*60 + el_sec
		for line in fstd:
			if  line.find("Time in solver") != -1:
				slv_hr  = int(line[17:18])
				slv_min = int(line[19:21])
				slv_sec = int(line[22:24])
				old_slv_time = slv_hr*3600 + slv_min*60 + slv_sec
			if  line.find("Elapsed time") != -1:
				el_hr  = int(line[16:17])
				el_min = int(line[18:20])
				el_sec = int(line[21:23])
				old_el_time = el_hr*3600 + el_min*60 + el_sec
		slv_denom = old_slv_time
		el_denom = old_el_time
		if old_slv_time == 0: slv_denom = 1
		if old_el_time == 0: el_denom = 1
		# calculate percent change (in increments of 10%) in solve and elapse times
		result[9]  = 10*int(10*(new_slv_time-old_slv_time)/float(slv_denom))
		result[10] = 10*int(10*(new_el_time-old_el_time)/float(el_denom))
		# get the size of the plotfile
		result[7] = os.path.getsize(pltname)
		#os.remove(pltname)
		flog.seek(0)
		fstd.seek(0)
		for line in difflib.unified_diff(flog.readlines(), fstd.readlines(), n=0):
			diff.write(line)
		diff.close()
		flog.close()
		fstd.close()
		diffsize = os.path.getsize(diffname)
		result[8] = diffsize/1000
	except IOError:
		result[2] = 'IOError'
	except OSError:
		result[2] = 'OSError'
	print result
	results.write(str(result) + '\n')
	dummy.close()
	os.remove(dummyname)
			
	# Write the temporary nightly_std file
	if b_del:
		for del_base in deleted:
			if del_base in std_line:
				#print "del_base", del_base
				#print "std_line", std_line
				std_line = std.readline()
				break
	if b_new:
		if base in new:
			std_tmp.write(str(result) + '\n')
		else:
			if base in std_line:
				if base in modified:
					std_tmp.write(str(result) + '\n')
				else:
					std_tmp.write(std_line)
				std_line = std.readline()
			else:
				print "base", base
				print "std_line", std_line
				sys.exit("base and std_line do not match")

# Finish the std files
if b_new or b_del:
	std_tmp.write(std_line)
	while True:
		std_line = std.readline()
		if len(std_line) == 0:
			break # EOF
		std_tmp.write(std_line)
	std.close()
	std_tmp.close()
	shutil.copy(f_std_tmp, f_std)
	os.remove(f_std_tmp)

# print a summary to the log file
results.write("\nSummary:\n")
results.write("\tNormal termination : " + str(norms) + "\n")
results.write("\tError termination  : " + str(nerrs) + "\n")
results.close()

# compare results.txt with results_'plat'.txt
os.chdir("..")
results = open("examples.txt", "r")
results_std = open("examples_std.txt", "r")
for line in difflib.unified_diff(results.readlines(), results_std.readlines(), n=0):
        sys.stdout.write(line)
results.close()
results_std.close()

# copy the results file to the Logs directory
res_date = res_name + "_" + str(datetime.date.today()) + ".txt"
shutil.copy(res_name + ".txt", "Logs/" + res_date)
