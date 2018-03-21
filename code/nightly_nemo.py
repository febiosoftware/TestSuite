#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, glob, platform, shutil, sys, subprocess, difflib, datetime, time, csv
from collections import deque
from compile_plugins import CompilePlugins
from logdata import dfield
from update import new, modified, deleted

# This is the test suite script for our nightly build and test suite run.
# It has been modified to run on nemo.sci.utah.edu (a Linux machine)
# This script does the following things:
# 1. Does an svn update 
# 2. compiles FEBio
# 3. Runs the test suite
# This script runs a list of FEBio files and checks the results
# The test results are stored in an output file
#===============================================================================

# Determine the operating system and host name
host = platform.node().split('.')[0]
opsys = platform.machine()
sysplat = sys.platform
bits = platform.architecture()[0]
print("host = " + host)
print("opsys = " + opsys)
print("sysplat = " + sysplat)

# Read the commandline arguments
# Arguments are any of:
# c: do not compile
# p: use only Pardiso
# t: test on a few problems
# 4: run with 4 threads
# r: use the Release version of FEBio2

if len(sys.argv) == 1: sys.exit("error: The name of the FEBio directory must be entered as an argument")
febio_name = sys.argv[1]
febio_lc_name = febio_name.lower()
if len(sys.argv) > 2: args = sys.argv[2]
else: args = ''
print(febio_name)

# Set the default solvers
# ** Noted removed skyline & superlu solvers. ** 
if args.find('p') != -1: solvers = ['pardiso']
else: solvers = ['pardiso'] #, 'skyline', 'superlu']

# Set the platform
plat = 'lnx64'

# Specify number of threads
dir_ext = ""
if args.find('4') != -1:
	os.environ['OMP_NUM_THREADS'] = '4'
	dir_ext = "4"
else: os.environ['OMP_NUM_THREADS'] = '1'

# Define several directories
code_dir = os.getcwd() + '/'
os.chdir("..")
test_dir = os.getcwd()
os.chdir("..")
root_dir = os.getcwd() + '/'
os.chdir(test_dir)

# Open the results file
if febio_name == 'FEBio':
	verify = "/Verify"
	if dir_ext == "4": res_name = "nightly4_" + plat
	else: res_name = "nightly_" + plat
else:
	verify = "/Verify2"
	if dir_ext == "4": res_name = "nightly24_" + plat
	else: res_name = "nightly2_" + plat
std_name = res_name + "_std"
results = open('Logs/' + res_name + ".txt", "w")

#Update the test suite
if args.find('c') == -1 and plat != 'osx': subprocess.call(['svn', 'up'])

# Define the test problems list.
if args.find('t') != -1: test = ['op01.feb']
else:
	os.chdir(test_dir + verify)
	test = glob.glob("*.feb")
	test.sort()
	os.chdir(test_dir)

# If verifymod.txt has changed, the test suite has changes that need to be run.
# Run 'date +%D > verifymod.txt' on the commanline if there are changes.
# 86400 is the number of seconds in a day.
test_update = 0
if time.time() - os.path.getmtime('code/verifymod.txt') < 86400: test_update = 1

# Test whether any .feb files have been updated
if not test_update:
	for f in test:
		if time.time() - os.path.getmtime(test_dir + verify + "/" + f) < 86400:
			test_update = 1
			break

#Added to incorporate the testing parser
parsing_dir = test_dir + '/Nightly_Parsing/'

# These are problems that report extra data fields
dfield0 = [col[0] for col in dfield]

# Define FEBio directory, executable, and library
# Assumes that this script is run from Testing and the FEBio directory is on the same level
# and that the executable is in FEBio/bin
if args.find('r') != -1:
	os.chdir(root_dir + "Release/" + febio_name)
	febio_dir = os.getcwd()
	febio = febio_dir + '/build/bin/' + febio_lc_name + '.' + plat
else:
	febio_dir = root_dir + febio_name
	febio = febio_dir + '/build/bin/' + febio_lc_name + '.' + plat
	os.chdir(febio_dir)

# Define the log and plt output directory
# user variable assumes the directory is e.g. /home/sci/rawlins/Testing
user = test_dir.split('/')[3]
out_dir = '/scratch/' + user + '/' + febio_lc_name + dir_ext + '_test/'
logs_dir = 'Logs/' + febio_name + dir_ext + '_Logs/'

if args.find('c') == -1: # if we don't explicitly say not to compile

	# Do an svn update on lnx64 and write to svn_version.py
	if plat != 'osx': subprocess.call(['svn', 'up'])
	version_str = subprocess.Popen(['svnversion'], stdout=subprocess.PIPE).communicate()[0]
	version = version_str.split("\n")[0]

	# Compile FEBio
	os.chdir("build")
	command =['make', plat]
	output = subprocess.call(command)
	
	if output == 0:
		# Test whether febio compiled in the last 20 hours
		if time.time() - os.path.getctime(febio) > 72000 and not test_update and args.find('c') == -1:
			results.write("Nothing to do\n")
			sys.exit("Nothing to do\n")

		# If febio did compile, update svnrev.h, recompile and create a copy of the executable
		if plat != 'osx':
			execfile("svnrev.py")
			command =['make', plat]
			output = subprocess.call(command)
			if output != 0: sys.exit("FEBio debug did not compile after updating svnrev.h")
		command =['make', plat]
		output = subprocess.call(command)
		if output != 0: print("FEBio (no debug) did not compile after updating svnrev.h")
		command =['make', plats]
		output = subprocess.call(command)
		if output != 0: print("FEBio (sequential) did not compile after updating svnrev.h")
		shutil.copy(febio, febio.split('.')[0] + '_' + str(version) + '.' + plat)

		# Compile the plugins
		pic = CompilePlugins(plats, root_dir)
		pic.launch()

	else: sys.exit("FEBio did not compile")

# keep counters
norms = 0                       # nr of normal terminations
nerrs = 0                       # nr of error terminations

# Exempt problems: 
	# These files are the input files for parameter optimization
	# and the rve files for multiscale problems:
exempt = ['oi01', 'oi02', 'hi01']
	
# These problems give inconsistent convergence statistics results
# when run with multiple threads:
inconsistent = []

# These problems will not run in FEBio1
exempt1 = ['bp23', 'ma17', 'mg01', 'mg02']

# These problems will not run in FEBio2
exempt2 = ['sh15']

# These are parameter optimization problems
paramopt = [['op01', 'oi01'],
	    ['op02', 'oi02'],
	    ['op03', 'oi01'],
	    ['op04', 'oi02']]
paramopt0 = [col[0] for col in paramopt]

# Read the commanline arguments
if dir_ext == "4": exempt += inconsistent
if febio_name == 'FEBio': exempt += exempt1
if febio_name == 'FEBio2': exempt += exempt2

# Open the nightly_std file and a temporary nightly_std file
b_new = 0
b_del = 0
if len(new) + len(modified) != 0: b_new = 1
if len(deleted) != 0: b_del = 1
if b_new or b_del:
	f_std = test_dir + "/Logs/" + std_name + ".txt"
	f_std_tmp = test_dir + "/Logs/" + std_name + "_tmp.txt"
	std_tmp = open(f_std_tmp, "w")
	std = open(f_std, "r")
	std_line = std.readline()
	while std_line[0] != "[":
		std_tmp.write(std_line)
		std_line = std.readline()

#run the test problems
os.chdir(test_dir + verify)
for solver in solvers:
	config_file = code_dir + solver + '.xml'
	for f in test:
		# strip the '.feb' from the input file name
		base = f[:4]
		if base not in exempt:
			
			# Test for extra data field problems
			if base in dfield0:
				df_time = dfield[dfield0.index(base)][1]
				df_tline = "Time = " + df_time + "\n"
				df_flg = 1
				found = 0
				data1 = 0
				line_num = 0
			else: df_flg = 0
			
			# define the log and plt files
			logname = out_dir + solver + '_' + base + '.log'
			logstd = out_dir + solver + '_' + base + '_std.log'
			pltname = out_dir + solver + '_' + base + '.xplt'
			diffname = out_dir + solver + '_' + base + '_diff.txt'
			# open the dummy file
			dummyname = out_dir + "dummy.txt"
			dummy = open(dummyname, "w")
			
			# Test for parameter optimization problems
			opt = 0
			if base in paramopt0:
				opt = 1
				if febio_name == 'FEBio2':
					fi = paramopt[paramopt0.index(base)][1]
					command = [febio, '-i', fi + '.feb', '-s', f, '-o', logname, '-p', pltname, \
						'-cnf', config_file]
					#print(command)
				else:
					command = [febio, '-s', f, '-o', logname, '-p', pltname, \
						'-cnf', config_file]
			# Test for plugin problems
			elif 'pi' in base:
				if base == 'pi08' or base == 'pi09':
					command = [febio, '-i', f, '-o', logname, '-p', pltname, \
						'-cnf', 'plugins/' + base + '_' + plat + '.xml', \
						'-task=angio', 'plugins/angiofe.txt']
				else:
					command = [febio, '-i', f, '-o', logname, '-p', pltname, \
						'-cnf', 'plugins/' + base + '_' + plat + '.xml']
			else:
				command = [febio, '-i', f, '-o', logname, '-p', pltname, \
					'-cnf', config_file]
			
			# run the FEBio problem
			val = subprocess.call(command, stdout=dummy)
			#print "Subprocess result: ", val

			# Create a variable that will store the results of the test
			
			#Optimization input file
			# Normal input file
			# 0: solver
			# 1: file
			# 2: Normal/Error termination status
			# 3: Final objective value
			# 4: Total iterations
			# 5: Plot file size
			# 6: Log diff file size
			if opt: result = [solver, base, "", 0.0, 0, 0, 0]

			# Normal input file
			# 0: solver
			# 1: file
			# 2: Normal/Error termination status
			# 3: Number of time steps
			# 4: Number of iterations
			# 5: Number of RHS evaluations
			# 6: Number of reformations
			# 7: Plot file size
			# 8: Log diff file size
			# 9: Solve time ratio new/old
			#10: Elapsed time ratio new/old
			#11: Data field value
			else: result = [solver, base, "", 0, 0, 0, 0, 0, 0, 0, 0, ""]
			
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
				
			# search the log file for the convergence info
			try:
				flog = open(logname, 'r')
				fstd = open(logstd, 'r')
				diff = open(diffname, "w")
				if opt:
					for line in flog:
						if line.find("Final objective value") !=-1: result[3] = line.split()[5]
						if line.find("Total iterations"     ) !=-1: result[4] = int(line[43:])
				else:
					for line in flog:
						if  line.find("Number of time steps completed"        ) != -1: result[3] = int(line[55:])
						if  line.find("Total number of equilibrium iterations") != -1: result[4] = int(line[55:])
						if  line.find("Total number of right hand evaluations") != -1: result[5] = int(line[55:])
						if  line.find("Total number of stiffness reformations") != -1: result[6] = int(line[55:])
						if  line.find("Time in linear solver") != -1:
							slv_hr  = int(line[24:25])
							slv_min = int(line[26:28])
							slv_sec = int(line[29:31])
							new_slv_time = slv_hr*3600 + slv_min*60 + slv_sec
							#print "New solve time", new_slv_time
						if  line.find("elapsed time") != -1:
							el_hr  = int(line[37:38])
							el_min = int(line[39:41])
							el_sec = int(line[42:44])
							new_el_time = el_hr*3600 + el_min*60 + el_sec
						if df_flg:
							if line.find("Data Record #1") !=-1: data1 = 1
							if data1: line_num += 1
							if line.find(df_tline) !=-1 and data1: found = 1
							if line_num == 6:
								if found: result[11] = line.rstrip("\n").split(" ")[1]
								found = 0
								line_num = 0
								data1 = 0

				# get the size of the plotfile and delete it
				result[7-2*opt] = int(os.path.getsize(pltname))
				#os.remove(pltname)
				# do a diff on the log file
				flog.seek(0)
				fstd.seek(0)
				for line in difflib.unified_diff(flog.readlines(), fstd.readlines(), n=0):
					diff.write(line)
				diff.close()
				flog.close()
				fstd.close()
				diffsize = os.path.getsize(diffname)
				diffsize = 5*(diffsize/5000)
				#result[8-2*opt] = int(diffsize)
				# If all other statistics are the same, there are only differences in the
				# residuals.  I decided to ignore this statistic.
			except IOError:
				result[2] = 'IOError'
			except OSError:
				result[2] = 'OSError'
			
			# Get the total vessel length from the AngioFE2 out_log.csv file
			if base == 'pi08' or base == 'pi09':
				with open('out_log.csv', 'rb') as csvfile:
					result[11] = deque(csv.reader(csvfile), 1)[0][3]
			
			print(result)
			results.write(str(result) + '\n')
			
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
						print("base", base)
						print("std_line", std_line)
						sys.exit("base and std_line do not match")
			dummy.close()
			os.remove(dummyname)
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

# compare results.txt with nightly_'plat'_std.txt
#parsingFile = open(parsing_dir + "Nightly_Runs/" + host + ".txt", "w")
os.chdir(test_dir)
results = open('Logs/' + res_name + ".txt", "r")
std = open('Logs/' + std_name + ".txt", "r")
for line in difflib.unified_diff(results.readlines(), std.readlines(), n=0):
	sys.stdout.write(line)
#	parsingFile.write(line)
results.close()
std.close()

# copy the results file to the Logs directory
res_date = res_name + "_" + str(datetime.date.today()) + ".txt"
shutil.copy('Logs/' + res_name + ".txt", logs_dir + res_date)

#SVN Commit the parsing file
#subprocess.call(['svn', 'ci', '-m', '"Commiting nightly files for Parsing"', #'Nightly_Parsing/Nightly_Runs/*.txt'])
