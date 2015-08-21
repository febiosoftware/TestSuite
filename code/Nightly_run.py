#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from TestConfig	import TestConfig
from Suite 	import Suite
from Files 	import Files
from Build 	import Build
from RunTest	import RunTest

class Nightly:
	# Constructor
	def __init__(self):
		self.test_config = TestConfig()
		self.suite       = Suite(self.test_config)
		self.files       = Files()

	# Run the test suite
	def runNightly(self):
		

	# Output configuration parameters
	def output(self):
		

# Main
def main():
	nightly = Nightly()
	nightly.runNightly()

if __name__ == '__main__':
    main()
