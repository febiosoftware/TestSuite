import sys, os.path
from logdata import *


if len(sys.argv) == 1:
    print("Pass log file as argument.")
    sys.exit()
    
if not os.path.isfile(sys.argv[0]):
    print(sys.argv[1] + " does not exist.")

with open(sys.argv[1]) as log:
    for line in log:
        if not line.startswith('    '):
            continue
        
        splitLine = line.split(':');
        
        test = splitLine[0].strip();
        results = splitLine[1].split('|')
        
        for index in range(len(results)):
            if '(' in results[index]:
                result = results[index].split('(')[0].strip()
                
                if "'" in result:
                    stdResults[test][index + 1] = result.replace("'", '')
                else:
                    stdResults[test][index + 1] = int(result)
                    
                    
with open("logdata.py", "w") as ldata:
    ldata.write("dataField = " + str(dataField).replace("', ", "',\n        ") + "\n\n")
    ldata.write("exemptTests = " + str(exemptTests) + "\n\n")
    ldata.write("paramOpt = " + str(paramOpt) + "\n\n")
    ldata.write("stdResults = " + str(stdResults).replace("], ", "],\n        ") + "\n\n")
        
