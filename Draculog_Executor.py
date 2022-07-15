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

# For Main Draculog Execution
import subprocess
import shutil
import json

# For Controlling the System
from Draculog import GlobalValues as Globe
from Draculog import SharedDraculogFunctions

from Sensors.Sensor import GlobalSensorValues as SensorGlobe

FrankenWeb = SharedDraculogFunctions()

# TimeZone creation for logging
tz = pytz.timezone(Globe.tzStr)

# Sensors
# TODO-Modularity To make Draculog more modular, I need to make this dynamic and not static
from Sensors import Sensor_Time
#, Sensor_PyRAPL

Sensor_Index = 0
Sensors_List = [Sensor_Time.Time()]
#, Sensor_PyRAPL.PyRAPL(organizeMe=False)]

Sensors_Threads = []

# Control Variables
verbose = Globe.verbose
log = Globe.log
executable = Globe.Executable_Str
timeoutSeconds = Globe.timeoutSeconds
control_file = None

# Variables used throughout the program
Downloaded_Code_List = []
Executed_Code_List = []

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
            for line in DLCode:
                if line.replace("\n", "") not in Downloaded_Code_List:
                    Downloaded_Code_List.append(line.replace("\n", ""))
        DLCode.close()
    # If there is no downloaded code file, return none for error control
    else:
        FrankenWeb.Log_Time("FATAL-*-\tNo Downloaded Code List Found", dt.now(tz))
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
            combined_data[sensor[0].name] = sensor[1:][0]
        # If it doesn't need to be organized, continue
        else:
            continue

    return combined_data


# Compiles Given Data into a Single JSON Object
def Compile_Data(user_id, submission_id, sensor_data, start_time, end_time, status):
    combined_sensor_data = Combine_Data(sensor_data)
    result_obj = {
        "userId": user_id,
        "submissionId": submission_id,
        "result": {
            "start_time": start_time,
            "end_time": end_time,
            "delta_time": end_time - start_time,
            "status": ("Completed" if status else "Failed") + " Execution",
            "measurements": combined_sensor_data  # Contains a dictionary like { "Sensor": [measurements], ... }
        }
    }
    for sensor in Sensors_List:
        if not sensor.organizeMe:
            result_obj["result"][sensor.name] = sensor.Get_Data()

    return result_obj


# Adds Str User Path of Executed code to a separate file
def Add_Executed_Path_To_File(UserPath, TimeStamp):
    global Executed_File, Executed_Code_List
    if Executed_File is None:
        Executed_File = open(Globe.Newly_Executed_Code_str, "a+")
    Executed_File.write(UserPath + "_Executed-" + str(TimeStamp) + "\n")
    Executed_Code_List.append(UserPath + "_Executed-" + str(TimeStamp))
    return


def Build_Sensor_Threads():
    global Sensors_Threads, Sensor_Index
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tBuilding all sensors", time.time())
    Sensors_Threads.clear()
    for sensor in Sensors_List:
        # This section is for sensors who don't need to be threaded
        if not sensor.threadMe:
            sensor.Build_Logger()
            Sensors_Threads.append(sensor)
            continue
        t = sensor.Build_Logger(str(Sensor_Index), function=sensor.Log)
        Sensors_Threads.append(t)
    Sensor_Index += 1
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tFinished building all sensors", time.time())
    return


def Start_Sensor_Threads():
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tStarting all sensors", time.time())
    for t in Sensors_Threads:
        if t in Sensors_List:
            t.Start_Logging()
            continue
        t.start()
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tFinished starting all sensors", time.time())
    return


def Wait_For_Sensor_Threads():
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tWaiting for all sensors to finish", time.time())
    for t in Sensors_Threads:
        if t in Sensors_List:
            t.End_Logging()
            continue
        t.join()
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tFinished running all sensors", time.time())
    return


def Gather_Sensor_Data():
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tStarting all sensors", time.time())
    measurements = []
    for sensor in Sensors_List:
        measurements.append([sensor, sensor.Get_Data()])
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tStarting all sensors", time.time())
    return measurements


def Execute_User_Code(status, commands):
    output = None
    start_time = time.time()
    if status:
        # TODO Spin up other thread to wait X time for seg faults
        # TODO-MultiCompiler This is where I would need to know a the needed compiler for their code
        try:
            output = subprocess.run(commands, timeout=timeoutSeconds, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT)
        except subprocess.TimeoutExpired:
            FrankenWeb.Log_Time("ERROR-CODE-*-\tDownloaded code timed out", time.time())
            status = False

        if output is None or output.returncode != 0:
            FrankenWeb.Log_Time("ERROR-CODE-*-\tDownloaded code error-ed out", time.time())
            status = False

    end_time = time.time()
    SensorGlobe.continueLogging = False
    return start_time, end_time, status


# Loops through User Path list (Downloaded Code List) and executes their code
def Measure_User_Code():
    global Sensors_Threads
    for User_Path in Downloaded_Code_List:
        # Clears Sensors_Threads list to prevent memory leak
        Sensors_Threads.clear()

        # Initializes/Sets Control Variables
        SensorGlobe.continueLogging = True
        status = True

        # Check for any updates to the Newly Downloaded Code File, if yes then update the list
        if Check_For_Updates():
            Compile_List_Of_Users()

        # Find the MakeFile and execute it (Build Source Code), else return that the status is false/failed
        if not os.path.isfile(User_Path + "/Makefile"):
            FrankenWeb.Log_Time("ERROR-*-\tNo Makefile found here, skipping - " + User_Path, dt.now(tz), OnlyPrint=True)
            continue
        else:
            # Run the makefile, if it fails save that status (errors in their code)
            built = os.system("cd " + User_Path + "&& make")
            if built != 0:
                status = False

        # Checks to see if we've already run their code
        if os.path.isfile(User_Path + "/Results.json"):
            FrankenWeb.Log_Time("ERROR-*-\tUser's Submission @ " + User_Path + " already contains results, skipping",
                               dt.now(tz), OnlyPrint=True)
            continue
        else:
            Results_File = open(User_Path + "/Results.json", "w+")

        # Overall Directory is 0, User ID is 1, Submission ID is 2
        User_Path_Split = User_Path.split('/')

        # TODO-MultiCompiler This is another thing that would be modified for multi usage
        # Build Command list
        commands = ["./" + User_Path + "/" + executable]

        # Build sensor threads
        Build_Sensor_Threads()

        # Allow sensors to run
        SensorGlobe.continueLogging = True

        # Start Sensor Threads
        Start_Sensor_Threads()

        # Run Downloaded Code
        startTime, endTime, status = Execute_User_Code(status, commands)

        # Wait for all sensors to finish
        Wait_For_Sensor_Threads()

        # Gather all sensor data
        measurements = Gather_Sensor_Data()

        # Compile it all together into one singular JSON
        result_json = Compile_Data(User_Path_Split[1], User_Path_Split[2], measurements, startTime, endTime, status)

        # Save it as a file in user path
        json.dump(result_json, Results_File)
        Results_File.close()

        # Save New User Path
        Add_Executed_Path_To_File(User_Path, round(time.time()))

    return


### Cleaning Up After Execution Functions
# Moves all Files in Old directory (Downloaded_Code/UserId/SubmissionId)
# Into new -> (Downloaded_Code/UserId/SubmissionId_Executed-TIMESTAMP)
def Clean_Up():
    global Executed_Code_List

    # print("=============== Length of ExCodeList is " + str(len(Executed_Code_List)) + " vs Len of DLCode " + str(len(Downloaded_Code_List)))
    # print(Executed_Code_List)
    # print(Downloaded_Code_List)

    # Moves all Files in old directory to new directory
    for index in range(0, len(Executed_Code_List)):
        allFilesInDir = os.listdir(Downloaded_Code_List[index])
        if os.path.isdir(Executed_Code_List[index]):
            shutil.rmtree(Executed_Code_List[index])
        os.mkdir(Executed_Code_List[index])
        for file in allFilesInDir:
            os.rename(Downloaded_Code_List[index] + "/" + file, Executed_Code_List[index] + "/" + file)

        # Delete Old User Path
        shutil.rmtree(Downloaded_Code_List[index])

    # Remove no longer needed file
    os.remove(Globe.Newly_Downloaded_Code_Str)

    return


### Main Execution Build Section
def main():

    # Starting Log Statement
    FrankenWeb.Log_Time("ES##-\tExecution Started", dt.now(tz))

    # Checks to see if we are already downloading, executing, or uploading code
    global control_file
    if os.path.isfile(Globe.Downloading_Code_Str) or os.path.isfile(Globe.Uploading_Code_Str):
        errorStr = "Downloading" if os.path.isfile(Globe.Downloading_Code_Str) else "Uploading"
        print("Wait: Draculog is currently " + errorStr + " code. . . . .")
        os.remove(Globe.Executing_Code_Str)
        sys.exit(2)
    if os.path.isfile(Globe.Executing_Code_Str):
        print("Wait: Draculog is currently still Executing code. . . . .")
        os.remove(Globe.Executing_Code_Str)
        sys.exit(2)

    # Make a control Text File
    control_file = open(Globe.Executing_Code_Str, "w")

    # Do Execution Stuff
    # Find Newly Downloaded Code file (containing all new code to run)
    if not Compile_List_Of_Users():
        os.remove(Globe.Executing_Code_Str)
        sys.exit(1)

    # Measures User Code
    Measure_User_Code()

    # Move all code from old directory into new directory
    Clean_Up()

    # Delete the control Text File
    control_file.close()
    os.remove(Globe.Executing_Code_Str)

    # Ending Log Statement
    FrankenWeb.Log_Time("EF##-\tExecution Finished", dt.now(tz))

    return


# Main Execution
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        FrankenWeb.Log_Time("FATAL-*-\tSome Error Happened, Exiting Executor now", dt.now(tz), Override=True)
        FrankenWeb.Log_Time("FATAL-*-\tError:\n" + str(e), dt.now(tz), Override=True)
        os.remove(Globe.Executing_Code_Str)
        os.remove(Globe.Newly_Executed_Code_str)
        sys.exit(1)

    sys.exit(0)
