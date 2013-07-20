'''
Created on Sep 10, 2012

@author: Bryce
'''
from xlwt3 import Workbook
import datetime

def SaveFinalResultsExcel(Results):
    currentRow = 0 
    
    wb = Workbook()
    ws = wb.add_sheet('Testing Results')
    
    ws.write(0,0,'Files Tested')
    currentRow += 1
    
    ### Output the number of files ran per machine ###
    for file in Results._files:
        machine = file.replace("../Resources/","")
        machine = machine.replace(".txt","")
        ws.write(currentRow, 0, machine)
        ws.write(currentRow, 1, str(Results._current_Output[file]['Numb Files']))
        currentRow += 1
    
    #### Output the any errors in the standard files ####
    currentRow += 1
    ws.write(currentRow,0, 'Standard Files Errors')
    currentRow += 1
    for file in Results._files:
        machine = file.replace("../Resources/", "")
        machine = machine.replace(".txt", "")
        for key in Results._standard_Errors[file].keys():
            ws.write(currentRow, 0, machine + " - " + key)
            for col in range (len(Results._standard_Errors[file][key])):
                ws.write(currentRow, col+1, Results._standard_Errors[file][key][col])
            currentRow += 1
    
    #### Standard Files Missing ####
    currentRow += 1
    ws.write(currentRow,0, 'Missing Standard Files')
    currentRow += 1
    
    for file in Results._files:
        machine = file.replace("../Resources/", "")
        machine = machine.replace(".txt", "")
        for key in Results._standard_Missing[file]:
            ws.write(currentRow, 0, machine)
            ws.write(currentRow, 1, key)
            currentRow += 1
    
    #### Output the Error terminations #### 
    currentRow += 1
    ws.write(currentRow,0, 'Error Terminations')
    currentRow += 1
    
    
    #Write the Machine names across the top
    currentCol = 1
    for file in Results._files:
        machine = file.replace("../Resources/", "")
        machine = machine.replace(".txt", "")
        ws.write(currentRow, currentCol, machine)
        currentCol += 1
    currentRow += 1
        
    #Loop through the files and output errors
    for file in Results._files:
        for key in Results._current_Errors.keys():
            ws.write(currentRow, 0, key)
            for col in range (len(Results._current_Errors[key])):
                ws.write(currentRow, col+1, Results._current_Errors[key][col])
            currentRow += 1
    
    #### Write out the Variations 
    currentRow += 1
    ws.write(currentRow,0, 'Variations')
    currentRow += 1
    ws.write(currentRow, 0, '- = Nothing Wrong')
    ws.write(currentRow, 2, 'M = Missing Standard')
    ws.write(currentRow, 4, 'R = Residual')
    ws.write(currentRow, 6, 'S = Steps')
    ws.write(currentRow, 8, 'U = Unknown Issue')
    currentRow += 1  
    #Write the Machine names across the top
    currentCol = 1
    for file in Results._files:
        machine = file.replace("../Resources/", "")
        machine = machine.replace(".txt", "")
        ws.write(currentRow, currentCol, machine)
        currentCol += 1
    currentRow += 1 
    
    for key in Results._variations.keys():
        ws.write(currentRow, 0, key)
        for col in range (len(Results._variations[key])):
            ws.write(currentRow, col+2, Results._variations[key][col])
        currentRow += 1
    
    today = datetime.date.today()
    ExcelFile = '../Results/Results-' + str(today) + '.xls'
    wb.save(ExcelFile)