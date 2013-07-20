'''
Created on Aug 10, 2012

@author: Bryce
'''
#This file is used to parse the nightly emails received
#from the various cron jobs. It will compare the output of
#each job and determine which tests produced varying results
#on each of the machines

#import the functions declared in other files
from CompareResults import CompareResults
from ParseEmails import ParseFiles
#Uncomment the following line if you want to save to an Excel file
#from SaveResults_EXCEL import SaveFinalResultsExcel
from SaveResults_HTML import SaveFinalResultsHTML
from Results import *

#Create an instance of the class so it can hold the results
results = Results ()
results.setFiles(['rd7.txt', 'rd4.txt', 'swell.txt', 'winxp.txt', 'FEBio2.txt'])

ParseFiles(results)
CompareResults(results)
#Uncomment if you need to save it to an excel file
#SaveFinalResultsExcel(results)
SaveFinalResultsHTML(results)

print("Finished Parsing" ); 