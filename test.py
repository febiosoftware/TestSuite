#! /usr/bin/env python
# -*- coding: utf-8 -*-
#import os
#import glob
#import sys
#import platform
#import shutil
#import filecmp
#import difflib
#import datetime
import subprocess
#import smtplib
#import csv
#import time
#from email.mime.text import MIMEText
#import struct

#os.system("cd ~/Testing")
#print(os.getcwd())

#name = "FEBio"
#print(name.lower())

#version = 4672
#febio = "febio.lnx64"
#plat = "lnx64"
#shutil.copy(febio, febio.split('.')[0] + '_' + version + '.' + plat)

#tmp = "4632"
#svn_version = open("svn_version.py", "w")
#svn_version.write("version = " + tmp)
#svn_version.close()
#from svn_version import version
#if version > 0: print(version)

output = subprocess.call(["svn", "up"])
version_str = subprocess.Popen(["svn", "up"], stdout=subprocess.PIPE).communicate()[0]
version_str = version_str.decode("utf8")
print(version_str)
#lines = version_str.split("\n")
#lines = [line.strip() for line in lines]
#for line in lines:
#	if line.find("revision") !=-1:
#		version = line.split(" ")[2].strip(".")
#version = "0"
#if output == 0: print("worked")

#if time.time() - os.path.getctime("febio.xml") > 43200:
#	print("Older than 12 hours")
#else:
#	print("Younger than 12 hours")

#flog = open("pardiso_op01_std.log", "r")

#result = [0, 0, 0]
#for line in flog:
#	if line.find("Final objective value") !=-1:
#		result[2] = line[28:39]
#		print(result)
#		print(line.split()[3])
#flog.close()

#from logdata import dfield

#dfield0 = [item[0] for item in dfield]
#print(dfield0)
#print(dfield)
#row = dfield0.index('co04')
#print(row)
#print(dfield[row][1])

#n = 0
#found = 0
#flog = open("pardiso_co08.log", "r")
#time1 = "0.6"
#time2 = "Time = " + time1 + "\n"
#print(time2)

#for line in flog:
#	if line.find(time2) !=-1: found = 1
#	if found: n += 1
#	if n == 3:
#		print(line.rstrip("\n").split(" ")[1])
#		found = 0
#		n = 0
#flog.close()

#result = [0, 0, 0]
#n = 0
#flog = open("pardiso_ht01.log", "r")
#for line in flog:
#	if line.find("N O N L I N E A R") !=-1:
#		result.append(line3.rstrip("\n").split(" ")[1])
#		print(result)
#	n += 1
#	print(n)
#	if n > 2: line3 = line2
#	if n > 1: line2 = line1
#	line1 = line
#flog.close()


#print platform.architecture()
#print platform.uname()
#print struct.calcsize('P')

#febio   = '/home/sci/rawlins/FEBio/bin/febio.lnx64'
#logname = '/scratch/rawlins/febio_test/pardiso_bp04.log'
#pltname = '/scratch/rawlins/febio_test/pardiso_bp04.plt'
#cnfname = '/home/sci/rawlins/FEBio/pardiso.xml'
#f       = 'bp04.feb'

#dummyname = '/scratch/rawlins/febio_test/dummy.txt'
#dummy = open(dummyname, "w")

#os.chdir("Verify")
#command = [febio, '-i', f, '-o', logname, '-p', pltname, '-cnf', cnfname]
#val = subprocess.call(command, stdout=dummy)
#print "Subprocess result: ", val
#print os.path.expanduser("~")
#cd_list = cur_dir.split('/')
#user = cd_list[3]
#print user

#sys.path.append(".")
#from data import new, modified
#print new
#print modified
#if time.time() - os.path.getctime("test.py") < 30:
#  print "Short time"
#else: print "Long time"
#a = 1
#b = 0
#if a and not b: print "works"
#sys.exit("this is an exit")
#print "a", a
#frp = open("tmp.txt", "r")
#fwp = open("tmp2.txt", "w")
#line = frp.readline()
#base = 'bp04'
#if base in line: print line
##fwp.write(line)
#line = frp.readline()
#if base in line: print line
##fwp.write(line)
#test = [1]
#print len(test)
#if len(test) != 0: print "empty list"
#st1 = "[123"
#print st1
#print st1[0]
#b_new = 0
#if b_new: print "b_new"
#frp.close()
#fwp.close()
#frp = open("tmp.txt", "r")
#counter = [1, 2, 3]
#for i in counter:
#  print frp.readline()
#frp.close()


#one = ['a', 'b', 'c']
#two = ['d', 'e', 'f']
#three = ['g']
#one += two + three
#print one

#print len(sys.argv)
#if len(sys.argv) > 1: args = sys.argv[1]
#else: args = ''
#print args
#if args.find('c') != -1: print "success"

#test = 54432
#print 5*(test/5000)

#temp = ['four', 'five']
#exempt = ['one',
#	'two', # this is a comment
#	'three'] + temp
#print exempt

#os.remove('tmp.txt')

#host = platform.node().split('.')[0]
#print host

#fp = open("nightly_win.txt", "rb")
#msg = MIMEText(fp.read())
#fp.close()
#msg['Subject'] = 'Test python email'
#me = 'rawlins@sci.utah.edu'
#you = 'rawlins@sci.utah.edu'
#msg['From'] = me
#msg['To'] = you
#s = smtplib.SMTP('mail.sci.utah.edu')
#s.sendmail(me, [you], msg.as_string())
#s.quit()

#test = 5
#if test < 10: incr = 1
#elif test < 20: incr = 2
#elif test < 50: incr = 5
#else: incr = 10
#print incr, 100/incr

#version = subprocess.Popen(["subwcrev", "."], stdout=subprocess.PIPE).communicate()[0]
#print "svn version : " + version + "\n"

#val1 = 5
#val2 = 2
#diff = val2 - val1
#if abs(diff) <= 2: diff = 0
#print "diff = ", diff

#ftest = open("test.txt", "w")
#test = subprocess.Popen(["svnversion"], stdout=subprocess.PIPE).communicate()[0]
#print "Version: ", test

#ftest.write(test)

#std = open("Examples/congneo_std.log", 'r')
#log = open("congneo_std.log", 'r')
#for line in log:
#	if line.find("Nr of equations") != -1:
#		eqs = int(line[47:])
#		mn1 = int(line[19:21])
#		sc1 = int(line[22:24])
#	if line.find("Elapsed time") != -1:
#		hr2 = int(line[16:17])
#		mn2 = int(line[18:20])
#		sc2 = int(line[21:23])
#print 'Equations ', eqs
#print 'Elapsed Hr, Min, Sec ', hr2, mn2, sc2
#slv_time = hr1*3600 + mn1*60 + sc1
#el_time = hr2*3600 + mn2*60 + sc2
#print slv_time, el_time, 10*int(10*(slv_time-el_time)/float(el_time))
#print slv_time, el_time, slv_time/el_time, el_time/slv_time

#name = "file"
#print name
#date = datetime.date.today()
#print date
#name = name + str(date)
#print name
#test = "test.txt"
#shutil.copy("febio.xml", "Logs/" + test)

#diff = 352
#print diff/1000

#std = open("co02_1.log", "r")
#log = open("co02_2.log", "r")
#diff = open("diff.txt", "w")
#for line in difflib.unified_diff(log.readlines(), std.readlines(), n=0):
#        diff.write(line)
#log.close()
#std.close()
#diff.close()

#katan = open('katan.txt', 'r')
#tmp = open('katan_tmp.txt', 'w')
#for line in katan:
#	tmp.write(line.replace('L',''))
#katan.close()
#tmp.close()

#dir1 = '/home/sci/rawlins/Projects/Nike3d/nike3d'
#dir2 = '/home/sci/rawlins/Projects/Nike3d/ddfc'
#dir3 = '/home/collab/mpuso/hip_joint_results/Nike3d'
#dir4 = '/home/collab/mpuso/hip_joint_results/Nike3dn'
#os.chdir(dir1)
#common = glob.glob('*')
#print common
#compare = filecmp.cmpfiles(dir1, dir4, common)
#print compare[0]
#print 'Files Differ:'
#for f in compare[1]:
#	if f.find('mod') == -1 and f.find('o') ==-1:
#		print f
#print compare[1]
#print 'Files that exist only in first directory:'
#for f in compare[2]:
#	if f.find('o') == -1:
#		print f
#print compare[2]
#logname = 'Verify/fi12.log'
#result = ['Pardiso', 'fi12', "", 0, 0, 0, 0, 0]
#try:
#	flog = open(logname, 'rt')
#	
#	for line in flog:
#		if  line.find("Number of time steps completed"        ) != -1: result[3] = int(line[55:])
#		if  line.find("Total number of equilibrium iterations") != -1: result[4] = int(line[55:])
#		if  line.find("Total number of right hand evaluations") != -1: result[5] = int(line[55:])
#		if  line.find("Total number of stiffness reformations") != -1: result[6] = int(line[55:])
#	flog.close()
#	result[7] = os.path.getsize('Verify/fi12.plt')
#except IOError:
#	result[2] = 'Fail'
#except OSError:
#	result[2] = 'Fail'
#print result

#test = 'hipb.feb'
#print test.rstrip('.feb')
#print test.split('.')[0]
#nums = ['one', 'two', 'three']
#test1 = 'on'
#test2 = 'e'
#if test1 + test2 not in nums:
#	print 'not in nums'
#else:
#	print 'in nums'
#var = '12345678'
#print var[:4]
#opsys = os.environ['HOME']
#print platform.machine()
#print 'febio.' + platform.node().split('.')[0]
#print platform.node().split('.')[0]
#print sys.platform
#print os.uname()
#print os.path.getsize('katan.csv')
#print os.environ['OMP_NUM_THREADS']
#os.environ['OMP_NUM_THREADS'] = '1'
#print os.environ['OMP_NUM_THREADS']
#print os.getenv('OMP_NUM_THREADS')

#os.chdir('/home/sci/rawlins/FEBio')
#os.system("svn up")

#shutil.copy('katan.csv','copied.txt')

#os.chdir("../bin")
#dir = glob.glob("febio.*")
#dir.sort()
#print dir
#for file in dir:
#	flist = file.split(".")
#	name = flist[0]
#	print name
