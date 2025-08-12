import os, platform, atexit, glob, time, re, subprocess

#helper function for getting the base of a filename
def _getBaseOfFilename(fileName):
    if platform.system() == "Windows":
        baseName = fileName.split('\\')[-1].split('.')[0]
    else:
        baseName = fileName.split('/')[-1].split('.')[0]
    return baseName

# This function builds the list of files that will be run. 
# It includes all the files with extension feb in the provided directory that match the regular expression (if provided).
def _buildFileList(testDir, exp = None, searchStr = None):

    print(testDir)

    # get all the feb files in the directory
    allFiles = glob.glob(testDir + "*.feb")
    allFiles.sort()

    # build the testfile list
    testFiles = []
    for fileName in allFiles:
        
        baseName = _getBaseOfFilename(fileName)

        # skip optimization input files
        if baseName[:2] == "oi":
            continue

        # Skip tests not matching optional exp argument
        if exp:
            skipFile = True
            for ex in exp:
                if re.search(ex, baseName):
                    skipFile = False
                    break
            if skipFile:
                continue

        if searchStr:
            file = open(fileName)
            if file:
                found = False
                for line in file:
                    if re.search(searchStr, line):
                        found = True
                        break
                file.close()
                if not found:
                    continue
            else:
                print(f"ERROR: Failed opening file {fileName}")

        # add it to the pile
        testFiles.append(fileName)

    return testFiles

# helper function for starting a process.
# just pass the command and we'll do the rest!
def _startProcess(command):
    return subprocess.Popen(command, env={"OMP_NUM_THREADS": "1"}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# helper function for running an optimization test file
def _runOptimizationTestFile(febioPath, fileName, optFile, logname, pltname):
    command = [febioPath, '-i', optFile, '-s', fileName, '-o', logname, '-p', pltname]
    return _startProcess(command)

# helper function for running plain vanilla test problem
def _runStandardTestFile(febioPath, fileName, logname, pltname):
    command = [febioPath, '-i', fileName, '-o', logname, '-p', pltname, '-task=test']
#   command = [febioPath, '-i', fileName, '-o', logname, '-p', pltname]
#   command = [febioPath, '-i', fileName, '-task=restart_test']
    return _startProcess(command)

# This function processes the results for a finished test suite problem
# and returns the convergence stats
def _processFileResults(workDir, baseName, returnCode, stdResults):

    # define the results field. This will depend on whether the problem is an optimization problem or not
    results = []

    # Check if test is an optimization problem
    opt = "op" in baseName

    #Optimization input file
    # 0: Normal/Error termination status
    # 1: Final objective value
    # 2: Total iterations
    # 3: Plot file size
    if opt: results = ["", 0.0, 0, 0]

    # Normal input file
    # 0: Normal/Error termination status
    # 1: Number of time steps
    # 2: Number of iterations
    # 3: Number of RHS evaluations
    # 4: Number of reformations
    # 5: Plot file size
    # 6: Data field value
    else: results = ["", 0, 0, 0, 0, 0, ""]

    # check the return value
    if returnCode == 0:
        results[0] = 'Normal'
    else:
        results[0] = 'Error'

    # Define the log and plt files
    logname = workDir + baseName + '.log'
    pltname = workDir + baseName + '.xplt'
    
    # search the log file for the convergence info
    try:
        flog = open(logname, 'r')
        
        if opt:
            for line in flog:
                if line.find("Final objective value") !=-1: results[1] = line.split()[5]
                if line.find("Total iterations"     ) !=-1: results[2] = int(line[43:])
        else:
            # ~ found = 0
            inDataRecord = False
            dataRecordLine = 0
            for line in flog:
                if  line.find("Number of time steps completed"        ) != -1: results[1] = int(line[55:])
                if  line.find("Total number of equilibrium iterations") != -1: results[2] = int(line[55:])
                if  line.find("Total number of right hand evaluations") != -1: results[3] = int(line[55:])
                if  line.find("Total number of stiffness reformations") != -1: results[4] = int(line[55:])
                if  line.find("Time in linear solver") != -1:
                    slv_hr  = int(line[24:25])
                    slv_min = int(line[26:28])
                    slv_sec = int(line[29:31])
                    new_slv_time = slv_hr*3600 + slv_min*60 + slv_sec
                    #print "New solve time", new_slv_time
                if  line.find("elapsed time") != -1:
                    el_hr  = int(line[37:38])
                    el_min = int(line[39:41])
                    el_sec = int(line[42:44])
                    new_el_time = el_hr*3600 + el_min*60 + el_sec

                if line.find("Data Record #1") !=-1: 
                    inDataRecord = True
                    dataRecordLine = 0
                else:
                    if inDataRecord: 
                        dataRecordLine += 1
                        
                        if dataRecordLine == 5:
                            results[6] = line.rstrip("\n").split(" ")[1]
                            
                            inDataRecord = False

        # get the size of the plotfile
        results[5-2*opt] = int(os.path.getsize(pltname))
    except IOError:
        pass
        
        
    # Print convergence info
    # determine which, if any, convergence criteria failed
    fail = [False] * len(results)
    
    try:
        index = 0
        for index in range(1, len(results)):
            if results[index] != stdResults[baseName][index]:
                fail[index] = True
    except:
        pass

    # color codes for printing results:
    # red    = error termination
    # green  = test passed
    # blue   = all criteria passed, except plot file size
    # yellow = some criteria failed
    BLUE   = '\033[96m'
    RED    = '\033[91m'
    GREEN  = '\033[92m'
    WHITE  = '\033[37m'
    YELLOW = '\033[93m'

    # if the test error terminated
    if results[0] != "Normal":
        print(RED + baseName + ": " + str(results) + WHITE)
    # if the test failed convergence criteria
    elif True in fail:                
        resultStrings = str(results).replace("[", "").replace("]", "").split(",")
        
        failFlag = 0
        for index in range(1, len(fail)):
            if fail[index]:
                resultStrings[index] += "(" + str(stdResults[baseName][index]) + ")"
                failFlag = (failFlag | (1 << (index-1)))
                
        msg = '['
        for rStr in resultStrings:
            msg += rStr + ","
            
        msg = msg[:-1] +']'

        if failFlag == (1 << 4):
            print(BLUE + baseName + ": " + msg + WHITE)
        else:
            print(YELLOW + baseName + ": " + msg + WHITE)

    # if the test passed
    else:
        print(GREEN + baseName + ": " + str(results) + WHITE)

    return results

# runs a list of files and returns results
def _runFilesInList(testFiles, febioPath, verifyDir, workDir, numCores, stdResults):

    # Stop subprocesses on death
    def cleanup():
        for proc in running.values():
            proc.kill()

    atexit.register(cleanup)

    # Loop over the tests and run them
    running = {}
    results = {}
    current = 0
    while True:
        while current < len(testFiles) and len(running) < numCores:
            # next customer in line!
            fileName = testFiles[current]
            current += 1

            baseName = _getBaseOfFilename(fileName)

            # Define the log and plt files
            logname = workDir + baseName + '.log'
            pltname = workDir + baseName + '.xplt'
        
            # Test for parameter optimization problems
            if baseName[:2] == "op":
                #Optimization input file
                # 0: Normal/Error termination status
                # 1: Final objective value
                # 2: Total iterations
                # 3: Plot file size
                results[baseName] = ["", 0.0, 0, 0]

                optFile = verifyDir + "oi" + baseName[2:] + ".feb"
                running[baseName] = _runOptimizationTestFile(febioPath, fileName, optFile, logname, pltname)

            else:
                # Normal input file
                # 0: Normal/Error termination status
                # 1: Number of time steps
                # 2: Number of iterations
                # 3: Number of RHS evaluations
                # 4: Number of reformations
                # 5: Plot file size
                # 6: Data field value
                results[baseName] = ["", 0, 0, 0, 0, 0, ""]

                # Run the test problem
                running[baseName] = _runStandardTestFile(febioPath, fileName, logname, pltname)

        # check if any files are running. If not, we're done
        if len(running) == 0:
            break

        # get all the files that have finished
        finished = []
        for baseName in running:
            if running[baseName].poll() != None:
                finished.append(baseName)

        # process the finished files
        # (and remove the files from the running list)
        for baseName in finished:
            results[baseName] = _processFileResults(workDir, baseName, running[baseName].returncode, stdResults)
            del running[baseName]

        # We take a little nap here, to prevent the outer while loop from taking up processor time 
        # when waiting for a processor to free up
        time.sleep(0.01)

    # all done!
    return results

# return the list of problems that crashed or error terminated
def _getErrorTerminations(results):
    err = []
    for key in results:
        if results[key][0] != "Normal":
            err.append(key)
    return err

# return a dictionary of problems that failed the test
def _getFailedTests(results, stdResults):
    failed = {}
    for key in results:
        try:
            # we process error terminations elsewhere
            if results[key][0] != "Normal":
                continue

            fail = [False] * len(results[key])
            for index in range(1, len(results[key])):
                if results[key][index] != stdResults[key][index]:
                    fail[index] = True

            if True in fail:
                failed[key] = fail
        except:
            pass
    return failed

# create a report and write it to a log file. 
def _createTestReport(results, stdResults, elapsedTime, logFilename = None):
    success = True
    subject = ""
    message = ""

    # find tests that error terminated or crashed
    err = _getErrorTerminations(results)
    if len(err) > 0:
        success = False
        
        subject += "Error terminations or crashes"
        
        message += "The following tests error terminated, or crashed:\n"
        for name in err:
            message += "\t" + name + "\n"
        message += "\n"
    
    # Find which tests failed the convergence criteria, and which criteria they failed
    failed = _getFailedTests(results, stdResults)
    if len(failed) > 0:
        success = False
        
        if subject != "":
            subject += ", "
        
        subject += "Bad Convergence Criteria"
        
        message += "The following tests failed due incorrect convergence criteria:\n\n"
        
        for name in failed:
            if name not in stdResults.keys():
                continue
            
            failedMsg = "    " + name + ": "
            
            resultStrings = str(results[name]).replace("[", "").replace("]", "").split(",")
            
            for index in range(1, len(failed[name])):
                if failed[name][index]:
                    resultStrings[index] += "(" + str(stdResults[name][index]) + ")"
            
            if "op" in name:
                failedMsg += "{:^15}|{:^15} | ".format(*resultStrings[1:-1])
                failedMsg += resultStrings[-1]
            else:
                failedMsg += "{:^15}|{:^15}|{:^15}|{:^15}|{:^20} | ".format(*resultStrings[1:-1])
                failedMsg += resultStrings[-1]
                
            
            message += failedMsg + "\n"
        
        message += "\n"
        
    if success:
        subject = "All tests passed"
        message = "All tests in the suite passed.\n"
        
    message += "Test Suite ran in " + elapsedTime + "\n\n"
        
    # Remove crashed tests from results so that they don't get added as new tests
    for name in err:
        del results[name]

    # create the log file
    if logFilename:
        # Create the log directory if it doesn't already exist
        logDir = os.path.abspath(os.path.dirname(logFilename))

        if not os.path.exists(logDir):
            os.makedirs(logDir)

        print("Writing log to %1s" %(logFilename))
        with open(logFilename, "w") as log:
            log.write(subject + "\n")
            log.write(message)
            for key in results:
                log.write(key + " : " + str(results[key]) + "\n")

    return success, subject, message

# This function will run the test suite
def runTests(febioPath, verifyDir, workDir, stdResults, exp=None, searchStr = None, numCores=1, logFilename = None):
    
    # get all the testsuite files
    testFiles = _buildFileList(verifyDir, exp, searchStr)
    print("Running %1d test file(s)" %(len(testFiles)))

    # mark start point
    tic = time.time()

    # run the test suite
    # returns a dictionary with the stats: {basename : [list of stats]}
    results = _runFilesInList(testFiles, febioPath, verifyDir, workDir, numCores, stdResults)

    # Calculate time it took to run suite
    toc = time.time()
    hours, remainder = divmod(int(toc-tic), 3600)
    minutes, seconds = divmod(remainder, 60)
    elapsedTime = '%s:%s:%s' % (hours, minutes, seconds)
    print("Test Suite ran in " + elapsedTime)

    # prepare the report
    success, subject, message = _createTestReport(results, stdResults, elapsedTime, logFilename)
    return success, subject, message, results
