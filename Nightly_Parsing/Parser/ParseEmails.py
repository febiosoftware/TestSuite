def CleanUpLine (line):
    line = line.replace("+", "")    #Remove any +
    line = line.replace("-", "")    #Remove any -
    line = line.replace("[", "")    #Remove any [
    line = line.replace("]", "")    #Remove any ]
    line = line.replace("'", "")    #Remove any '
    line = line.replace(" ", "")    #Remove whitespace
    line = line.replace("\n", "")    #Remove any new line characters
    
    return line

def RemoveLong (parsedLine):
    #Some of the systems store the size with a long integer so there's an L
    #attached that needs to be removed. 
    parsedLine[5] = parsedLine[5].replace("L", "")
    parsedLine[6] = parsedLine[6].replace("L", "")
    
    return parsedLine

def ParseFiles (Results):
    #with forces the file to close even if the program exits
    #unexpectedly. This portion will loop through the emails
    #gather the data and create hashmaps for each item.
    for file in Results._files:
        with open(file) as nightly_winxp:
            GatherData = False
            
            Results._current_Errors = {}
            Results._current_Output[file] = {}
            Results._current_Output[file]['Data'] = {}
            Results._current_Variations[file] = {}
            
            Results._standard_Errors[file] = {}
            Results._standard_Output[file] = {}
            Results._standard_Output[file]['Data'] = {}
            Results._standard_Missing[file] = set()
            
            
            
            #Pull a line at a time from the file to parse
            for line in nightly_winxp:
                #Check to make sure excess header info has been removed
                #Get the machine name
                if (not GatherData and line[0:6] == 'host ='):
                    Machine = CleanUpLine(line[6:])
                    Results._current_Output[file]['Machine'] = Machine
                    continue
                    
                #Get the operating system used
                elif(not GatherData and line[0:7] == 'opsys ='):
                    GatherData = True
                    opsys = CleanUpLine(line[7:])
                    Results._current_Output[file]['OpSys'] = opsys
                    continue
                            
                #Parse the line
                if(GatherData):
                    if(line[0] == '['):
                        line = CleanUpLine(line)
                        parsedLine = line.split(",")
                        key = parsedLine[0] + "_" + parsedLine[1]
                        data = RemoveLong(parsedLine[2:])
                        Results._current_Output[file]['Data'][key] = data
                    
                    elif(line[0:2] == "-["):
                        line = CleanUpLine(line)
                        parsedLine = line.split(",")
                        key = parsedLine[0] + "_" + parsedLine[1] 
                        data = RemoveLong(parsedLine[2:])
                        Results._current_Variations[file][key] = data
                        
                    elif(line[0:2] == "+["):
                            line = CleanUpLine(line)
                            parsedLine = line.split(",")
                            key = parsedLine[0] + "_" + parsedLine[1] 
                            data = RemoveLong(parsedLine[2:])
                            Results._standard_Output[file][key] = data
                            
            
            #This is used to see if the machines are running the same number of test. 
            #If these numbers aren't the same then the comparisons will be out of whack
            Results._current_Output[file]['Numb Files'] = len(Results._current_Output[file]['Data'])
        nightly_winxp.close()  