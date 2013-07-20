'''
Created on Aug 10, 2012

@author: Bryce
'''
def CompareResults(Results):            
   for file in Results._files:
        '''
            Loop through the individual test files & standard files to 
            check for any "Error" terminations 
        ''' 
        for key in Results._current_Output[file]['Data'].keys(): 
            #This array will hold the termination results for the individual machines
            fileError = ['-']*len(Results._files)
            
            #loop through the different machines and compare them
            for machineIndex in range (len(Results._files)):
                #Comparing the same data to itself is useless so skip
                if(machineIndex == Results._files.index(file)):
                    continue 
                
                #Take all terminations with an Error and save them.
                elif (Results._current_Output[file]['Data'][key][0] != 'Normal'):
                    fileError[machineIndex] = 'X'
                
                #Check to see if any of the standard files have Error terminations
                elif (key in Results._standard_Output[file]):
                    if (Results._standard_Output[file][key][0] != 'Normal'):
                        Results._standard_Errors[file][key] = Results._standard_Output[file][key];
                        Results._standard_Output[file].pop(key)
                        continue
    
            #Loop through the error list to see if any errors popped up
            if(any('X' in search for search in fileError)):
                Results._current_Errors[key] = fileError
                
            
            
        RemoveList = set()
        #Remove any error terminations from the _current_Variations
        for key in Results._current_Variations[file].keys():
            if(Results._current_Variations[file][key][0] != 'Normal'):
                RemoveList.add(key)
            elif(key in Results._standard_Errors[file].keys()):
                RemoveList.add(key)                    
            
        for key in RemoveList:
            Results._current_Variations[file].pop(key)
            
            
        
        '''
            Now loop through the variations to determine if they are likely 
            a residual error or something more. 
        '''
        for key in Results._current_Variations[file].keys():    
            
            #Variation Array used to hold 
            VariationError = ['-']*len(Results._files)
            
            for machineIndex in range (len(Results._files)):
                #Comparing the same data to itself is useless so skip
                if(machineIndex == Results._files.index(file)):
                    continue 
                
                if(not(key in Results._standard_Output[file])):
                    Results._standard_Missing[file].add(key)
                    VariationError[machineIndex] = 'M'
                    continue
            
                residual = True
                            
                for index in range (len(Results._current_Variations[file][key])):
                    if(Results._current_Variations[file][key][index] == Results._standard_Output[file][key][index]):
                        continue
                    elif (index > 0 and index < 5):
                        if(int(Results._current_Variations[file][key][index]) != int(Results._standard_Output[file][key][index])):
                            VariationError[machineIndex] = 'S'
                    elif ( index > 5):
                        if(int(Results._current_Variations[file][key][index]) > int(Results._standard_Output[file][key][index]) + 50):
                            residual = False

                if(residual):
                    VariationError[machineIndex] = 'R'
                elif (not residual and VariationError[machineIndex] != 'S'):
                    VariationError[machineIndex] = 'U' 
                    
            Results._variations[key] = VariationError
            
'''
Note this function was used to combine the results produced by the 
three compilers. Since we've removed skyline and superlu compilers
this method is no longer need, but is left in in case we decide later
to reinstall & test on these compilers again. 

def ReduceErrorList ():
    for firstKey in errorKeys:
        for secondKey in errorKeys:
            if(firstKey == secondKey):
                continue
            for thirdKey in errorKeys:
                if(secondKey == thirdKey or 
                   firstKey == thirdKey):
                    continue
                
                #Check to see if all three of the compilers had similar erros 
                if(firstKey[-4:] == secondKey [-4:] and firstKey[-4:] == thirdKey[-4:] and secondKey[-4:] == thirdKey[-4:]):
                    if(errors[firstKey] == errors[secondKey] and errors[firstKey] ==errors[thirdKey] and errors[secondKey] == errors[thirdKey]):
                        finalKey = "par_sky_sup_" + firstKey[-4:]
                        if(not any(finalKey[-4:] in search for search in finalKeys)):
                            finalKeys.add(finalKey)
                            finalError[finalKey] = errors[firstKey]
            
                     
    for firstKey in errorKeys:
        for secondKey in errorKeys:
            if(firstKey == secondKey):
                continue
            
            #Check to see if all three of the compilers had similar erros 
            if(firstKey[-4:] == secondKey [-4:]):
                if(errors[firstKey] == errors[secondKey]):
                    if(firstKey < secondKey):
                        finalKey = firstKey[0:3] + "_" + secondKey[0:3] + "_" + firstKey[-4:]
                    else: 
                        finalKey = secondKey[0:3] + "_" + firstKey[0:3] + "_" + firstKey[-4:]
                        
                    if(not any(finalKey[-4:] in search for search in finalKeys)):
                        finalKeys.add(finalKey)
                        finalError[finalKey] = errors[firstKey]
        
    for firstKey in errorKeys:  
        
        if(not any(firstKey[-4:] in search for search in finalKeys)):
            finalKeys.add(firstKey)
            finalError[firstKey] = errors[firstKey]
        
        for search in finalKeys:    
            if(firstKey[-4:] == search[-4:]):
                if(finalError[search] != errors[firstKey]):
                    finalError[firstKey] = errors[firstKey]
'''