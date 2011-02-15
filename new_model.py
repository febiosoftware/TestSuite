#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, platform, sys, shutil, subprocess
# This script creates the standard log file for new models

# Determine the operating system
opsys = platform.machine()
sysplat = sys.platform
bits = platform.architecture()[0]

# Set the solvers
solvers = ['pardiso', 'superlu']

# Set the platform
if opsys == 'i386':
        plat = 'osx'
elif opsys == 'x86_64':
        plat = 'lnx64'
elif sysplat == 'win32':
        plat = 'win'
elif opsys == 'i686':
        plat = 'lnx32'

# Use one thread
os.environ['OMP_NUM_THREADS'] = '1'

# Define the febio executable
if plat == 'win':
        febio_dir = 'C:/FEBio'
        if bits == '64bit':
                exe_dir = febio_dir + '/x64/Release-x64'
        else:
                exe_dir = febio_dir + '/Release'
        febio = exe_dir + '/FEBio.exe'

        out_dir = ''
else:
        # Assumes that this script is run from FEBio/Testing
        # and that the executable is in FEBio/bin
        os.chdir("..")
        febio_dir = os.getcwd()
        febio = febio_dir + '/bin/febio.' + plat

        # Define the log and plt output directory
        out_dir = '/scratch/rawlins/febio_test/'

# Define the new models to be run
os.chdir(febio_dir + "/Testing/Verify")
new_mod = ['bp11', 'bp12', 'bp13', 'bp14']

# Exempt models
exempt = ['superlubp12', 'superlubp13']

#run the new models
for solver in solvers:
        for f in new_mod:
		if solver + f not in exempt:
			# define the log and plt files
			in_file = f + '.feb'
			logname = out_dir + solver + '_' + f + '.log'
			logstd = out_dir + solver + '_' + f + '_std.log'
			# open the dummy file
			dummyname = out_dir + "dummy.txt"
			dummy = open(dummyname, "w")
			# run the FEBio problem
			command = [febio, '-i', in_file, '-o', logname, \
				'-cnf', febio_dir + '/' + solver + '.xml']
			print command
			val = subprocess.call(command, stdout=dummy)
			try:
				shutil.copy(logname, logstd)
			except IOError:
				print "Error copying files"
