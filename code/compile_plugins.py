#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, subprocess, shutil
from datetime import date

# This file compiles the plugins for the nightly test suite
#==========================================================

class CompilePlugins:
	def __init__(self, plat, root_dir):
		self.plat = plat
		self.root_dir = root_dir
		self.test_dir = root_dir + 'Testing/'
		self.plugins_dir = root_dir + 'Software/Plugins/'
		self.plugins = ['NeoHookeanPI', 'FEWarp', 'Angio', 'PreStrain', 'AngioFE2']

	# compile using Makefile
	def compileMake(self):

		if self.plat == 'lnx64s': ext = '.so'
		else: ext = '.dylib'
		i = 0
		
		# Compile the plugins
		for plugin in self.plugins:
			i = i + 1
			os.chdir(self.plugins_dir + plugin + '/build')
			command = ['make', self.plat]
			output = subprocess.call(command)
			if output != 0: print(plugin + " did not compile")
			else:
				try:
					plugin_lc = plugin.lower()
					from_name = 'lib/lib' + plugin_lc + '_' + self.plat + ext
					if i == 4 or i == 5:
						shutil.copy(from_name, self.test_dir + 'Verify2/plugins')
					else: 
						if i == 3: from_name = 'lib/lib' + plugin_lc + 'fe_' + self.plat + ext
						to_name = self.test_dir + 'Verify2/plugins/pi0' + str(i) + '_' + self.plat + ext
						shutil.copy(from_name, to_name)
				except IOError: print("Error copying " + from_name)

	# compile using Visual Studio
	def compileVS(self):

		i = 0
		d = str(date.today())
		os.chdir(self.test_dir + "code")
		
		for plugin in self.plugins:
			i = i + 1
			command = ['compile_plugin.bat', plugin, d]
			output = subprocess.call(command)
			if output != 0: print(plugin + " did not compile")
			else:
				try:
					from_name = self.plugins_dir + plugin + '/VS2013/x64/Release/' + plugin + '.dll'
					if i == 4 or i == 5:
						shutil.copy(from_name, self.test_dir + 'Verify2/plugins')
					else: 
						if i == 3: from_name = self.plugins_dir + plugin + '/VS2013/x64/Release/' + plugin + 'FE.dll'
						to_name = self.test_dir + 'Verify2/plugins/pi0' + str(i) + '_' + self.plat + '.dll'
						shutil.copy(from_name, to_name)
				except IOError: sys.exit("Error copying " + plugin)

	# run the program
	def launch(self):

		# Update the Plugins directory
		os.chdir(self.plugins_dir)
		subprocess.call(['svn', 'up'])
		
		if self.plat == 'win': self.compileVS()
		else: self.compileMake()
