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


### Json Setup Functions
# Creates a JSON of all the newly run User code
def Compile_Json():
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
    control_file = open(Globe.Uploading_Code_Str, "w")

    # Do Upload Stuff
    # Compile Results into JSON format (Gather all new JSON files)
    ## To do this, find the file containing all executed code (labeled as SubmissionId_Ex-Timestamp)
    ## Then append that results json file into overall Json object (containing all executed/measured code)
    ## Then, move all files from there into a new directory labeled as SubmissionId_Ex-Timestamp_Up-Timestamp

    newJsonResults = None
    # Upload all new Results into JSON format
    result = GreenCode.Upload_To_GreenCode(newJsonResults)
    if result is not None:
        sys.exit(1)

    # Delete the control Text File
    os.remove(Globe.Uploading_Code_Str)

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
