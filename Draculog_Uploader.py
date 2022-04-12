### DracuLog   > Uploaded
## Abstract    - Managing script for Uploading all new code downloaded from downloader
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
JSON Object to upload looks like
JSON (Resultant Obj) = {
    User [0] = {
        id: int,
        submissionId: int,
        result:{
            length: delta time,
			start time: start time,
			end time: end time,
            energyConsumed: MicroJoules,
            sensor 1:[(time_data,measure_data), (t_data,m_data), ...],
            ...
            sensor N:[(t_data,m_data), ...]
        }
    } , User [1] {
      ...
    } , ...

Directory to store User code looks like:
Users_Code/
  User_ID/
      Submission_ID_TIMESTAMP(Unix Time, Down to Minute)/
          Makefile
          JSON_Result
          CPP_Code (Saved as userId_submissionId)
"""

# For Basic System Operations
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

# Temporary Control Variable for Upload Problems
testing = True

Executed_Code_List = []

### User Path List Setup
#
def Compile_List_Of_Users():
    global Executed_Code_List
    if os.path.isfile(Globe.Newly_Executed_Code_str):
        EXCode = open(Globe.Newly_Executed_Code_str, "r+")
        EXCode_Content = EXCode.read()
        Executed_Code_List = EXCode_Content.split("\n")
        EXCode.close()
        Executed_Code_List.pop()
    else:
        thisTime = dt.now()
        GreenCode.Log_Time("FATAL-*-\tNo Downloaded Code List Found", thisTime)
        return False
    return True

### Uploading To GreenCode Functions
#
def Find_And_Upload():

    if testing:
        fileStr = "Downloaded_Code/115005222949393991754/80_Executed-1649627793/Results.json"
        if GreenCode.Upload_To_GreenCode(fileStr):
            print("SUCCESS")
        else:
            print("FAILURE")

    return

### Main Execution Build Section
def main():
    thisTime = dt.now()
    if verbose:
        print("Uploading Code Started @ " + str(thisTime))
    if log:
        GreenCode.Log_Time("US##-\tUpload Started", thisTime)

    # Checks to see if we are already downloading, executing, or uploading code
    global control_file
    if os.path.isfile(Globe.Downloading_Code_Str) or os.path.isfile(Globe.Executing_Code_Str):
        errorStr = "Executing" if os.path.isfile(Globe.Executing_Code_Str) else "Downloading"
        print("Wait: Draculog is currently " + errorStr + " code. . . . .")
        sys.exit(2)
    if os.path.isfile(Globe.Uploading_Code_Str):
        print("Wait: Draculog is currently still Uploading code. . . . .")
        sys.exit(2)

    # Make a control Text File
    # control_file = open(Globe.Uploading_Code_Str, "w")

    # Do Upload Stuff
    # if not Compile_List_Of_Users():
    #     sys.exit(1)
    # Loop through all user directories in Downloaded_Code folder
    Find_And_Upload()
    # If Results.json exists, upload it to Green Code
    # Then, move all files from there into a new directory labeled as SubmissionId_Ex-Timestamp_Up-Timestamp

    # Delete the control Text File
    # os.remove(Globe.Uploading_Code_Str)

    thisTime = dt.now()
    if verbose:
        print("Uploading Code Finished @ " + str(thisTime))
    if log:
        GreenCode.Log_Time("UF##-\tUpload Finished", thisTime)

    return


# Main Execution
if __name__ == "__main__":
    main()
    sys.exit(0)
