#! /usr/bin/env python

import subprocess

# This function does an svn update

def svn_update:
	subprocess.call(['svn', 'up'])
	return
