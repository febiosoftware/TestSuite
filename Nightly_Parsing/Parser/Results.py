<<<<<<< .mine
'''
Created on Sep 10, 2012

@author: Bryce
'''

class Results():
    '''
    classdocs
    '''
    #member variables
    
    #This holds the name of the files to parse
    _files = []
    
    #This holds the termination results for each test
    _current_Errors = {}
    _current_Output = {}
    _current_Variations = {}
    
    #These hold the values for the standard terminations
    _standard_Output = {} 
    _standard_Errors = {}
    _standard_Missing = {}
    
    _variations = {}
    
    def setFiles(self,files):
        filepath ='../Nightly_Runs/'
        for file in files:
            self._files.append(filepath+file)    =======
'''
Created on Sep 10, 2012

@author: Bryce
'''

class Results():
    '''
    classdocs
    '''
    #member variables
    
    #This holds the name of the files to parse
    _files = []
    
    #This holds the termination results for each test
    _current_Errors = {}
    _current_Output = {}
    _current_Variations = {}
    
    #These hold the values for the standard terminations
    _standard_Output = {} 
    _standard_Errors = {}
    _standard_Missing = {}
    
    _variations = {}
    
    def setFiles(self,files):
        filepath ='../Resources/'
        for file in files:
            self._files.append(filepath+file)    >>>>>>> .r4807
