#! /usr/bin/env python
# -*- coding: utf-8 -*-

class Files:
	'Class for file manipulation'
	
	#========== Member Variables ==========
	#	results
	#	f_std_results
	#	f_std_results_tmp
	#	std_results
	#	std_results_tmp
	#	dummy
	#	log
	#	std_log

	#============ Member Methods ==========
	#	OpenResults
	#	OpenStdResults
	#	OpenStdResultsTmp
	#	WriteStdResultsTmp
	#	OpenDummy
	#	OpenLog
	#	OpenStdLog

	#===================================================
	def OpenResults(self, TC):

		self.results = open(TC.test_dir + '/' + TC.res_name + '.txt', 'w')

	#===================================================
	def OpenStdResults(self, TC):
		
		self.f_std_results = TC.test_dir + "/" + TC.std_name + '.txt'
		self.std_results = open(self.f_std_results, 'r')

	#===================================================
	def OpenStdResultsTmp(self, TC):
		
		self.f_std_results_tmp = TC.test_dir + "/" + TC.std_name + ".txt"
		self.std_results_tmp = open(self.f_std_results_tmp, 'w')

	#===================================================
	def WriteStdResultsTmp(self, TC)
		
		# Write the header of the std_tmp file
		std_line = self.std.readline()
		while std_line[0] != "[":
			self.std_tmp.write(std_line)
			std_line = self.std.readline()

	#===================================================
	def OpenDummy(self, dummyname):

		self.dummy = open(dummyname, 'w')

	#===================================================
	def OpenLog(self, fname):

		self.log = open(fname, 'r')

	#===================================================
	def OpenStdLog(self, fname):

		self.std_log = open(fname, 'r')
	