#! /usr/bin/env python
# -*- coding: utf-8 -*-

#This file is used to parse the nightly emails received
#from the various cron jobs. It will compare the output of
#each job and determine which tests produced varying results
#on each of the machines

#import 
import os, platform, smtplib, sys, subprocess, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# imports from separate parser files
from CompareResults import CompareResults
from ParseEmails import ParseFiles
#Uncomment the following line if you want to save to an Excel file
#from SaveResults_EXCEL import SaveFinalResultsExcel
from SaveResults_HTML import SaveFinalResultsHTML
from Results import *

subprocess.call(['svn', 'up', '../Nightly_Runs/']);

#Create an instance of the class so it can hold the results
results = Results ()
results.setFiles(['cibc-rd7.txt', 'cibc-rd4.txt', 'katan.txt', 'swell.txt', 'winxp.txt', 'FEBio2.txt'])

ParseFiles(results)
CompareResults(results)
#Uncomment if you need to save it to an excel file
#SaveFinalResultsExcel(results)
SaveFinalResultsHTML(results)

print("Finished Parsing - Sending Email" ); 

#Send out the results in an email 

#Now email off the results from the parsing. 
host = platform.node().split('.')[0]
today = datetime.date.today()
me = 'scirun-tester@sci.utah.edu'
os.chdir("C:/Testing/Nightly_Parsing/Nightly_Results/")
fp = open('nightly_results-' + str(today) + '.html, 'r')
msg = MIMEText(fp.read(), 'html')
fp.close()
msg['Subject'] = 'Nightly Parser ' + host
you = bryce.c.hayden@gmail.com
#you = 'febio-test@sci.utah.edu'
msg['From'] = me
msg['To'] = you
s = smtplib.SMTP('mail.sci.utah.edu')
s.sendmail(me, [you], msg.as_string())
s.quit()