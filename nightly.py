#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os, glob, platform, shutil, sys, subprocess, difflib, datetime, time
#
# This is the test suite script for our nightly build and test suite run.
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

# Read the commanline arguments
# Arguments are any of:
# c: do not compile
# p: use only Pardiso
# f: do fast test (no long or inconsistent problems)
# t: test on a few problems
# 4: run with 4 threads

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
if opsys == 'x86_64':
	if host == 'katan':
		plat = 'osx'	
	else:
		plat = 'lnx64'
elif sysplat == 'win32':
	plat = 'win'
elif opsys == 'i686':
	plat = 'lnx32'

# Specify number of threads
if (args.find('f') != -1) or (args.find('4') != -1): os.environ['OMP_NUM_THREADS'] = '4'
else: os.environ['OMP_NUM_THREADS'] = '1'
#os.environ['OMP_NUM_THREADS'] = '4'

# open the results file
test_dir = os.getcwd()
if febio_name == 'FEBio': res_name = "nightly_" + plat
else: res_name = "nightly2_" + plat
std_name = res_name + "_std"
results = open(res_name + ".txt", "w")

#Added to incorporate the testing parser
parsing_dir = test_dir + '/Nightly_Parsing/'

if plat == 'win':
	febio_dir = 'C:/' + febio_name
	if host == 'cibc-rd7':
		exe_dir = febio_dir + '/x64/Release'
	elif febio_name == 'FEBio2':
		exe_dir = febio_dir + '/VS2008/Release'
	else:
		exe_dir = febio_dir + '/Release'
	febio = exe_dir + '/' + febio_name + '.exe'

	out_dir = 'C:/Testing/' + febio_name + '_Logs/'
	logs_dir = out_dir

	# Print the FEBio svn revision number in the results file
	os.chdir(febio_dir)
	version_str = subprocess.Popen(["subwcrev", "."], stdout=subprocess.PIPE).communicate()[0]
	version_str = version_str.decode("utf8")
	results.write("svn version : " + version_str + "\n")
	version_lines = version_str.split("\n")
	version_lines = [line.strip() for line in version_lines]
	for line in version_lines:
		if line.find("Updated") !=-1:
			version = line.split(" ")[3]
	
	# Print message if executable did not compile (exe is older than 1 hour)
	# or save a copy of the executable if it did.
	if time.time() - os.path.getctime(febio) > 3600:
		results.write("FEBio did not compile\n")
		print("FEBio did not compile\n")
	else:
		try:
			shutil.copy(febio, febio.split('.')[0] + '_' + version + '.exe')
		except IOError:
			print("Error copying files")
		
else:
	#Update the test suite
	if plat == 'lnx64' and febio_name == 'FEBio':
		subprocess.call(['svn', 'up'])

	# Define FEBio directory, executable, and library
	# Assumes that this script is run from Testing and the FEBio directory is on the same level
	# and that the executable is in FEBio/bin
	os.chdir("../" + febio_name)
	febio_dir = os.getcwd()
	febio = febio_dir + '/bin/' + febio_lc_name + '.' + plat

	# Define the log and plt output directory
	# user variable assumes the directory is e.g. /home/sci/rawlins/Testing
	user = test_dir.split('/')[3]
	out_dir = '/scratch/' + user + '/' + febio_lc_name + '_test/'
	logs_dir = febio_name + '_Logs/'

	if args.find('c') == -1:

		# Do an svn update on lnx64 and write to svn_version.py
		if plat == 'lnx64':
			version = "0"
			version_str = subprocess.Popen(['svn', 'up'], stdout=subprocess.PIPE).communicate()[0]
			version_str = version_str.decode("utf8")
			output_lines = version_str.split("\n")
			for line in output_lines:
				if line.find("Updated") !=-1:
					version = line.split(" ")[3].strip(".")
			svn_version = open("svn_version.py", "w")
			svn_version.write("version = " + version)
			svn_version.close()


		# Compile FEBio if it has been updated
		sys.path.append(os.getcwd())
		from svn_version import version
		if version > 0:
			command =['make', '-f', 'febio.mk', plat + 'clean' ]
			subprocess.call(command)
			command =['make', '-f', 'febio.mk', plat]
			output = subprocess.call(command)
			if output == 0:
				try:
					shutil.copy(febio, febio.split('.')[0] + '_' + str(version) + '.' + plat)
				except IOError:
					print("Error copying files")
			else: sys.exit("FEBio did not compile")	

	# Print the svn revision number in the results file
	version = subprocess.Popen(["svnversion"], stdout=subprocess.PIPE).communicate()[0]
	results.write("svn version : " + str(version) + "\n")

# Define the test problems list.
os.chdir(test_dir + "/Verify")
if args.find('t') != -1: test = ['co01.feb', 'co02.feb']
else:
	test = glob.glob("*.feb")
	test.sort()


# keep counters
norms = 0                       # nr of normal terminations
nerrs = 0                       # nr of error terminations

# Exempt problems: 
exempt = [
	# These files are the input files for a parameter optimization problem:
	  'oi01',
	  'oi02']
	
# These problems will be ignored for a fast run of the test suite:
slow = ['co33',
	'mi28',
	'ri02']

# These problems give inconsistent convergence statistics results
# when run with multiple threads:
inconsistent = []

# These problems will not run in FEBio2
exempt2 = ['mp01',
	   'mp02',
	   'mp03',
	   'mp06',
	   'mp07',
	   'mp08',
	   'tr01',
	   'tr02',
	   'tr03',
	   'tr04',
           'op01',
           'op02']

# These are parameter optimization problems
paramopt = ['op01',
	    'op02']


# These are problems that report extra data fields
from logdata import dfield
dfield0 = [col[0] for col in dfield]

# Read the commanline arguments
if args.find('f') != -1: exempt += slow + inconsistent
if args.find('4') != -1: exempt += inconsistent
if febio_name == 'FEBio2': exempt += exempt2

# These problems are new, newly modified, or deleted
from update import new, modified, deleted

# Open the nightly_std file and a temporary nightly_std file
b_new = 0
b_del = 0
if len(new) + len(modified) != 0: b_new = 1
if len(deleted) != 0: b_del = 1
if b_new or b_del:
	f_std_tmp = test_dir + "/" + plat + "_std_tmp.txt"
	f_std = test_dir + "/" + std_name + ".txt"
	std_tmp = open(f_std_tmp, "w")
	std = open(f_std, "r")
	std_line = std.readline()
	while std_line[0] != "[":
		std_tmp.write(std_line)
		std_line = std.readline()

#run the test problems
for solver in solvers:
	for f in test:
		# strip the '.feb' from the input file name
		base = f[:4]
		if base not in exempt:
			
			# Test for parameter optimization problems
			if base in paramopt:
				opt = 1
				runflag = '-s'
			else:
				opt = 0
				runflag = '-i'
			
			# Test for extra data field problems
			if base in dfield0:
				df_time = dfield[dfield0.index(base)][1]
				df_tline = "Time = " + df_time + "\n"
				df_flg = 1
				found = 0
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
			
			# run the FEBio problem
			# we grab the exit value for termination status
			# TODO: check if the redirection will work on windows
			#command = febio + ' -i ' + f + ' -o ' + logname + ' -p ' + pltname + \
			#       ' -cnf ~/FEBio/' + solver + '.xml' + ' >& ../dummy.out'
			command = [febio, runflag, f, '-o', logname, '-p', pltname, \
				'-cnf', febio_dir + '/' + solver + '.xml']
			#print command
			val = subprocess.call(command, stdout=dummy)
			#print "Subprocess result: ", val

			# Create a variable that will store the results of the test
			
			#Optimization input file
			# Normal input file
			# 0: solver
			# 1: file
			# 2: Normal/Error termination status
			# 3: Major iterations
			# 4: Minor iterations
			# 5: Final objective value
			# 6: Plot file size
			# 7: Log diff file size
			if opt: result = [solver, base, "", 0, 0, 0.0, 0, 0]

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
			else: result = [solver, base, "", 0, 0, 0, 0, 0, 0, 0, 0]
			
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
						if line.find("Major iterations"     ) !=-1: result[3] = int(line[43:])
						if line.find("Minor iterations"     ) !=-1: result[4] = int(line[43:])
						if line.find("Final objective value") !=-1: result[5] = line.split()[3]
				else:
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
							#print "New solve time", new_slv_time
						if  line.find("Elapsed time") != -1:
							el_hr  = int(line[16:17])
							el_min = int(line[18:20])
							el_sec = int(line[21:23])
							new_el_time = el_hr*3600 + el_min*60 + el_sec
						if df_flg:
							if line.find(df_tline) !=-1: found = 1
							if found: line_num += 1
							if line_num == 3:
								result.append(line.rstrip("\n").split(" ")[1])
								found = 0
								line_num = 0
					for line in fstd:
						if  line.find("Time in solver") != -1:
							slv_hr  = int(line[17:18])
							slv_min = int(line[19:21])
							slv_sec = int(line[22:24])
							old_slv_time = slv_hr*3600 + slv_min*60 + slv_sec
							#print "Old solve time", old_slv_time
						if  line.find("Elapsed time") != -1:
							el_hr  = int(line[16:17])
							el_min = int(line[18:20])
							el_sec = int(line[21:23])
							old_el_time = el_hr*3600 + el_min*60 + el_sec
					# calculate percent difference (in incr% increments) in solve and elapse times
					slv_denom = (new_slv_time + old_slv_time)/2
					el_denom = (new_el_time + old_el_time)/2
					if slv_denom == 0: slv_denom = 1
					if el_denom == 0: el_denom = 1
					slv_diff = new_slv_time - old_slv_time
					el_diff = new_el_time - old_el_time
					if abs(slv_diff) <= 3: slv_diff = 0
					if abs(el_diff) <= 3: el_diff = 0
					if slv_denom < 5: incr = 200
					elif slv_denom < 20: incr = 100
					elif slv_denom < 60: incr = 50
					else: incr = 20
					result[9]  = incr*int((100/incr)*slv_diff/float(slv_denom))
					if el_denom < 5: incr = 200
					elif el_denom < 20: incr = 100
					elif el_denom < 60: incr = 50
					else: incr = 20
					result[10] = incr*int((100/incr)*el_diff/float(el_denom))

				# get the size of the plotfile and delete it
				result[7-opt] = int(os.path.getsize(pltname))
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
				result[8-opt] = int(diffsize)
			except IOError:
				result[2] = 'IOError'
			except OSError:
				result[2] = 'OSError'
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
parsingFile = open(parsing_dir + "Nightly_Runs/" + host + ".txt", "w")
os.chdir("..")
results = open(res_name + ".txt", "r")
std = open(std_name + ".txt", "r")
for line in difflib.unified_diff(results.readlines(), std.readlines(), n=0):
	sys.stdout.write(line)
	parsingFile.write(line)
results.close()
std.close()

# copy the results file to the Logs directory
res_date = res_name + "_" + str(datetime.date.today()) + ".txt"
shutil.copy(res_name + ".txt", logs_dir + res_date)
