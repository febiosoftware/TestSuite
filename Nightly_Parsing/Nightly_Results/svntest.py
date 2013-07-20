import os, glob, platform, shutil, sys, subprocess, difflib, datetime, time


#SVN Commit the parsing file
url = '/url:https://gforge.sci.utah.edu/svn/MRLProjects/Testing/Nightly_Parsing/Nightly_Results'
current = os.getcwd()
cwd = current.replace("\\", "/")

path = '/path:' + cwd + '/cibc-rd7.txt'
print "Path: " + path

subprocess.Popen(['TortoiseProc.exe', '/command:commit', '/message: committing parsing results', url, path, '/closeonend:0'])
#subprocess.call(['svn', 'ci', parsingFile, '-m', '"Commiting nightly files for Parsing"'])
