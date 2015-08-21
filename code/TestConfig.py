#! /usr/bin/env python
# -*- coding: utf-8 -*-

import platform, os, sys

class TestConfig:
	'Class to configure the test being run'

	#========== Member Variables ==========
	#	plat
	#	platd
	#	host
	#	opsys
	#	febio_name
	#	febio_dir
	#	febio_exe
	#	test_dir
	#	output_dir
	#	logs_dir
	#	verify
	#	dir_ext
	#	res_name
	#	std_name
	#	solvers
	#	b_compile
	#	b_test
	#	b_4threads

	#============ Member Methods ==========
	#	__init__
	#	SetPlat
	#	SetOps
	#	SetPaths
	#	DisplayPlat
	#	DisplayFEBio

	#===================================================
	def __init__(self, plat):
		
		if len(sys.argv) == 1:
			sys.exit("error: The name of the FEBio directory must be entered as an argument")
		
		# Set the platform
		self.SetPlat()
		
		# Set which version of FEBio to use
		self.febio_name = sys.argv[1]
		
		# Read the commandline arguments
		if len(sys.argv) > 2:
			ops = sys.argv[2]
			self.SetOps(ops)
		else: ops = ''
		
		# Set the directory and file names
		self.SetPaths()
		
	#===================================================
	def SetPlat(self):
		self.host = platform.node().split('.')[0]
		self.opsys = platform.machine()
		
		if self.opsys == 'x86_64':
			if self.host == 'katan':
				self.plat = 'osx'
			else:
				self.plat = 'lnx64'
			self.platd = self.plat + 'd'
		elif sys.platform == 'win32':
			self.plat = 'win'
		elif sys.platform == 'i686':
			self.plat = 'lnx32'
		
	#===================================================
	def SetOps(self, ops):
		# Arguments are any of:
		# c: do not compile
		# a: run Pardiso, SuperLU and Skyline
		# t: test on a few problems
		# 4: run with 4 threads

		# Set the number of threads
		self.dir_ext = ""
		if ops.find('4') != -1:
			self.b_4threads = 1
			self.dir_ext = "4"
			os.environ['OMP_NUM_THREADS'] = '4'
		else:
			self.b_4threads = 0
			os.environ['OMP_NUM_THREADS'] = '1'
		
		# Set the solvers
		if ops.find('a') != -1:
			self.solvers = ['pardiso', 'skyline', 'superlu']
		else:
			self.solvers = ['pardiso']
		
		# Set whether or not to compile
		if ops.find('c') != -1: self.b_compile = 0
		else: self.b_compile = 1
		
		# Set whether or not to run a small set of problems
		if ops.find('t') != -1: self.b_test = 1
		else: self.b_test = 0
		
	#===================================================
	def SetPaths(self):
		# Set the main directory names
		tmp = os.getcwd()
		os.chdir('../..')
		root_dir = os.getcwd()
		os.chdir(tmp)
		self.test_dir = root_dir + 'Testing'
		self.febio_dir = root_dir + febio_name
		
		# Set the testing directory and the results file names
		if self.febio_name == 'FEBio':
			self.verify = self.test_dir + '/Verify'
			if self.b_4threads: self.res_name = 'nightly4_' + plat
			else: self.res_name = 'nightly_' + plat
		else:
			self.verify = self.test_dir + '/Verify2'
			if self.b_4threads: self.res_name = 'nightly24_' + plat
			else: res_name = 'nightly2_' + plat
		self.std_name = self.res_name + '_std'
		
		# Set platform dependent paths and variables
		if self.plat == 'win':
			if self.febio_name = 'FEBio':
				self.febio_exe = self.febio_dir + '/VS2010/x64/Release/' + febio_name + '.exe'
			else:
				self.febio.exe = self.febio_dir + '/VS2010/x64/Release OpenMP/' + febio_name + 'x64mt.exe'
			self.output_dir = self.test_dir + self.febio_name + self.dir_ext + 'Logs'
			self.logs_dir = self.output_dir
		else:	# Linux or Mac
			febio_lc_name = self.febio_name.lower()
			self.febio_exe = self.febio_dir + '/bin/' + febio_lc_name + '.' + self.platd
			user = test_dir.split('/')[3]
			self.out_dir = '/scratch/' + user + '/' + febio_lc_name + self.dir_ext + '_test/'
			self.logs_dir = self.febio_name + self.dir_ext + '_Logs/'
				
	#===================================================
	def DisplayPlat(self):
		print("host = " + self.host)
		print("opsys = " + self.opsys)

	#===================================================
	def DisplayFEBio(self):
		print(self.febio_name)
		