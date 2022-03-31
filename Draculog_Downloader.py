#### DracuLog - Downloader - Downloading Hook for Green Code and DracuLog Integration
### Created by Daniel Jacoby alongside Dr. Joshua Gross, Aaron Helman, and Austin Folser
##
#

# Notes:
# Returned JSON from GreenCode looks as such:
# JSON (Pulled Obj) = {
#   PulledData (0) = {
#       submissionId: int,
#       userId: string,
#       codeName: string like "dummy.cpp",
#       mimetype: string like "cpp" or "c",
#       codeString: string of entire code,
#       codeCompile: int (0 or 1 for compiled or not)
#   }, ...
#   PulledData (N) = { ...
#   }
# }
# Directory to store User code looks like:
# Users_Code/
#   User_ID/
#       Submission_ID/
#           Makefile
#           JSON_Result (If tested)
#           CPP_Code (Saved as userId_submissionId)


# For Basic System Operations
import sys
import os
import shutil

# For Downloading Data
import json
import requests
from datetime import datetime as time

# Control Variables
verbose = True

# API Variables
greenCodeApiToken = ""
greenCodeApiBase = "https://greencodemk2.herokuapp.com/code/"

headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {0}'.format(greenCodeApiToken)}

# Directory Variables
mainCodeDirectory = "Downloaded_Code"

### API Functions
# Calls Green Code with a specific command for the Code route
def Call_GreenCode_API(command):
    apiCall = '{0}{1}'.format(greenCodeApiBase, command)
    response = requests.get(apiCall, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

### Code Set Up Functions
# TODO Create a test where we make a Makefile for a fake user
# Creates an MakeFile for the User's Code
def Create_Makefile(path, codeFile):
    # TODO Add Dynamic Compiler Variable
    compiler = "gcc"
    # TODO Add Dynamic Compiler Flags Variable
    flags = "-o"
    try:
        makefile = open(path + "/" + "Makefile", "w")
        makefile.write("COM=" + compiler + "\n")
        makefile.write("FLAGS=" + flags + "\n")
        makefile.write("all: main\n")
        makefile.write("main: " + codeFile + "\n")
        makefile.write("\t$(COM) $(FLAGS) code " + codeFile + "\n")
        makefile.close()
    except Exception as e:
        print("Makefile Error -- " + e)
        return False
    return True

# TODO Create a test where we just make 2 text files, one with code and without
# Creates an Executable File from the User's Code
def Create_User_Code(path, codeFile, codeString, testing=False):
    # Write the submitted code to the code file, and if it's None run a 60-second baseline measure
    try:
        file = open(path + "/" + codeFile, "w")
        file.write(codeString if codeString is not None else "baseline 60")
        file.close()
    except Exception as e:
        print("User Code Error -- " + e)
        return False
    if testing:
        return True if codeString is not None else False
    return True

# TODO Create a test where we pass it a list of dictionaries, passes if it makes them
# Goes through all pulled users (from un-compiled code) and creates directories with a make file in them
def Setup_UnCompiledCode(PulledJSON):
    # Make Main Directory
    if not os.path.isdir(mainCodeDirectory):
        if verbose:
            print("No main directory found, making one")
        os.mkdir(mainCodeDirectory)

    for submission in PulledJSON:
        # Local Variables
        u = str(submission["userId"])
        s = str(submission["submissionId"])
        m = str(submission["mimetype"])
        codeFile = u + "_" + s + "." + m

        # Checks if the User has a directory and if not, makes one
        userpath = mainCodeDirectory + "/" + u + "_user"
        if not os.path.isdir(userpath):
            if verbose:
                print("Making a directory for user " + u)
            os.mkdir(userpath)

        # Checks if the User already has a submission of this number, and if not makes one
        submissionPath = userpath + "/" + s
        if os.path.isdir(submissionPath):
            if verbose:
                print("Submission already exists, removing previous submission")
            shutil.rmtree(submissionPath)
        if verbose:
            print("Making a new subdirectory for user " + u + "'s submission " + s)
        os.mkdir(submissionPath)

        Create_Makefile(submissionPath, codeFile)
        Create_User_Code(submissionPath, codeFile, submission["codeString"])

    return

### Main Execution Build Section
def main():
    # Make a control Text File
    tempFile = open("Downloading_Code.txt", "w")
    UnCompiledCode = Call_GreenCode_API("notCompiled")
    Setup_UnCompiledCode(UnCompiledCode)
    # Delete the control Text File
    os.remove("Downloading_Code.txt")
    return

# Main Execution
if __name__ == "__main__":
    main()
    sys.exit()
