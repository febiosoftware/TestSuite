#!/usr/bin/env python3

import os, subprocess, sys, glob, platform, re, fnmatch, copy, datetime, multiprocessing
from runTests import *
from acceptChanges import *
from textwrap import TextWrapper

REPOROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFYDIR = os.path.join(REPOROOT, "Verify", "")
LOGDIR = os.path.join(REPOROOT, "Logs")

if platform.system() == "Windows":
    from windowsGoldStandards import *
    GOLDSTANDARDS =os.path.join(REPOROOT, "code", "windowsGoldStandards.py")
elif platform.system() == "Linux":
    from linuxGoldStandards import *
    GOLDSTANDARDS =os.path.join(REPOROOT, "code", "linuxGoldStandards.py")
else:
    from macOSGoldStandards import *
    GOLDSTANDARDS =os.path.join(REPOROOT, "code", "macOSGoldStandards.py")
    
def showHelp():
    wrapper = TextWrapper()
    wrapper.width = os.get_terminal_size()[0]
    wrapper.initial_indent = wrapper.subsequent_indent = "              "
    
    print("tools.py accepts the following flags:\n")
    
    print("-h            Show this help text.")
    
    print("")
    print("-a (logfile)  Accept Changes in logfile")
    print(wrapper.fill("Accepts all changes to convergence criteria as reported in (logfile). "
        "If (logfile) is not provided, defaults to newest file in LOGDIR. "
        "Updates the gold standard results for the current OS and then pushes those changes "
        "to the repository."))

    print("")
    print("-r (febio bin) Run test suite.")
    print(wrapper.fill("Runs the problems in the test stute. Does not update or build anything. "
        "Does not send email. Does not update the gold standards. If (febio bin) is not provided, "
        "it defaults to the value set in the FEBIO_TEST_BIN environment variable"))
    print("")
    print(wrapper.fill("Also accepts optional argument to specify the number of simultaneous tests to run:"))
    print("")
    print("    -c [num]  Runs suite with [num] simultaneous problems.")
    
    print("")
    print("-e [exp] ...  Selects problems matching [exp]")
    print(wrapper.fill("Limits the other functions provided by tools.py to problems that match any "
        "number of regular expressions. For example:"))
    print(wrapper.fill("To limit runs to only biphasic and contact problems: "))
    print(wrapper.fill("    tools.py -r -e bi co"))
    print(wrapper.fill("To only accept changes from a few specific probelms: "))
    print(wrapper.fill("    tools.py -a [logfile] -e dm17 co01 fl36"))

def searchFEBioFiles(searchString):
    print("Searching FEBio files in ", VERIFYDIR)
    files = os.listdir(VERIFYDIR)
    matches = 0
    for filename in files:
        if fnmatch.fnmatch(filename, "*.feb"):
            file = open(os.path.join(VERIFYDIR, filename))
            linenr = 0
            for line in file:
                linenr += 1
                if re.search(searchString, line):
                    print(filename + " (line " + str(linenr) + "):" + line[:-1])
                    matches += 1
    if matches==0:
        print("no matches found")
    else:
        print("%d matches found" %(matches))

# commit new results to git repo
def _commitNewTestResultsToGithub(newResults):

    with open(GOLDSTANDARDS, "w") as ldata:
        ldata.write("stdResults = " + str(newResults).replace("], ", "],\n        ") + "\n\n")

    subprocess.run(["git", "-C", REPOROOT, "stage", GOLDSTANDARDS], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["git", "-C", REPOROOT, "commit", "-m", "Updated " + GOLDSTANDARDS + " with new tests."], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["git", "-C", REPOROOT, "pull", "--no-edit"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["git", "-C", REPOROOT, "push"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# class defining the test report
class TestReport:
    def __init__(self, success, subject, message):
        self.success = success
        self.subject = subject
        self.message = message

# run the test suite and return a TestReport object
def runTestSuite(febioTestBin, numCores, regex, commitNew: bool):
    logFile = os.path.join(LOGDIR, str(datetime.date.today()) + ".txt")
    success, subject, message, results = runTests(febioTestBin, VERIFYDIR, VERIFYDIR, stdResults, exp=regex, numCores=numCores, logFilename=logFile)

    # Check for new tests
    newTests = False
    resultkeys = results.keys()
    stdResultKeys = stdResults.keys()
    for key in resultkeys:
        if key not in stdResultKeys:
            newTests = True
            break

    # Add any new tests to the std file
    if commitNew and newTests:
        if subject != "":
            subject += ", "
            
        subject += "New Tests Added"
            
        message += "The following tests were newly added to the test suite:"
            
        for key in results:
            if key not in stdResults.keys() and results[key][0] == "Normal":
                message += "\t" + key + "\n"
                stdResults[key] = results[key]

        _commitNewTestResultsToGithub(stdResults)

    return TestReport(success, subject, message)

if __name__ == "__main__":
    
    exp = []

    if '-e' in sys.argv:
        index = sys.argv.index('-e')
        
        for i in range(index + 1, len(sys.argv)):
            if sys.argv[i][0] == '-' and len(sys.argv[i]) == 2:
                break
                
            exp.append(sys.argv[i])
        
        if not exp:
            print("Pass in regular expression after '-e'")
    
    
    if '-a' in sys.argv:
        index = sys.argv.index('-a')
        
        if len(sys.argv) > index + 1 and sys.argv[index+1] != "-e":
            acceptChangesLocal(REPOROOT, sys.argv[index+1], exp)
        else:
            print("Accepting changes from latest GitHub actions")
            acceptChangesRemote(REPOROOT, exp)
    
    elif '-r' in sys.argv:
        # find the febio binary
        febioTestBin = None

        index = sys.argv.index('-r')

        if len(sys.argv) > index + 1:
            if not (sys.argv[index + 1 ].startswith('-') and len(sys.argv[index]) == 2):
                febioTestBin = sys.argv[index + 1]
        
        if not febioTestBin:
            febioTestBin = os.environ.get("FEBIO_TEST_BIN")

        if febioTestBin:
            if not os.path.exists(febioTestBin):
                print("Please pass in a valid path to an FEBio binary or set FEBIO_TEST_BIN")
                sys.exit(1)
        else:
            print("Please pass in a valid path to an FEBio binary or set FEBIO_TEST_BIN")
            sys.exit(1)


        defaultCores = multiprocessing.cpu_count()
        NumCores = defaultCores
        
        if '-c' in sys.argv:
            index = sys.argv.index('-c')
            
            coreFail = False
            
            if len(sys.argv) > index:
                try:
                    NumCores = int(sys.argv[index+1])
                except:
                    coreFail = True
                    pass
            else:
                coreFail = True
                
            if NumCores <= 0:
                coreFail = True
            
            if coreFail:
                NumCores = defaultCores
                print("Cannot parse cores number. Defauling to " + str(defaultCores) + " cores.\nPlease pass the number of cores after the '-c' flag as a positive integer.")
        
        results = runTestSuite(febioTestBin, NumCores, exp, True)

        if not results.success:
            exit(1)

    elif '-h' in sys.argv:
        showHelp()
    elif '-s' in sys.argv:
        index = sys.argv.index('-s')
        searchFEBioFiles(sys.argv[index + 1])
    else:
        showHelp()
