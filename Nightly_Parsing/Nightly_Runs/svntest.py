import os, glob, platform, shutil, sys, subprocess, difflib, datetime, time

#SVN Commit the parsing file
url = '/url:https://gforge.sci.utah.edu/svn/MRLProjects/Testing/Nightly_Parsing/Nightly_Results'
current = os.getcwd()
cwd = current.replace("\\", "/")

path = ' /path:' + cwd + '/cibc-rd7.txt' #cibc-rd7.txt is just a test file I was experimenting with
arguments = '/command:commit ' +url + path, ' \/logmsg: "committing parsing results" /closeonend:4'
subprocess.call(['TortoiseProc.exe', arguments])