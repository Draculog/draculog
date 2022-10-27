### DracuLog   > Uploaded
## Abstract    - Managing script for Uploading all new code downloaded from downloader
# Created by Daniel Jacoby alongside Dr. Joshua Gross, Aaron Helman, and Austin Folster

"""
Notes:
Directory used to store User code after being executed:
Downloaded_Code/
  Submission_ID_TIMESTAMP(Unix Time, Down to Minute)/
      Makefile
      JSON_Result
      CPP_Code (Saved as userId_submissionId)

TODO Transition to using Power-C like we were before, with a usable header file
Results JSON Looks Like:
JSON (Resultant Obj from execution for each submission) = {
    submissionId: int,
    compiledEnum: int,
    resultsString: string,
    algorithms: [
        {
            algorithmName: string,
            sizeRuns: [
                {
                    size: int,
                    time: float,
                    energy: float,
                    carbon: float
                }, .... (k times for going from size n -> m)
            ]
        }, .... (j times for going from algorithms n -> m)
    ]
}

"""

# For Linux Time Operations
from datetime import datetime as dt
import time
import pytz

# For Basic Linux System Operations
import sys
import os
import shutil

# For Controlling the System
from Draculog import GlobalValues as Globe
from Draculog import SharedDraculogFunctions

FrankenWeb = SharedDraculogFunctions()

# TimeZone creation for logging
tz = pytz.timezone(Globe.tzStr)

# Control Variables
verbose = Globe.verbose
log = Globe.log
control_file = None

# Temporary Control Variable for Upload Problems
testing = True

Executed_Code_List = []
Uploaded_Code_List = []

# List of Executed Code
if not os.path.isfile(Globe.Newly_Uploaded_Code_str):
    Uploaded_File = open(Globe.Newly_Uploaded_Code_str, "w+")
else:
    Uploaded_File = open(Globe.Newly_Uploaded_Code_str, "a+")


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
        thisTime = dt.now(tz)
        FrankenWeb.Log_Time("FATAL-*-\tNo Executed Code List Found", thisTime)
        return False
    return True


# Adds Str User Path of Uploaded code to a separate file
def Add_Executed_Path_To_File(UserPath, TimeStamp):
    global Uploaded_File, Uploaded_Code_List
    if Uploaded_File is None:
        Uploaded_File = open(Globe.Newly_Executed_Code_str, "a+")
    Uploaded_File.write(UserPath + "_Uploaded-" + str(TimeStamp) + "\n")
    Uploaded_Code_List.append(UserPath + "_Uploaded-" + str(TimeStamp))
    return


### Uploading To FrankenWeb Functions
#
def Find_And_Upload():
    for UserPath in Executed_Code_List:
        if not os.path.isfile(UserPath + "/" + Globe.Results_Json_Str):
            FrankenWeb.Log_Time("ERROR-*-\tNo Results file found for Directory " + UserPath, time.time())
            continue

        # if testing:
        #     resultsFile = open(UserPath + "/" + Globe.Results_Json_Str, "r+")
        #     resultsFile.close()
        #     Add_Executed_Path_To_File(UserPath, round(time.time()))
        #     continue
        try:
            FrankenWeb.Upload_To_FrankenWeb(jsonResultFile=(UserPath + "/" + Globe.Results_Json_Str))
        except Exception as e:
            FrankenWeb.Log_Time("FATAL-*-\tUpload Failed for " + UserPath + ", continuing forward", dt.now(tz))
            continue
        Add_Executed_Path_To_File(UserPath, round(time.time()))

        # if FrankenWeb.Upload_To_FrankenWeb(jsonResultFile=UserPath + "/" + Globe.Results_Json_Str):
        #     # Append Userpath if Upload successful
        #     Add_Executed_Path_To_File(UserPath, round(time.time()))

    return

### Cleaning Up After Execution Functions
# Moves all Files in Old directory (Downloaded_Code/UserId/SubmissionId)
# Into new -> (Downloaded_Code/UserId/SubmissionId_Executed-TIMESTAMP)
def Clean_Up():
    global Executed_Code_List

    # Moves all Files in old directory to new directory
    for index in range(0, len(Uploaded_Code_List)):
        allFilesInDir = os.listdir(Executed_Code_List[index])
        if os.path.isdir(Uploaded_Code_List[index]):
            shutil.rmtree(Uploaded_Code_List[index])
        os.mkdir(Uploaded_Code_List[index])
        for file in allFilesInDir:
            os.rename(Executed_Code_List[index] + "/" + file, Uploaded_Code_List[index] + "/" + file)

        # Delete Old User Path
        shutil.rmtree(Executed_Code_List[index])

    # Remove no longer needed file
    os.remove(Globe.Newly_Executed_Code_str)

    return


### Main Execution Build Section
def main():
    # Starting Log Statement
    FrankenWeb.Log_Time("US##-\tUpload Started", dt.now(tz))

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

    # Compile List of all users that executed code
    if not Compile_List_Of_Users():
        sys.exit(1)

    # Loop through all user directories in Downloaded_Code folder
    Find_And_Upload()
    # If Results.json exists, upload it to Green Code
    # Then, move all files from there into a new directory labeled as SubmissionId_Ex-Timestamp_Up-Timestamp
    Clean_Up()

    # Delete the control Text File
    os.remove(Globe.Uploading_Code_Str)

    # Ending Log Statement
    FrankenWeb.Log_Time("UF##-\tUpload Finished", dt.now(tz))


# Main Execution
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        FrankenWeb.Log_Time("FATAL-*-\tSome Error Happened, Exiting Uploader now", dt.now(tz), Override=True)
        FrankenWeb.Log_Time("FATAL-^-\tError:\n" + str(e), dt.now(tz), Override=True)
        FrankenWeb.Log_Time("CONTINUING-^-\tError happened, continuing", dt.now(tz), Override=True)
        os.remove(Globe.Uploading_Code_Str)
        os.remove(Globe.Newly_Uploaded_Code_str)
        sys.exit(1)

    sys.exit(0)
