#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, subprocess, time, shutil

class Build:
	'Class to build the executables'
	
	#========== Member Variables ==========
	#	version

	#============ Member Methods ==========
	#	__init__

	#===================================================
	def __init__(self, TC):

		os.chdir(TC.febio.dir)
		
		# Update FEBio
		if TC.plat != 'osx': subprocess.call(['svn', 'up'])
		version_str = subprocess.Popen(['svnversion'], stdout=subprocess.PIPE).communicate()[0]
		self.version = version_str.split("\n")[0]
			
	#===================================================
	def BuildFEBio(self, TC)
		
		# Build FEBio
		os.chdir(TC.febio.dir)
		if TC.plat = 'win':
			#Todo: windows
		else:	# Linux and Mac
			os.chdir('build')
			command = ['make', TC.platd]
			output = subprocess.call(command)
			if output == 0:
				# Test whether febio compiled in the last 20 hours
				if time.time() - os.path.getctime(TC.febio_exe) > 72000 and not TC.test_update == -1:
				return 1	
	
				# If FEBio did compile, create a copy.
				try:
					shutil.copy(TC.febio_exe, TC.febio_exe.split('.')[0] + str(self.version) + '.' + platd)
				except: IOError:
					return 2
			else: return 3	# FEBio didn't compile
			return 0