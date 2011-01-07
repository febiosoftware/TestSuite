#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os, glob, platform, shutil, sys, subprocess, difflib, datetime
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
        plat = 'lnx64'
elif sysplat == 'win32':
        plat = 'win'
elif opsys == 'i686':
        plat = 'lnx32'

# Use one thread
os.environ['OMP_NUM_THREADS'] = '1'

# open the results file
test_dir = os.getcwd()
res_name = "nightly_" + plat
results = open(os.path.join(test_dir, res_name + ".txt"), "w")

if plat == 'win':
        febio_dir = 'C:/FEBio'
        if bits == '64bit':
                exe_dir = febio_dir + '/x64/Release-x64'
        else:
                exe_dir = febio_dir + '/Release'
        febio = exe_dir + '/FEBio.exe'

        out_dir = ''
else:
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
        if host == 'swell':
                subprocess.call(['svn', 'up'])

        # Compile FEBio
        try:
                shutil.copy(febio, febio.split('.')[0] + '_old.' + plat)
                shutil.copy(febio_lib, febio_lib.split('.')[0] + '_old.a')
        except IOError:
                print "Error copying files"
        command =['make', '-f', 'febio.mk', plat + 'clean' ]
        subprocess.call(command)
        command =['make', '-f', 'febio.mk', plat]
        subprocess.call(command)

        # Print the svn revision number in the results file
        version = subprocess.Popen(["svnversion"], stdout=subprocess.PIPE).communicate()[0]
        results.write("svn version : " + version + "\n")

# Define the test problems list.
os.chdir(febio_dir + "/Testing/Verify")
test = glob.glob("*.feb")
test.sort()
#test = ['co01.feb', 'co02.feb']

# keep counters
norms = 0                       # nr of normal terminations
nerrs = 0                       # nr of error terminations

# exempt problems: These problems require nonsymmetric matrices
exempt = ['skylineco32','skylineco34','skylinema07','skylinema08','skylinema09']

#run the test problems
for solver in solvers:
        for f in test:
                # strip the '.feb' from the input file name
                base = f[:4]
                if solver + base not in exempt:
                        # define the log and plt files
                        logname = out_dir + solver + '_' + base + '.log'
                        logstd = out_dir + solver + '_' + base + '_std.log'
                        pltname = out_dir + solver + '_' + base + '.plt'
                        diffname = out_dir + solver + '_' + base + '_diff.txt'
                        # open the dummy file
                        dummy = open(out_dir + "dummy.txt", "w")
                        # run the FEBio problem
                        # we grab the exit value for termination status
                        # TODO: check if the redirection will work on windows
                        #command = febio + ' -i ' + f + ' -o ' + logname + ' -p ' + pltname + \
                        #       ' -cnf ~/FEBio/' + solver + '.xml' + ' >& ../dummy.out'
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
                        # 9: Solve time ratio new/old
                        #10: Elapsed time ratio new/old
                        result = [solver, base, "", 0, 0, 0, 0, 0, 0, 0, 0]
                        
                        # check the return value
                        if val==0:
                                result[2] = 'Normal'
                                norms = norms + 1
                        else:
                                result[2] = 'Error'
                                nerrs = nerrs + 1
                                
                        # search the log file for the convergence info
                        try:
                                flog = open(logname, 'r')
                                fstd = open(logstd, 'r')
                                diff = open(diffname, "w")
                                
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
                                slv_denom = old_slv_time
                                el_denom = old_el_time
                                slv_diff = new_slv_time - old_slv_time
                                el_diff = new_el_time - old_el_time
                                if old_slv_time == 0: slv_denom = 1
                                if old_el_time == 0: el_denom = 1
                                if abs(slv_diff) <= 2: slv_diff = 0
                                if abs(el_diff) <= 2: el_diff = 0
                                # calculate percent change (in increments of 10%) in solve and elapse times
                                result[9]  = 10*int(10*slv_diff/float(slv_denom))
                                result[10] = 10*int(10*el_diff/float(el_denom))
                                # get the size of the plotfile
                                result[7] = os.path.getsize(pltname)
                                # do a diff on the log file
                                flog.close()
                                flog = open(logname, 'r')
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

# print a summary to the log file
results.write("\nSummary:\n")
results.write("\tNormal termination : " + str(norms) + "\n")
results.write("\tError termination  : " + str(nerrs) + "\n")
results.close()

# compare results.txt with nightly_'plat'.txt
os.chdir("..")
results = open(res_name + ".txt", "r")
std_name = res_name + "_std"
std = open(std_name + ".txt", "r")
for line in difflib.unified_diff(results.readlines(), std.readlines(), n=0):
        sys.stdout.write(line)
results.close()
std.close()

# copy the results file to the Logs directory
res_date = res_name + "_" + str(datetime.date.today()) + ".txt"
shutil.copy(res_name + ".txt", "Logs/" + res_date)
