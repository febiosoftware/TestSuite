import requests, zipfile, io, subprocess, copy, re, os, platform

def _getLogLines(osName):

    token = ""
    try:
        token = os.environ["GH_TOKEN"]
    except:
        print("Please set your GH_TOKEN evnironment variable")
        exit(-1)

    headers = {'User-Agent': 'python-requests/2.18.4', 'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + token}

    response = requests.get("https://api.github.com/repos/febiosoftware/febio/actions/artifacts?per_page=1,name=testsuite" + osName + "-X64-logs", 
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


def _acceptChanges(repoRoot, log, stdResults, standardsFile, exp):
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
                
        for index in range(len(results)):
            # If an incorrect result is recorded, the correct result will
            # be shown in parenthesis next to it
            if '(' in results[index]:
                # If we find an incorrect result, add the test to the
                # list of updated tests
                updatedTests.add(test)
                
                result = results[index].split('(')[0].strip()
                
                if "'" in result:
                    stdResults[test][index + 1] = result.replace("'", '')
                else:
                    stdResults[test][index + 1] = int(result)
                    
    with open(standardsFile, "w") as ldata:
        ldata.write("stdResults = " + str(stdResults).replace("], ", "],\n        ") + "\n\n")
        
    if len(updatedTests) == 0:
        print("No results were updated.")
    else:
        print("The following results were updated:")
        
        sortedList = list(updatedTests)
        sortedList.sort()
        for test in sortedList:
            print(test + ":")
            print("\tOld: " + str(oldResults[test]))
            print("\tNew: " + str(stdResults[test]))
            
        # Commit changes 
        print("Committing new standard results.")
        subprocess.run(["git", "-C", repoRoot, "stage", standardsFile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["git", "-C", repoRoot, "commit", "-m", "Updated " + standardsFile + " with new results."], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def acceptChangesRemote(repoRoot, exp = None):
    
    # Windows
    print("Accepting Windows changes")
    osName = "Windows"
    from windowsGoldStandards import stdResults
    standardsFile = os.path.join(repoRoot, "code", "windowsGoldStandards.py")
    
    log = _getLogLines(osName)
    _acceptChanges(repoRoot, log, stdResults, standardsFile, exp)

    # Linux
    print("Accepting Linux changes")
    osName = "Linux"
    from linuxGoldStandards import stdResults
    standardsFile = os.path.join(repoRoot, "code", "linuxGoldStandards.py")
    
    log = _getLogLines(osName)
    _acceptChanges(repoRoot, log, stdResults, standardsFile, exp)
    
    # macOS
    print("Accepting macOS changes")
    osName = "macOS"
    from macOSGoldStandards import stdResults
    standardsFile = os.path.join(repoRoot, "code", "macOSGoldStandards.py")

    log = _getLogLines(osName)
    _acceptChanges(repoRoot, log, stdResults, standardsFile, exp)

    _pullPush(repoRoot)


def acceptChangesLocal(repoRoot, logFile, exp = None):
    if not os.path.isfile(logFile):
        print(logFile + " does not exist.")
        
    if platform.system() == "Windows":
        from windowsGoldStandards import stdResults
        standardsFile =os.path.join(repoRoot, "code", "windowsGoldStandards.py")
    elif platform.system() == "Linux":
        from linuxGoldStandards import stdResults
        standardsFile =os.path.join(repoRoot, "code", "linuxGoldStandards.py")
    else:
        from macOSGoldStandards import stdResults
        standardsFile =os.path.join(repoRoot, "code", "macOSGoldStandards.py")

    with open(logFile) as log:
        _acceptChanges(repoRoot, log, stdResults, standardsFile, exp)

    _pullPush(repoRoot)