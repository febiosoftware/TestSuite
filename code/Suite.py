#! /usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess, os, glob, time

class Suite:
	'Class to set up the test suite problems'
	
	#========== Member Variables ==========
	#	test_suite
	#	b_test_update
	#	data_field
	#	data_field0
	#	new
	#	modified
	#	deleted
	#	exempt
	#	paramopt
	#	paramopt0
	#	b_new
	#	b_del

	#============ Member Methods ==========
	#	__init__

	#===================================================
	def __init__(self, TC):

		# Set the test suite problems
		if TC.b_cmpl: subprocess.call(['svn', 'up'])
		if TC.b_test:
			self.test_suite = ['co01.feb', 'co02.feb']
		else:
			os.chdir(TC.verify)
			self.test_suite = glob.glob('*.feb')
			self.test_suite.sort()
			os.chdir('..')
			
		
		# If verifymod.txt has changed, the test suite has changes that need to be run.
		# Run 'date +%D > verifymod.txt' on the commanline if there are changes.
		# 86400 is the number of seconds in a day.
		self.b_test_update = 0
		if time.time() - os.getmtime('verifymod.txt) < 86400: self.b_test_update = 1
		
		# See if any of the problems have bee updated
		else:
			for f in self.test_suite:
				if time.time() - os.path.getmtime(TC.verify + "/" + f) < 86400:
					b_test_update = 1
					break

		# Import the problems that report extra data fields
		from logdata import dfield
		self.data_field = dfield
		self.data_field0 = [col[0] for col in dfield]
		
		# Import the problems that are new, modified or deleted
		from update import new, modified, deleted
		self.new = new
		self.modified = modified
		self.deleted = deleted
		self.b_new = 0
		self.b_del = 0
		if len(new) + len(modified) != 0: self.b_new = 1
		if len(deleted) != 0: self.b_del = 1
		
		
		# Exempt problems:
		self.exempt = ['oi01', 'oi02'] # Parameter optimization input files
		
		# Parameter optimization problems
		self.paramopt = [['op01', 'oi01'],
						 ['op02', 'oi02'],
						 ['op03', 'oi01'],
						 ['op04', 'oi02']]
		self.paramopt0 = [col[0] for col in self.paramopt]