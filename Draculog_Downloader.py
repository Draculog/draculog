### DracuLog   > Downloader
## Abstract    - Managing script for all Downloaded Code from Various users and their submissions
# Created by Daniel Jacoby alongside Dr. Joshua Gross, Aaron Helman, and Austin Folster

"""
Notes:
Downloaded JSON from FrankenWeb looks as such:
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

# String Used for if user's don't have code submitted to FrankenWeb

import os
import shutil
# For Linux System Operation
import sys
# For Linux System Time Operations
from datetime import datetime as dt

import pytz

# For Controlling the System
from Draculog import GlobalValues as Globe
from Draculog import SharedDraculogFunctions

# API Connection to FrankenWeb
FrankenWeb = SharedDraculogFunctions()

# TimeZone creation for logging
tz = pytz.timezone(Globe.tzStr)

# Control Variables
testing = Globe.testing
verbose = Globe.verbose
log = Globe.log
control_file = None
header_file_usage = Globe.header_file_usage

# List of Downloaded Code
if not os.path.isfile(Globe.Newly_Downloaded_Code_Str):
    Downloaded_File = open(Globe.Newly_Downloaded_Code_Str, "w+")
else:
    Downloaded_File = open(Globe.Newly_Downloaded_Code_Str, "a+")

# Directory Variables
mainCodeDirectory = Globe.User_Code_Directory_Name
headerFileLocation = Globe.Header_File_Location

### Testing Functions

### Code Set Up Functions
# Creates an MakeFile for the User's Code
def Create_Makefile(path, codeFile):
    # TODO-MultiCompiler This is what needs to be modified so that we can take in more than 1 compiler
    # TODO-MultiCompiler Add Dynamic Compiler Variable
    compiler = "g++"
    # TODO-MultiCompiler Add Dynamic Compiler Flags Variable
    flags = "-std=c++11 -Wno-psabi" if header_file_usage else "-std=c++11 -Wno-psabi -o"

    # Makes a special makefile dependent on if we are using a main header file or not
    if header_file_usage:
        exec_str = "\nmain: deps $(MAIN_HEADER)\n"
        main_str = "\t$(COM) $(FLAGS) $(MAIN_HEADER) $(HEADER) $(STUDENT_CODE) -o " + Globe.Executable_Str + "\n"
    else:
        exec_str = "\nmain:\n"
        main_str = "\t$(COM) $(FLAGS) " + Globe.Executable_Str + " " + codeFile + "\n"

    # - catches error when executing makefile
    try:
        makefile = open(path + "/" + "Makefile", "w")
        makefile.write("COM = " + compiler + "\n")
        makefile.write("FLAGS = " + flags + "\n")
        if header_file_usage:
            makefile.write("MAIN_HEADER = " + Globe.Main_Header_File_Str + "\n")
            makefile.write("HEADER = " + Globe.Header_File_Str + "\n")
            makefile.write("STUDENT_CODE = " + codeFile + "\n")
        makefile.write("\nall: main\n")
        if header_file_usage:
            makefile.write("\ndeps: $(HEADER)\n")
        makefile.write(exec_str)
        makefile.write(main_str)
        makefile.close()
    except Exception as myE:
        FrankenWeb.Log_Time("ERROR-*-\tMakefile creation error: " + str(myE), dt.now(tz), Override=True)

    return


# Copies over Header Files to user directory
def Copy_Header_Files(userPath):
    files = [(headerFileLocation + "/" + Globe.Main_Header_File_Str), (headerFileLocation + "/" + Globe.Header_File_Str)]
    for f in files:
        shutil.copy(f, userPath)
    return


# Creates a File containing the User's Code
def Create_User_Code(path, codeFile, codeString):
    # Write the submitted code to the code file, and if it's None run a 60-second baseline measure
    if codeString is not None:
        file = open(path + "/" + codeFile, "w")
        file.write(codeString)
        file.close()
    else:
        FrankenWeb.Log_Time("WARNING-*-\tSubmission Code Doesn't Exist, Skipping and Deleting Directory", dt.now(tz))

    return codeString is not None


# Adds Str User Path of Downloaded code to a separate file
def Add_Downloaded_Path_To_File(UserPath):
    global Downloaded_File
    if Downloaded_File is None:
        Downloaded_File = open(Globe.Newly_Downloaded_Code_Str, "a+")
    Downloaded_File.write(UserPath + "\n")
    return


# TODO Create a test where we pass it a list of dictionaries, passes if it makes them
# Goes through all pulled users (from un-compiled code) and creates directories with a make file in them
def Setup_UnCompiled_Code(PulledJSON):
    # Make Main Directory
    if not os.path.isdir(mainCodeDirectory):
        FrankenWeb.Log_Time("UPDATE-*-\tNo Main directory Found, Making new one", dt.now(tz), OnlyPrint=verbose)
        os.mkdir(mainCodeDirectory)

    for submission in PulledJSON:
        # Local Variables
        u = str(submission["userId"])  # User ID
        s = str(submission["submissionId"])  # Submission ID
        m = str(submission["mimetype"])  # Mimetype (cpp/c/py etc)

        # User file creation, checks if we need to make a headless or headed file name
        codeFile = (s + "_submitted_sorts." + m) if header_file_usage else (u + "_" + s + "." + m)

        # Checks if the User has a directory and if not, makes one
        userpath = mainCodeDirectory + "/" + u
        if not os.path.isdir(userpath):
            FrankenWeb.Log_Time("UPDATE-*-\tNo User directory Found, Making new one", dt.now(tz))
            os.mkdir(userpath)

        # Checks if the User already has a submission of this number, and if not makes one
        submissionPath = userpath + "/" + s

        ## TODO Check if we've already executed/uploaded this user before
        # if os.path.isdir(submissionPath +

        if os.path.isdir(submissionPath):
            FrankenWeb.Log_Time("UPDATE-*-\tSubmission already exists, removing previous submission", dt.now(tz))
            shutil.rmtree(submissionPath)
        FrankenWeb.Log_Time("UPDATE-*-\tMaking a new subdirectory for user " + u + "'s submission " + s, dt.now(tz))

        os.mkdir(submissionPath)

        # TODO-MultiCompiler This is what needs to be modified so that we can take in more than 1 compiler
        User_Code_Exists = Create_User_Code(submissionPath, codeFile, submission["codeString"])
        if User_Code_Exists:
            Create_Makefile(submissionPath, codeFile)
            if header_file_usage:
                Copy_Header_Files(submissionPath)
            Add_Downloaded_Path_To_File(submissionPath)
        else:
            shutil.rmtree(submissionPath)

    return


### Main Execution Build Section
def main():
    # Starting Log Statement
    FrankenWeb.Log_Time("DS##-\tDownload Starting", dt.now(tz))

    # Checks to see if we are already downloading, executing, or uploading code
    global control_file
    if os.path.isfile(Globe.Executing_Code_Str) or os.path.isfile(Globe.Uploading_Code_Str):
        errorStr = "Executing" if os.path.isfile(Globe.Executing_Code_Str) else "Uploading"
        FrankenWeb.Log_Time("WAIT-*-\tDraculog is currently " + errorStr + " code. . . . .", dt.now(tz), Override=True)
        os.remove(Globe.Downloading_Code_Str)
        sys.exit(2)
    if os.path.isfile(Globe.Downloading_Code_Str):
        FrankenWeb.Log_Time("WAIT-*-\tDraculog is currently still Downloading code. . . . .", dt.now(tz), Override=True)
        os.remove(Globe.Downloading_Code_Str)
        sys.exit(2)

    # Make a control Text File
    control_file = open(Globe.Downloading_Code_Str, "w")

    # Download all Un-Compiled (ie Un-Tested) code from FrankenWeb's Website
    # End Result is a File called "New_Downloaded_Code.txt" that contains all newly downloaded Submissions Paths
    UnCompiledCode = SharedDraculogFunctions.Create_Dummy_Data() if testing else FrankenWeb.Download_From_FrankenWeb()
    if UnCompiledCode is None:
        os.remove(Globe.Downloading_Code_Str)
        sys.exit(1)

    Setup_UnCompiled_Code(UnCompiledCode)

    # Delete the control Text File
    control_file.close()
    os.remove(Globe.Downloading_Code_Str)

    # Ending Log Statement
    FrankenWeb.Log_Time("DF##-\tDownload Finished", dt.now(tz))

    return


# Main Execution
if __name__ == "__main__":
    main()
    # try:
    #     main()
    # except Exception as e:
    #     FrankenWeb.Log_Time("FATAL-*-\tSome Error Happened, Exiting Downloader now", dt.now(tz), Override=True)
    #     FrankenWeb.Log_Time("FATAL-*-\tError:\n" + str(e), dt.now(tz), Override=True)
    #     os.remove(Globe.Downloading_Code_Str)
    #     os.remove(Globe.Newly_Downloaded_Code_Str)
    #     sys.exit(1)

    sys.exit(0)
