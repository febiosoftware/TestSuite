#! /usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess, os, shutil

class RunTest:
	'Class to run a test suite problem'
	
	#========== Member Variables ==========
	#	solver
	#	input_file
	#	base
	#	df_time
	#	df_time_str
	#	df_flg
	#	found
	#	data1
	#	line_num
	#	logname
	#	log_std
	#	pltname
	#	log_diff
	#	dummyname
	#	opt
	#	return_val
	#	result
	#	norms
	#	nerrs

	#============ Member Methods ==========
	#	__init__
	#	RunFEBio
	#	Results
	#	ParseLog
	#	ParseStdLog
	#	CalcTimes

	#===================================================
	def __init__(self, solver, input_file, TC, suite)
		
		self.solver = solver
		self.input_file = input_file
		# Strip the .feb from the input file name
		self.base = input_file[:4]
		if self.base not in suite.exempt:
			# Test for data field problems
			if self.base in suite.data_field0:
				self.df_time = suite.data_field[suite.data_field0.index(self.base)][1]
				self.df_time_str = "Time = " + self.df_time + '\n'
				self.df_flg = 1
				self.found = 0
				self.data1 = 0
				self.line_num = 0
			else: self.df_flg = 0
			
			# Define the log and plot files
			self.logname = TC.output_dir + solver + '_' + self.base + '.log'
			self.log_std = TC.output_dir + solver + '_' + self.base + '_std.log'
			self.pltname = TC.output_dir + solver + '_' + self.base + '.xplt'
			self.log_diff = TC.output_dir + solver + '_' + self.base + '_diff.txt'
			self.dummyname = TC.output_dir + "dummy.txt"

	#===================================================
	def RunFEBio(self, TC, suite, files)
		
		os.chdir(TC.verify)
		files.OpenDummy(self.dummyname)
		
		# Set up the executable command line
		if self.base in suite.paramopt0:
			self.opt = 1
			if TC.febio_name = 'FEBio2':
				opt_input = suite.paramopt0.index(self.base)][1]
				command = [TC.febio_exe, '-i', opt_input + '.feb', '-s', self.input_file, '-o', self.logname, \
				           '-p', self.pltname, '-cnf', TC.test_dir + '/' + self.solver + '.xml']
				#print(command)
			else:
				command = [TC.febio_exe, '-s', self.input_file, '-o', self.logname, '-p', self.pltname \
				           '-cnf', TC.test_dir + '/' + self.solver + '.xml']
		else:
			self.opt = 0
			command = [TC.febio_exe, '-i' self.input_file, '-o', self.logname, '-p', self.pltname \
			           '-cnf', TC.test_dir + '/' + self.solver + '.xml']
			
		# Run the FEBio problem
		self.return_val = subprocess.call(command, stdout = files.dummy)
		
		# Create std log for new and modified problems
		if self.base in suite.new or self.base in suite.modified:
			shutil.copy(self.logname, self.log_std)

	#===================================================
	def Results(self, TC, suite, files)
	
		self.norms = 0
		self.nerrs = 0
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
		if self.opt: self.result = [self.solver, self.base, "", 0, 0, 0.0, 0, 0]

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
		else: self.result = [self.solver, self.base, "", 0, 0, 0, 0, 0, 0, 0, 0, ""]
		
		# Check the return value
		if self.return_val == 0:
			self.result[2] = 'Normal'
			self.norms = self.norms + 1
		else:
			self.result[2] = 'Error'
			self.nerrs = self.nerrs + 1
		
		# Parse the log file for convergence info
		self.ParseLog(files)
		# Parse the standard log file for time data
		self.ParseStdLog(files)
		# Calculate the time differences
		self.CalcTimes()
		
	#===================================================
	def ParseLog(self, files)
	
		try:
			files.OpenLog(self.logname)
			
			if self.opt: # Optimization problems
				for line in files.log:
					if line.find("Major iterations"     ) !=-1: self.result[3] = int(line[43:])
					if line.find("Minor iterations"     ) !=-1: self.result[4] = int(line[43:])
					if line.find("Final objective value") !=-1: self.result[5] = line.split()[3]
			else:		# Regular problems
					if  line.find("Number of time steps completed"        ) != -1: self.result[3] = int(line[55:])
					if  line.find("Total number of equilibrium iterations") != -1: self.result[4] = int(line[55:])
					if  line.find("Total number of right hand evaluations") != -1: self.result[5] = int(line[55:])
					if  line.find("Total number of stiffness reformations") != -1: self.result[6] = int(line[55:])
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
						if line.find("Data Record #1") !=-1: data1 = 1
						if line.find("Data Record #2") !=-1: data1 = 0
						if line.find(df_tline) !=-1 and data1: found = 1
						if found: line_num += 1
						if line_num == 3:
							self.result[11] = line.rstrip("\n").split(" ")[1]
							found = 0
							line_num = 0
		except IOError:
			self.result[2] = 'IOError'
		except OSError:
			self.result[2] = 'OSError'
		
	#===================================================
	def ParseStdLog(self, files)

		try:
			files.OpenLogStd(self.log_std)

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
		except IOError:
			self.result[2] = 'IOError'
		except OSError:
			self.result[2] = 'OSError'
		
	#===================================================
	def CalcTimes(self)

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
