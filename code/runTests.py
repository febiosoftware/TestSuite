import os, subprocess, sys, glob, datetime, time, shutil, smtplib
from logdata import *

TESTDIR = "/home/sci/mherron/Projects/TestSuite/"
FEBIODIR = "/home/sci/mherron/Projects/FEBio/"
FEBIOSUBPATH = "build/bin/febio3.lnx64"
WORKINGDIR = "/scratch/mherron/FEBioTests/"

# Set up and parse commandline options
update = False
build = False
email = False
runAnyWay = False
numCores = 4

if '-u' in sys.argv:
    update = True
    
if '-b' in sys.argv:
    build = True
    
if '-e' in sys.argv:
    email = True
    from email.message import EmailMessage

if '-r' in sys.argv:
    runAnyWay = True
    
if '-c' in sys.argv:
    index = sys.argv.index('-c')
    
    coreFail = False
    
    if len(sys.argv) > index:
        try:
            numCores = int(sys.argv[index+1])
        except:
            coreFail = True
            pass
    else:
        coreFail = True
        
    if numCores <= 0:
        coreFail = True
    
    if coreFail:
        numCores = 4
        print("Cannot parse cores number. Defauling to 4 cores.\nPlease pass the number of cores after the '-c' flag as a positive integer.")

def sendEmail(success, subject, message, procOut = None, gitInfo = False):
    if email:
        msg = EmailMessage()    

        if success:
            msg['Subject'] = "PASSED - " + subject
        else:
            msg['Subject'] = "FAILED - " + subject
        
        msg['From'] = "mherron@sci.utah.edu"
        msg['To'] = "febio-test@sci.utah.edu"
        
        if gitInfo:
            os.chdir(FEBIODIR)
            gitout = subprocess.run(["git", "log", '--after="1 day ago"'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            gitMessage = "The following commits to the FEBio repository occured in the last 24 hours:\n\n"
            gitMessage += "    " + str(gitout.stdout, "Utf-8").replace("\n", "\n    ") + "\n"
            
            message = gitMessage + message
        
        if procOut:
            message += "\n\nSTDOUT:\n\n" + str(procOut.stdout, "Utf-8") + "\n\nSTDERR:\n\n" + str(procOut.stderr, "Utf-8")
        
        msg.set_content(message)
        
        print("Subject: " + subject)
        print("Message: " + message)

        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()
    
    return True

if update or build:
    needToRun = False
else:
    needToRun = True
    
if runAnyWay:
    needToRun = True

if update:
    # Update FEBio 
    print("Updating FEBio")
    os.chdir(FEBIODIR)

    gitout = subprocess.run(["git", "checkout", "develop"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if gitout.returncode == 0:
        print("Switched to develop branch.")
    else:
        sendEmail(False, "FEBio Update Failed", "Git failed to switch to develop branch.", gitout)
        sys.exit("Failed to switch to develop branch")

    gitout = subprocess.run(["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if gitout.returncode == 0:
        print("Update successful")
    else:
        sendEmail(False, "FEBio Update Failed", "Git failed to update the FEBio repository.", gitout)
        sys.exit("Failed to update FEBio")
        
    if str(gitout.stdout, "Utf-8").strip() != "Already up to date.":
        needToRun = True

    # Check if FEBio is new since last nightly test
    # I may have manually updated and built since the last run, and in this case we want to
    # run the test suite even if the update that just happened does nothing
    if os.path.exists(FEBIODIR + FEBIOSUBPATH):
        if os.path.getmtime(FEBIODIR + FEBIOSUBPATH) > time.time() - 86400:
            needToRun = True

if build:
    # Compile FEBio
    print("Building FEBio")
    os.chdir(FEBIODIR + "build")
    buildout = subprocess.run(["make", "lnx64", "-j16"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # If the first build fails, clean it then try again
    # I don't clean every time because it makes it annoying to test
    if buildout.returncode != 0:
        buildout = subprocess.run(["make", "lnx64clean"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        buildout = subprocess.run(["make", "lnx64", "-j16"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if buildout.returncode == 0:
        print("Build successful")
        
        # Make backup copy
        gitout = subprocess.run(["git", "rev-parse", "--short", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if gitout.returncode == 0:
            backupName = FEBIODIR + FEBIOSUBPATH + "." + str(gitout.stdout, "Utf-8").strip()
            if os.path.exists(backupName):
                print("Backup already exists.")
            else:
                shutil.copy(FEBIODIR + FEBIOSUBPATH, backupName)
                print("Backup Made")
    else:
        sendEmail(False, "FEBio Build Failed", "FEBio failed to build.", gitout, True)
        sys.exit("Failed to build FEBio")

if update:
    # Update Test Suite
    print("Updating Test Suite")
    os.chdir(TESTDIR)
    gitout = subprocess.run(["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if gitout.returncode == 0:
        print("Update successful")
    else:
        sendEmail(False, "Test Suite Update Failed", "Git failed to update the TestSuite repository.", gitout)
        sys.exit("Failed to update Test Suite")
        
    if str(gitout.stdout, "Utf-8").strip() != "Already up to date.":
        needToRun = True

if needToRun:
    # Define the test problems list.
    testFiles = glob.glob(TESTDIR + "Verify3/*.feb")
    testFiles.sort()
    
    # Remove exempt problems from list
    for name in exemptTests:
        try:
            testFiles.remove(TESTDIR + "Verify3/" + name + ".feb")
        except:
            #print("Failed to remove " + name + " from list of test files.")
            pass
    
    # keep counters
    norms = 0                       # nr of normal terminations
    nerrs = 0                       # nr of error terminations

    err = []
    ioErr = []

    results = {}
    running = {}
    current = 0
    # Loop over the tests and run them
    while True:
        while current < len(testFiles) and len(running) < numCores:
            fileName = testFiles[current]
            baseName = fileName.split('/')[-1][:4]
            
            current += 1
            
            # Define the log and plt files
            logname = WORKINGDIR + baseName + '.log'
            pltname = WORKINGDIR + baseName + '.xplt'
        
            opt = False
        
            # Test for parameter optimization problems
            if "op" in baseName:
                opt = True
                optFile = TESTDIR + "Verify3/" + paramOpt[baseName] + ".feb"
                command = [FEBIODIR + FEBIOSUBPATH, '-i', optFile, '-s', fileName, '-o', logname, '-p', pltname]
            # Test for plugin problems
            elif 'pi' in baseName:
                # Skip plugin tests for now
                continue
                # if base == 'pi08' or base == 'pi09':
                    # command = [FEBIODIR + FEBIOSUBPATH, '-i', testFile, '-o', results[baseName].logname, '-p', results[baseName].pltname, \
                        # '-cnf', 'plugins/' + base + '_' + plat + '.xml', \
                        # '-task=angio', 'plugins/angiofe.txt']
                # else:
                    # command = [FEBIODIR + FEBIOSUBPATH, '-i', testFile, '-o', results[baseName].logname, '-p', results[baseName].pltname, \
                        # '-cnf', 'plugins/' + base + '_' + plat + '.xml']
            else:
                command = [FEBIODIR + FEBIOSUBPATH, '-i', fileName, '-o', logname, '-p', pltname]
                
            # Create a variable that will store the results of the test
                
            #Optimization input file
            # 0: Normal/Error termination status
            # 1: Final objective value
            # 2: Total iterations
            # 3: Plot file size
            if opt: results[baseName] = ["", 0.0, 0, 0]

            # Normal input file
            # 0: Normal/Error termination status
            # 1: Number of time steps
            # 2: Number of iterations
            # 3: Number of RHS evaluations
            # 4: Number of reformations
            # 5: Plot file size
            # 6: Data field value
            else: results[baseName] = ["", 0, 0, 0, 0, 0, ""]
            
            
            # Run the test problem
            running[baseName] = subprocess.Popen(command, env={"OMP_NUM_THREADS": "1"}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if len(running) == 0:
            break
                
        finished = []
        for baseName in running:
            if running[baseName].poll() != None:
                finished.append(baseName)
        
        for baseName in finished:
            # Define the log and plt files
            logname = WORKINGDIR + baseName + '.log'
            logstd = WORKINGDIR + baseName + '_std.log'
            pltname = WORKINGDIR + baseName + '.xplt'
            
            # Check if test is an optimization problem
            opt = "op" in baseName
            
            # If this file is in the dataField list
            try:
                df_time = dataField[baseName]
                df_tline = "Time = " + df_time + "\n"
                df_flg = 1
                found = 0
                data1 = 0
                line_num = 0
            # Else
            except:
                df_flg = 0
            
            # check the return value
            if running[baseName].returncode == 0:
                results[baseName][0] = 'Normal'
                norms += + 1
            else:
                err.append(baseName)
                results[baseName][0] = 'Error'
                nerrs += + 1
                
            # search the log file for the convergence info
            try:
                flog = open(logname, 'r')
                
                if opt:
                    for line in flog:
                        if line.find("Final objective value") !=-1: results[baseName][1] = line.split()[5]
                        if line.find("Total iterations"     ) !=-1: results[baseName][2] = int(line[43:])
                else:
                    for line in flog:
                        if  line.find("Number of time steps completed"        ) != -1: results[baseName][1] = int(line[55:])
                        if  line.find("Total number of equilibrium iterations") != -1: results[baseName][2] = int(line[55:])
                        if  line.find("Total number of right hand evaluations") != -1: results[baseName][3] = int(line[55:])
                        if  line.find("Total number of stiffness reformations") != -1: results[baseName][4] = int(line[55:])
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
                        if df_flg:
                            if line.find("Data Record #1") !=-1: data1 = 1
                            if data1: line_num += 1
                            if line.find(df_tline) !=-1 and data1: found = 1
                            if line_num == 6:
                                if found: results[baseName][6] = line.rstrip("\n").split(" ")[1]
                                found = 0
                                line_num = 0
                                data1 = 0

                # get the size of the plotfile and delete it
                results[baseName][5-2*opt] = int(os.path.getsize(pltname))
            except IOError:
                pass
                
            print(baseName + ": " + str(results[baseName]))
            
            del running[baseName]
            
        time.sleep(0.01)

    # Find which tests failed the convergence criteria, and which cirteria they failed
    failed = {}
    for key in results:
        try:
            fail = [False] * len(results[key])
            
            if results[key][0] != "Normal":
                # fail[0] = True
                # failed[key] = fail
                continue
            
            index = 0
            for index in range(1, len(results[key])):
                if results[key][index] != stdResults[key][index]:
                    fail[index] = True
                    
            if True in fail:
                failed[key] = fail
        except:
            pass
    
    success = True
    subject = ""
    message = ""
    
    if len(err) > 0:
        success = False
        
        subject += "Error terminations or crashes"
        
        message += "The following tests error terminated, or crashed:\n"
        for name in err:
            message += "\t" + name + "\n"
        message += "\n"
    
    # if len(ioErr) > 0:
        # success = False
        
        # if subject != "":
            # subject += ", "
        
        # subject += "IO Errors"

        # message += "The following tests failed to read from or write to files:\n"
        # for name in ioErr:
            # message += "\t" + name + "\n"
        # message += "\n"
        
    
    # if len(osErr) > 0:
        # success = False
        
        # if subject != "":
            # subject += ", "
        
        # subject += "OS Errors"
        
        # message += "The following tests failed due to an OSError:\n"
        # for name in osErr:
            # message += "\t" + name + "\n"
        # message += "\n"
    
    failedMsgs = []
    
    if len(failed) > 0:
        success = False
        
        if subject != "":
            subject += ", "
        
        subject += "Bad Convergence Criteria"
        
        message += "The following tests failed due incorrect convergence criteria:\n\n"
        # message += "Format:\n\tFailed Test Name:\n\t\tFailed Criteria:\tcurrent value\tstandard value\n\n"
        
        # optFields = ["Status", "Final objective value", "Total iterations", "Plot file size", "Log diff file size"]
        # fields = ["Status", "Number of time steps", "Number of iterations", "Number of RHS evaluations", "Number of reformations", "Plot file size", "Log diff file size", "Solve time ratio new/old", "Elapsed time ratio new/old", "Data field value"]
        
        
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
            
            
            # message += "\t" + name + ":\n"
            
            # for index in range(1, len(failed[name])):
                # if failed[name][index]:
                    # if len(failed[name]) == 5:
                        # message += "\t\t" + optFields[index] + ":"
                        
                        # for x in range(0, 28 - len(optFields[index])):
                            # message += " "
                    # else:
                        # message += "\t\t" + fields[index] + ":"
                        
                        # for x in range(0, 28 - len(fields[index])):
                            # message += " "
                         
                    # message += str(results[name][index]) + "\t"
                    # message += str(stdResults[name][index]) + "\n"
        
        message += "\n"
        
    if success:
        subject = "All tests passed"
        message = "All tests in the suite passed.\n\n"
        
    # Remove crashed tests from results so that they don't get added as new tests
    for name in err:
        del results[name]
        
    # Add any new tests to the std file
    if len(results) > len(stdResults):
        
        if subject != "":
            subject += ", "
        
        subject += "New Tests Added"
        
        message += "The following tests were newly added to the test suite:"
        
        for key in results:
            if key not in stdResults.keys() and results[key][0] == "Normal":
                message += "\t" + key + "\n"
                
                stdResults[key] = results[key]
    
        with open(TESTDIR + "code/logdata.py", "w") as ldata:
            ldata.write("dataField = " + str(dataField).replace("', ", "',\n        ") + "\n\n")
            ldata.write("exemptTests = " + str(exemptTests) + "\n\n")
            ldata.write("paramOpt = " + str(paramOpt) + "\n\n")
            ldata.write("stdResults = " + str(stdResults).replace("], ", "],\n        ") + "\n\n")
            
    
    with open(TESTDIR + "Logs/" + str(datetime.date.today()) + ".txt", "w") as log:
        log.write(subject)
        log.write(message)
        log.write(str(results).replace("], ", "],\n"))
        
    sendEmail(success, subject, message, gitInfo=True)
else:
    sendEmail(True, "Up to Date", "FEBio, and Test Suite are up to date.\n\nNo need to run.")

















