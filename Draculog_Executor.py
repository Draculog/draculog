#### DracuLog   > Executor
### Abstract    - Executes all code downloaded by the downloader, saves the results in the submission folder
## Created by Daniel Jacoby alongside Dr. Joshua Gross, Aaron Helman, and Austin Folster
#

"""
Notes:

Directory used to store User code looks like:
Users_Code/
  User_ID/
      Submission_ID/
          Makefile
          JSON_Result (If tested)
          CPP_Code (Saved as userId_submissionId)

Directory used to store User code after being executed:
Users_Code/
  User_ID/
      Submission_ID_TIMESTAMP(Unix Time, Down to Minute)/
          Makefile
          JSON_Result
          CPP_Code (Saved as userId_submissionId)

Results JSON Looks Like:
JSON (Resultant Obj from execution) = {
    id: int,
    submissionId: int,
    result:{
        start time: start time (int, UNIX),
        end time: end time (int, UNIX),
        delta time: end time - start time (int, UNIX),
        measurements: {
            Sensor 1 name: [measurements],
            ...
            Sensor N name: [measurements]
            }
        other sensor measurements (str) (not correlated to time): data (varying, but in this case int)
    }
}
"""

# For Basic System Operations
from datetime import datetime as dt
import time
import sys
import os

# For Main Draculog Execution
import subprocess
import shutil
import json

# For Controlling the System
from Draculog import GlobalValues as Globe
from Draculog import SharedDraculogFunctions
GreenCode = SharedDraculogFunctions()

# Sensors
# TODO-Modularity To make Draculog more modular, I need to make this dynamic and not static
from Sensors import Sensor_Time, Sensor_Temp, Sensor_Load, Sensor_PyRAPL
Sensors_List = [Sensor_Time.Time(), Sensor_Temp.Temperature(),
                Sensor_Load.Load(), Sensor_PyRAPL.PyRAPL(organizeMe=False)]
sensor_count = Globe.sensor_count

# Control Variables
verbose = Globe.verbose
log = Globe.log
control_file = None

# Variables used throughout the program
Downloaded_Code_List = []

# List of Executed Code
if not os.path.isfile(Globe.Newly_Executed_Code_str):
    Executed_File = open(Globe.Newly_Executed_Code_str, "w+")
else:
    Executed_File = open(Globe.Newly_Executed_Code_str, "a+")

### Gathering User's Paths Functions
# Gathers all User's Code paths in Newly Downloaded Code file, and returns it as a list (global list)
def Compile_List_Of_Users():
    global Downloaded_Code_List
    if os.path.isfile(Globe.Newly_Downloaded_Code_Str):
        with open(Globe.Newly_Downloaded_Code_Str, "r") as DLCode:
            line = DLCode.readline()
            if line not in Downloaded_Code_List:
                Downloaded_Code_List.append(line)
        DLCode.close()
    # If there is no downloaded code file, return none for error control
    else:
        thisTime = dt.now()
        if verbose:
            print("ERROR-*-\tNo Downloaded Code List Found @ " + str(thisTime))
        if log:
            GreenCode.Log_Time("ERROR-*-\tNo Downloaded Code List Found", thisTime)
        return False

    return True

# Return True/False if there have been any changes in the Newly Downloaded Code File
def Check_For_Updates():
    temp_Downloaded_Code_List = []
    if os.path.isfile(Globe.Newly_Downloaded_Code_Str):
        with open(Globe.Newly_Downloaded_Code_Str, "r") as DLCode:
            temp_Downloaded_Code_List.append(DLCode.readline())
    return temp_Downloaded_Code_List != Downloaded_Code_List

### Executing User Code Functions
# TODO-Modularity Change this to be more modular, as it will only take static numbers (ie only 4 sensors exist, and we
## only want 3 of them in here
# TODO-Organize Should we fully organize the data into (time, measure_1, measure_2, ..., measure_N) before sending it?
# Combines Sensor Data into easy to read format like
# { Sensor name: [measurements], ... }
def Combine_Data(sensor_data):
    combined_data = {}
    for sensor in sensor_data:
        # Check if the passed in sensor obj needs to be organized
        if sensor[0].organizeMe:
            combined_data[sensor[0].name] = sensor[1:]
        # If it doesn't need to be organized, continue
        else:
            continue

    return combined_data

# Compiles Given Data into a Single JSON Object
def Compile_Data(user_id, submission_id, sensor_data, start_time, end_time):
    combined_sensor_data = Combine_Data(sensor_data)
    result_obj = {
        "user_id": user_id,
        "submission_id": submission_id,
        "result": {
            "start_time": start_time,
            "end_time": end_time,
            "delta_time": end_time - start_time,
            "measurements": combined_sensor_data
        }
    }
    for sensor in Sensors_List:
        if not sensor.organizeMe:
            result_obj["result"][sensor.name] = sensor.Get_Data()

    return result_obj

#
def Add_Executed_User_To_File(UserPath, TimeStamp):
    global Executed_File
    if Executed_File is None:
        Executed_File = open(Globe.Newly_Executed_Code_str, "a+")
    Executed_File.write(UserPath + "_Executed-" + str(TimeStamp) + "\n")
    return

# Loops through User Path list (Downloaded Code List) and executes their code
def Execute_User_Code():
    for User_Path in Downloaded_Code_List:
        # Check for any updates to the Newly Downloaded Code File, if yes then update the list
        if Check_For_Updates():
            Compile_List_Of_Users()

        # Find the MakeFile and execute it (Build Source Code)
        if not os.path.isfile(User_Path + "/Makefile"):
            GreenCode.Log_Time("ERROR-*-\tNo Makefile found here, skipping - " + User_Path, dt.now(), OnlyPrint=True)
            continue
        else:
            os.system("cd " + User_Path + "&& make")

        if os.path.isfile(User_Path + "/Results.json"):
            GreenCode.Log_Time("ERROR-*-\tUser's Submission @ " + User_Path + " already contains results, skipping", dt.now(), OnlyPrint=True)
            continue
        else:
            Results_File = open(User_Path + "/Results.json", "w+")

        # Overall Directory is 0, User ID is 1, Submission ID is 2
        User_Path_Split = User_Path.split('/')
        executable = User_Path_Split[1]+"_"+User_Path_Split[2]

        # Build and Start Loggers
        for s in range(0, sensor_count):
            Sensors_List[s].Build_Logger(Sensors_List[s].Log)
            Sensors_List[s].Start_Logging()

        # TODO-MultiCompiler This is where I would need to know a the needed compiler for their code
        # Execute Their Code
        start_time = time.time()
        output = subprocess.Popen("./" + User_Path + "/" + executable, shell=True)
        output.wait()
        end_time = time.time()

        # End Loggers
        sensor_results = []
        for s in range(0, sensor_count):
            sensor_data = [Sensors_List[s], Sensors_List[s].End_Logging()]
            sensor_results.append(sensor_data)

        # Compile Data into JSON
        result_json = Compile_Data(User_Path_Split[1], User_Path_Split[2], sensor_results, start_time, end_time)

        # Save it as a file in user path
        json.dump(result_json, Results_File)
        Results_File.close()

        # Save New User Path
        Add_Executed_User_To_File(User_Path, round(time.time()))

    return

### Cleaning Up After Execution Functions
# Moves all Files in Old directory (Downloaded_Code/UserId/SubmissionId)
# Into new -> (Downloaded_Code/UserId/SubmissionId_Executed-TIMESTAMP)
def Clean_Up():
    Executed_Code_List = []
    if os.path.isfile(Globe.Newly_Executed_Code_str):
        with open(Globe.Newly_Executed_Code_str, "r") as EXCode:
            line = EXCode.readline()
            if line not in Executed_Code_List:
                Executed_Code_List.append(line)
        EXCode.close()

    # Moves all Files in old directory to new directory
    for index in range(0, len(Downloaded_Code_List)):
        allFilesInDir = os.listdir(Downloaded_Code_List[index].replace("\n", ""))
        for file in allFilesInDir:
            os.rename(Downloaded_Code_List[index] + file, Executed_Code_List[index] + file)

        # Delete Old User Path
        shutil.rmtree(Downloaded_Code_List[index])

    # Remove no longer needed file
    os.remove(Globe.Newly_Downloaded_Code_Str)

    return

### Main Execution Build Section
def main():
    thisTime = dt.now()
    if verbose:
        print("Execution Finished @ " + str(thisTime))
    if log:
        GreenCode.Log_Time("ES##-\tExecution Started", thisTime)

    # Checks to see if we are already downloading, executing, or uploading code
    global control_file
    if os.path.isfile(Globe.Downloading_Code_Str) or os.path.isfile(Globe.Uploading_Code_Str):
        errorStr = "Downloading" if os.path.isfile(Globe.Downloading_Code_Str) else "Uploading"
        print("Wait: Draculog is currently " + errorStr + " code. . . . .")
        sys.exit(2)
    if os.path.isfile(Globe.Executing_Code_Str):
        print("Wait: Draculog is currently still Executing code. . . . .")
        sys.exit(2)

    # Make a control Text File
    control_file = open(Globe.Executing_Code_Str, "w")

    # Do Execution Stuff
    # Find Newly Downloaded Code file (containing all new code to run)
    if not Compile_List_Of_Users():
        sys.exit(1)

    # Executes User Code
    Execute_User_Code()

    # Move all code from old directory into new directory
    Clean_Up()

    # Delete the control Text File
    control_file.close()
    os.remove(Globe.Executing_Code_Str)

    thisTime = dt.now()
    if verbose:
        print("Executing Code Finished @ " + str(thisTime))
    if log:
        GreenCode.Log_Time("EF##-\tExecution Finished", thisTime)

    return

# Main Execution
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        GreenCode.Log_Time("FATAL-*-\tSome Error Happened, Exiting Executor now", dt.now(), Override=True)
        GreenCode.Log_Time("FATAL-*-\tError:\n" + str(e), dt.now(), Override=True)
        os.remove(Globe.Executing_Code_Str)
        os.remove(Globe.Newly_Executed_Code_str)
        sys.exit(1)

    sys.exit(0)