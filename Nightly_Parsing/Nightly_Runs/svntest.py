import os, glob, platform, shutil, sys, subprocess, difflib, datetime, time

#SVN Commit the parsing file
subprocess.call(['svn', 'commit - m "Updated nightly parser"'])

