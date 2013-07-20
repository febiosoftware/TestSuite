import os, glob, platform, shutil, sys, subprocess, difflib, datetime, time


#SVN Commit the parsing file
url = '/url:https://gforge.sci.utah.edu/svn/MRLProjects/Testing/Nightly_Parsing/Nightly_Results'
current = os.getcwd()
cwd = current.replace("\\", "/")

path = ' /path:' + cwd + '/cibc-rd7.txt'
arguments = '/command:commit ' +url + path, '\/message: "committing parsing results" /closeonend:2'
subprocess.call(['TortoiseProc.exe', arguments])
