import requests, zipfile, io, subprocess, copy, re, os, platform

def _getLogLines(osName):

    token = ""
    try:
        token = os.environ["GH_TOKEN"]
    except:
        print("Please set your GH_TOKEN evnironment variable")
        exit(-1)

    headers = {'User-Agent': 'python-requests/2.18.4', 'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + token}

    response = requests.get("https://api.github.com/repos/febiosoftware/febio/actions/artifacts?per_page=1&name=testsuite-" + osName + "-X64-logs", 
                            headers=headers)

    id = (response.json()["artifacts"][0]["id"])

    zipResponse = requests.get("https://api.github.com/repos/febiosoftware/febio/actions/artifacts/" + str(id) + "/zip", headers=headers)

    zip = zipfile.ZipFile(io.BytesIO(zipResponse.content))

    logName = ""
    for name in zip.namelist():
        if name.startswith("Logs") and name.endswith(".txt"):
            logName = name
            break

    return zip.read(logName).decode().split("\n")

def _pullPush(repoRoot):
    print("Pulling and auto-merging")
    subprocess.run(["git", "-C", repoRoot, "pull", "--no-edit"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Pushing new commit")
    subprocess.run(["git", "-C", repoRoot, "push"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def _commitToRepo(repoRoot, filepath, message):
    print("Committing to repo")
    subprocess.run(["git", "-C", repoRoot, "stage", filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["git", "-C", repoRoot, "commit", "-m", message], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# builds a python file from a log file that contains test results. 
# log (in): the name of the log file
# stdResults (in/out): the original test results are overwritten with the results from the log file
# standardsFile (in): the name of the output file
# exp (in) : regex that sets what log entries to process (or empty for all entries)
def _buildStandardsFileFromLog(log, stdResults, standardsFile, exp) -> bool:
    oldResults = copy.deepcopy(stdResults)
    
    updatedTests = set()

    for line in log:
        if not line.startswith('    '):
            continue
        
        splitLine = line.split(':')
        
        test = splitLine[0].strip()         
        results = splitLine[1].split('|')
        
        # Skip tests not matching optional exp argument
        if exp:
            cont = True
            for ex in exp:
                if re.search(ex, test):
                    cont = False
                    break
            if cont:
                continue

        diff = False        
        for index in range(len(results)):
            # If an incorrect result is recorded, the correct result will
            # be shown in parenthesis next to it
            if '(' in results[index]:
                result = results[index].split('(')[0].strip()

                if "'" in result:
                    result = result.replace("'", '')
                else:
                    result = int(result)

                # Check if the current result is actually different from the standards
                if stdResults[test][index + 1] != result:
                    diff = True
                    stdResults[test][index + 1] = result
                
        # If we find an incorrect result, add the test to the
        # list of updated tests
        if diff:
            updatedTests.add(test)
                    
    with open(standardsFile, "w") as ldata:
        ldata.write("stdResults = " + str(stdResults).replace("], ", "],\n        ") + "\n\n")
        
    if len(updatedTests) == 0:
        print("No results were updated.")

        return False
    else:
        print("The following results were updated:")
        
        sortedList = list(updatedTests)
        sortedList.sort()
        for test in sortedList:
            print(test + ":")
            print("\tOld: " + str(oldResults[test]))
            print("\tNew: " + str(stdResults[test]))
        return True

def _acceptChanges(repoRoot, log, stdResults, standardsFile, exp):

    if _buildStandardsFileFromLog(log, stdResults, standardsFile, exp):
        print("Committing new standard results.")
        _commitToRepo(repoRoot, standardsFile, "Updated " + os.path.basename(standardsFile) + " with new results.")
        return True
    else:
        return False

def acceptChangesRemote(repoRoot, exp = None):
    push = False

    # Windows
    print("Accepting Windows changes")
    osName = "Windows"
    from windowsGoldStandards import stdResults
    standardsFile = os.path.join(repoRoot, "code", "windowsGoldStandards.py")
    
    log = _getLogLines(osName)
    if _acceptChanges(repoRoot, log, stdResults, standardsFile, exp):
        push = True

    # Linux
    print("Accepting Linux changes")
    osName = "Linux"
    from linuxGoldStandards import stdResults
    standardsFile = os.path.join(repoRoot, "code", "linuxGoldStandards.py")
    
    log = _getLogLines(osName)
    if _acceptChanges(repoRoot, log, stdResults, standardsFile, exp):
        push = True
    
    # macOS
    print("Accepting macOS changes")
    osName = "macOS"
    from macOSGoldStandards import stdResults
    standardsFile = os.path.join(repoRoot, "code", "macOSGoldStandards.py")

    log = _getLogLines(osName)
    if _acceptChanges(repoRoot, log, stdResults, standardsFile, exp):
        push = True

    if push:
        _pullPush(repoRoot)
    else:
        print("No new commits. Nothing to push.")


def acceptChangesLocal(repoRoot, logFile, stdResults, standardsFile, exp = None, commitAndPush = True):
    if not os.path.isfile(logFile):
        print(logFile + " does not exist.")
        return
    
    with open(logFile) as log:
        success = _buildStandardsFileFromLog(log, stdResults, standardsFile, exp)
        if commitAndPush:
            if success:
                print("Committing new standard results.")
                _commitToRepo(repoRoot, standardsFile, "Updated " + os.path.basename(standardsFile) + " with new results.")
                _pullPush(repoRoot)
            elif (success == False):
                print("No new commits. Nothing to push.")
