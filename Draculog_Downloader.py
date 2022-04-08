### DracuLog   > Downloader
## Abstract    - Managing script for all Downloaded Code from Various users and their submissions
# Created by Daniel Jacoby alongside Dr. Joshua Gross, Aaron Helman, and Austin Folster

"""
Notes:
Downloaded JSON from GreenCode looks as such:
JSON (Pulled Obj) = {
  PulledData [0] = {
      submissionId: int,
      userId: string,
      codeName: string like "dummy.cpp",
      mimetype: string like "cpp" or "c",
      codeString: string of entire code,
      codeCompile: int (0 or 1 for compiled or not)
  }, ...
  PulledData [N] = { ...
  }
}

Directory to store User code looks like:
Users_Code/
  UserID/
      SubmissionID/
          Makefile
          CPP_Code (Saved as userId_submissionId)
"""

# String Used for if user's don't have code submitted to GreenCode

# For Linux System Operations
from datetime import datetime as dt
import time
import sys
import os
import shutil

# For Controlling the System
from Draculog import GlobalValues as Globe
from Draculog import SharedDraculogFunctions

GreenCode = SharedDraculogFunctions()

# Control Variables
verbose = Globe.verbose
log = Globe.log
control_file = None

# List of Downloaded Code
if not os.path.isfile(Globe.Newly_Downloaded_Code_Str):
    Downloaded_File = open(Globe.Newly_Downloaded_Code_Str, "w+")
else:
    Downloaded_File = open(Globe.Newly_Downloaded_Code_Str, "a+")

# Directory Variables
mainCodeDirectory = Globe.User_Code_Directory_Name

### Code Set Up Functions
# Creates an MakeFile for the User's Code
def Create_Makefile(path, codeFile, User_Code_Exists):
    # TODO-MultiCompiler This is what needs to be modified so that we can take in more than 1 compiler
    if not User_Code_Exists:
        GreenCode.Log_Time("WARNING-*-\tUser code DNE, skipping Makefile", dt.now())
        return
    # TODO-MultiCompiler Add Dynamic Compiler Variable
    compiler = "gcc"
    # TODO-MultiCompiler Add Dynamic Compiler Flags Variable
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
        GreenCode.Log_Time("ERROR-*-\tMakefile creation error: " + str(e), dt.now(), Override=True)
    return


# Creates an Executable File from the User's Code
def Create_User_Code(path, codeFile, codeString):
    # Write the submitted code to the code file, and if it's None run a 60-second baseline measure
    if codeString is not None:
        file = open(path + "/" + codeFile, "w")
        file.write(codeString)
        file.close()
    # TODO-MultiCompiler This is what needs to be modified so that we can take in more than 1 compiler
    else:
        GreenCode.Log_Time("WARNING-*-\tUser Code Doesn't Exist, Skipping Code Creation", dt.now())
        
    return codeString is not None

#
def Add_User_Code_To_Wait_List(UserPath):
    global Downloaded_File
    if Downloaded_File is None:
        Downloaded_File = open(Globe.Newly_Downloaded_Code_Str, "a+")
    Downloaded_File.write(UserPath + "\n")
    return


# TODO Create a test where we pass it a list of dictionaries, passes if it makes them
# Goes through all pulled users (from un-compiled code) and creates directories with a make file in them
def Setup_UnCompiledCode(PulledJSON):
    # Make Main Directory
    if not os.path.isdir(mainCodeDirectory):
        GreenCode.Log_Time("UPDATE-*-\tNo Main directory Found, Making new one", dt.now(), OnlyPrint=verbose)
        os.mkdir(mainCodeDirectory)

    for submission in PulledJSON:
        # Local Variables
        u = str(submission["userId"])  # User ID
        s = str(submission["submissionId"])  # Submission ID
        m = str(submission["mimetype"])  # Mimetype (cpp/c/py etc)
        codeFile = u + "_" + s + "." + m  # Code File Name

        # Checks if the User has a directory and if not, makes one
        userpath = mainCodeDirectory + "/" + u
        if not os.path.isdir(userpath):
            GreenCode.Log_Time("UPDATE-*-\tNo User directory Found, Making new one", dt.now())
            os.mkdir(userpath)

        # Checks if the User already has a submission of this number, and if not makes one
        submissionPath = userpath + "/" + s
        if os.path.isdir(submissionPath):
            GreenCode.Log_Time("UPDATE-*-\tSubmission already exists, removing previous submission", dt.now())
            shutil.rmtree(submissionPath)
        GreenCode.Log_Time("UPDATE-*-\tMaking a new subdirectory for user "+u+"'s submission "+s, dt.now())

        os.mkdir(submissionPath)

        # TODO-MultiCompiler This is what needs to be modified so that we can take in more than 1 compiler
        User_Code_Exists = Create_User_Code(submissionPath, codeFile, submission["codeString"])
        Create_Makefile(submissionPath, codeFile, User_Code_Exists)

        Add_User_Code_To_Wait_List(submissionPath)

    return


### Main Execution Build Section
def main():
    thisTime = dt.now()
    GreenCode.Log_Time("DS##-\tDownload Starting", thisTime)

    # Checks to see if we are already downloading, executing, or uploading code
    global control_file
    if os.path.isfile(Globe.Executing_Code_Str) or os.path.isfile(Globe.Uploading_Code_Str):
        errorStr = "Executing" if os.path.isfile(Globe.Executing_Code_Str) else "Uploading"
        GreenCode.Log_Time("WAIT-*-\tDraculog is currently " + errorStr + " code. . . . .", dt.now(), Override=True)
        sys.exit(2)
    if os.path.isfile(Globe.Downloading_Code_Str):
        GreenCode.Log_Time("WAIT-*-\tDraculog is currently still Downloading code. . . . .", dt.now(), Override=True)
        sys.exit(2)

    # Make a control Text File
    control_file = open(Globe.Downloading_Code_Str, "w")

    # Download all Un-Compiled (ie Un-Tested) code from GreenCode's Website
    # End Result is a File called "New_Downloaded_Code.txt" that contains all newly downloaded Submissions Paths
    UnCompiledCode = GreenCode.Download_From_GreenCode()
    if UnCompiledCode is None:
        sys.exit(1)
    Setup_UnCompiledCode(UnCompiledCode)

    # Delete the control Text File
    control_file.close()
    os.remove(Globe.Downloading_Code_Str)

    thisTime = dt.now()
    GreenCode.Log_Time("DF##-\tDownload Finished", thisTime)

    return

# Main Execution
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        GreenCode.Log_Time("FATAL-*-\tSome Error Happened, Exiting Downloader now", dt.now(), Override=True)
        GreenCode.Log_Time("FATAL-*-\tError:\n" + str(e), dt.now(), Override=True)
        os.remove(Globe.Executing_Code_Str)
        os.remove(Globe.Newly_Executed_Code_str)
        sys.exit(1)

    sys.exit(0)
