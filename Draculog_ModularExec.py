#### DracuLog   > Executor
### Abstract    - Executes all code downloaded by the downloader, saves the results in the submission folder
## Created by Daniel Jacoby alongside Dr. Joshua Gross, Aaron Helman, and Austin Folster
#

"""
Notes:
# TODO EXIT CODES:
## TODO -- 0 - > Success; 1 -> Compiler Error; 2 -> Runtime Error; 3 -> Not Sorted; 4 -> Timeout Error; 5 -> Draculog Failure

Directory used to store User code looks like:
Downloaded_Code/
  Submission_ID/
      Makefile
      JSON_Result (If tested)
      CPP_Code (Saved as userId_submissionId)

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
from Sensors import Sensor_Dummy, Sensor_PyRAPL

Sensor_Index = 0
# Sensor_List = Globe.Sensor_List
# Sensors_List = [Sensor_Time.Time()]
Sensors_List = {
    # "Time": Sensor_Time.Time(),
    # "Load": Sensor_Load.Load(),
    # "Temp": Sensor_Temp.Temperature(),
    "PyRAPL": Sensor_PyRAPL.PyRAPL()  # Closed for Testing Purposes
    # "Dummy": Sensor_Dummy.Dummy()  # Sensor only used for Dummy data similar to PyRAPL
}

Sensors_Threads = []
execute_module = Draculog_Sort()

# Control Variables
testing = Globe.testing
verbose = Globe.verbose
log = Globe.log
executable = Globe.Executable_Str
timeoutSeconds = Globe.timeoutSeconds
control_file = None

# Headless Execution Variables
header_file_usage = Globe.header_file_usage
minSize = Globe.minSize
maxSize = Globe.maxSize
step = Globe.step
algorithms = Globe.algorithms

# Variables used throughout the program
Downloaded_Code_List = []
Executed_Code_List = []

# List of Executed Code
if not os.path.isfile(Globe.Newly_Executed_Code_str):
    Executed_File = open(Globe.Newly_Executed_Code_str, "w+")
else:
    Executed_File = open(Globe.Newly_Executed_Code_str, "a+")


### Carbon Calculations
# New formula for carbon used: 238g of C02 per kWh
# Formula for Carbon used from electricity is 884.2 lbs of CO2 / 1 MegaWatt Hour
# As per this EPA.gov article: https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references
def Get_Carbon(energyUsed):
    # Input in microjoules
    # Output in grams of CO2
    #
    # Convert microjoules to kilowatt-hour
    # 1 microjoule is one millionth of a watt for one second
    #
    # 1. Divide microjoules by 1,000,000 to get joules (watt-seconds)
    wattSeconds = energyUsed / 1000000
    # 2. Divide joules by 3,600 seconds per hour to get watt-hours
    wattHours = wattSeconds / 3600
    # 3. Divide watt-hours by 1000 to get kilowatt-hours
    kilowattHours = wattHours / 1000
    # 4. Multiply kilowatt-hours by 238 to get grams of CO2
    gramsCO2 = kilowattHours * 238

    return gramsCO2


### Gathering User's Paths Functions
# Gathers all User's Code paths in Newly Downloaded Code file, and returns it as a list (global list)
def Compile_List_Of_Users():
    global Downloaded_Code_List 
    print("Length of Downloaded_Code_List " + str(len(Downloaded_Code_List)))
    if os.path.isfile(Globe.Newly_Downloaded_Code_Str):
        with open(Globe.Newly_Downloaded_Code_Str, "r") as DLCode:
            for line in DLCode:
                if line.replace("\n", "") not in Downloaded_Code_List:
                    Downloaded_Code_List.append(line.replace("\n", ""))
        DLCode.close()
    # If there is no downloaded code file, return none for error control
    else:
        print("Here 3: " + Globe.Newly_Downloaded_Code_Str)
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


"""
Results JSON Looks Like:
JSON (Resultant Obj from execution for each submission) = {
    submissionId: int,
    compiledEnum: int,
    resultsString: string, # STDerr/out case dependant
    algorithms: [ ## output 
        {
            algorithmName: string,
            sizeRuns: [
                {
                    size: int,
                    seconds: float,
                    microjoules: float,
                    gramsco2: float
                }, .... (k times for going from size n -> m)
            ]
        }, .... (j times for going from algorithms n -> m)
    ]
}
"""


def Compile_Headed_Data(submission_id, status, resultsString, output):
    # Compile Results String (String)
    # Compile Enum (Int)

    us = '_'
    if not us in submission_id:
      submission_id = us + submission_id

    result_obj = {
        "submissionId": submission_id.split('_')[1],
        "compiledEnum": status,
        "resultsString": resultsString,
        "algorithms": output
    }
    if testing:
        print(result_obj)
    return result_obj


# Compiles Given Data into a Single JSON Object
def Compile_Headless_Data(submission_id, sensor_data, start_time, end_time, status):
    combined_sensor_data = Combine_Data(sensor_data)

    result_obj = {
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
        temp_sensor = Sensors_List[sensor]
        if not temp_sensor.organizeMe:
            result_obj["result"][temp_sensor.name] = temp_sensor.Get_Data()

    return result_obj

def Compile_To_Json(json_results, User_Path):
    Results_File = open(User_Path + "/" + Globe.Results_Json_Str, "w+")
    json.dump(json_results, Results_File)
    Results_File.close()
    return

# Adds Str User Path of Executed code to a separate file
def Add_Executed_Path_To_File(UserPath, TimeStamp):
    global Executed_File, Executed_Code_List
    if Executed_File is None:
        Executed_File = open(Globe.Newly_Executed_Code_str, "a+")
    Executed_File.write(UserPath + "_Executed-" + str(TimeStamp) + "\n")
    Executed_Code_List.append(UserPath + "_Executed-" + str(TimeStamp))
    return


## TODO only used for non-headed file execution
def Build_Sensor_Threads():
    global Sensors_Threads, Sensor_Index
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tBuilding all sensors", time.time())
    Sensors_Threads.clear()
    for sensor in Sensors_List:
        temp_sensor = Sensors_List[sensor]
        # This section is for sensors who don't need to be threaded
        if not temp_sensor.threadMe:
            temp_sensor.Build_Logger()
            Sensors_Threads.append(temp_sensor)
            continue
        t = temp_sensor.Build_Logger(str(Sensor_Index), function=temp_sensor.Log)
        Sensors_Threads.append(t)
    Sensor_Index += 1
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tFinished building all sensors", time.time())
    return


## TODO only used for non-headed file execution
## TODO Fix sensor list bug, since can't check if a obj is in a dict like this
def Start_Sensor_Threads():
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tStarting all sensors", time.time())
    for t in Sensors_Threads:
        # if t in Sensors_List:
        #     t.Start_Logging()
        #     continue
        t.start()
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tFinished starting all sensors", time.time())
    return


## TODO only used for non-headed file execution
## TODO Fix sensor list bug, since can't check if a obj is in a dict like this
def Wait_For_Sensor_Threads():
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tWaiting for all sensors to finish", time.time())
    for t in Sensors_Threads:
        if t in Sensors_List:
            t.End_Logging()
            continue
        t.join()
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tFinished running all sensors", time.time())
    return


## TODO only used for non-headed file execution
def Gather_Sensor_Data():
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tGathering all sensor data", time.time())
    measurements = []
    for sensor in Sensors_List:
        temp_sensor = Sensors_List[sensor]
        measurements.append([temp_sensor, temp_sensor.Get_Data()])
    FrankenWeb.Log_Time("UPDATE-SENSORS-*-\tStarting all sensors", time.time())
    return measurements


def Execute_User_Code(status, commands):
    output = None
    start_time = time.time()
    if status == 0 or status:
        # TODO Spin up other thread to wait X time for seg faults
        # TODO-MultiCompiler This is where I would need to know a the needed compiler for their code
        try:
            output = subprocess.run(commands, shell=True, timeout=timeoutSeconds, capture_output=True, text=True)
            # , stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) # Old Flags
        except subprocess.TimeoutExpired:
            FrankenWeb.Log_Time("ERROR-CODE-*-\tDownloaded code timed out", time.time())
            status = 4

    if output.returncode != 0:
        FrankenWeb.Log_Time("ERROR-CODE-*-\tDownloaded code error-ed out", time.time())
        status = 2

    end_time = time.time()
    SensorGlobe.continueLogging = False
    return start_time, end_time, status, output


def Measure_Headed_User_Code():
    global Sensors_Threads

    # Loop for Each Submission
    for User_Path in Downloaded_Code_List:
        # Overall Directory is 0, User ID is 1, Submission ID is 2
        User_Path_Split = User_Path.split('/')

        if testing:
            print("Running " + User_Path + "'s Code")
        # Initialize Variables for this Submission
        status = 0
        algorithms_data = []
        # Check for any updates to the Newly Downloaded Code File, if yes then update the list
        if Check_For_Updates():
            Compile_List_Of_Users()

        # Checks to see if we've already run their code
        if os.path.isfile(User_Path + "/Results.json"):
            FrankenWeb.Log_Time(
                "ERROR-*-\tUser's Submission @ " + User_Path + " already contains results, skipping",
                dt.now(tz), OnlyPrint=True)
            status = 5
            continue

        # use the executor to build
        executor_module.buildCode(User_Path
        '''
            Data Obj = {
                algorithmName: "",
                sizeRun: [
                    { # sizeRun_data
                        size: x,
                        delta_time: x,
                        energy: x,
                        carbon: x,
                    },
                    {
                        ...
                    }, ...
                ]
            }
        '''
        resultsString = "Successful Sorting"
        # For Each Submission, Loop for each algorithm in algorithms
        params = executor_module.getParamList()
        for p in params:
            if testing:
                print("Running " + User_Path + "'s Code's with algorithm " + algo)
            algo_data = {
                "algorithmName": Globe.algorithmMap[algo],
                "sizeRun": []
            }
            # For Each Submission of this algorithm, loop from n to m size
            for size in range(minSize, (maxSize + step), step):
                if testing:
                    print("Running " + algo + " at size " + str(size))
                Sensors_Threads.clear()

                # Initialize Sensor Control Variables
                SensorGlobe.continueLogging = True

                # TODO-MultiCompiler This is another thing that would be modified for multi usage
                ## TODO Basically, to make it multi-compiler, change the executable file (the ./ + text)
                ## TODO to be a variable pulled from the user's code, maybe even smth saved in the "Newly_DL'ed" file.
                ## TODO then just pass that into this as the variable. Ie C++ would be ["./", executable, ...]
                ## TODO and python would be ["python3", executable, ...]
                # Build Command list
                commands = "./" + User_Path + "/" + executable + " " + str(size) + " " + algo + " " + str(Globe.verboseCode).lower()

                # Build sensor threads
                # Build_Sensor_Threads()
                for SensorStr in Sensors_List:
                    Sensors_List[SensorStr].Build_Logger()

                # TODO EXIT CODES:
                ## TODO -- 0 - > Success; 1 -> Compiler Error; 2 -> Runtime Error; 3 -> Not Sorted; 4 -> Timeout Error; 5 -> Draculog Failure

                # Allow sensors to run
                SensorGlobe.continueLogging = True

                # Start Sensor Threads
                # Start_Sensor_Threads()
                ## Since we're only measuring Energy, just call Start_Logging
                for SensorStr in Sensors_List:
                    Sensors_List[SensorStr].Start_Logging()

                # Run Downloaded Code
                startTime, endTime, status, output = Execute_User_Code(status, commands)
                if testing:
                    print(output)

                # Finishes Execution of All sensors (PyRAPL)
                # Wait for all sensors to finish
                # Wait_For_Sensor_Threads()
                for SensorStr in Sensors_List:
                    Sensors_List[SensorStr].End_Logging()

                # # Gather all sensor data
                # measurements = Gather_Sensor_Data() # Gets a list of sensors and data points

                # Check for Status errors from execution
                # if output.stdout.split()
                if status != 0:
                    if status == 2:
                        FrankenWeb.Log_Time("ERROR-*-\tExecution Failed - " + User_Path, dt.now(tz),
                                            OnlyPrint=True)
                        resultsString = output.stderr
                        break
                    if status == 4:
                        FrankenWeb.Log_Time("ERROR-*-\tTimeout Error - " + User_Path, dt.now(tz),
                                            OnlyPrint=True)
                        resultsString = "Timeout error, code ran for longer than " + str(timeoutSeconds)
                        break
                outputString = output.stdout.split()
                if outputString[outputString.index("sorted:") + 1] != "true":
                    status = 3
                    FrankenWeb.Log_Time("ERROR-*-\tCode Failed to Sort - " + User_Path, dt.now(tz),
                                        OnlyPrint=True)
                    resultsString = "Numbers failed to sort, please check your algorithm(s)"
                    break

                # Gather all needed Data (Energy and Delta Time)
                sizeRun_data = {
                    "size": size,
                    "seconds": endTime - startTime,
                    "microjoules": Sensors_List["PyRAPL"].Get_Data(),
                    "gramsco2": Get_Carbon(Sensors_List["PyRAPL"].Get_Data())
                }
                if testing:
                    print(sizeRun_data)
                # combined_measurements = Combine_Data(measurements) # Returns a dictionary of those data points organized

                algo_data["sizeRun"].append(sizeRun_data)
            algorithms_data.append(algo_data)

        # # Compile it all together into one singular JSON #TODO fix this function
        # Compile_Headed_Data(result_json, User_Path_Split[2], measurements, startTime,
        #                     endTime, size, algo, status, output)

        json_results = Compile_Headed_Data(User_Path_Split[1], status, resultsString, algorithms_data)
        # Save it as a file in user path
        Compile_To_Json(json_results, User_Path)
        # json.dump(json_results, Results_File)
        # Results_File.close()

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

    FrankenWeb.Log_Time("UPDATE-*-\tCleaning up already run directories now", dt.now(tz))

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
        os.remove("Here1: " + Globe.Executing_Code_Str)
        sys.exit(2)
    if os.path.isfile(Globe.Executing_Code_Str):
        print("Wait: Draculog is currently still Executing code. . . . .")
        print("Here2: " + Globe.Executing_Code_Str)
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
    if header_file_usage:
        Measure_Headed_User_Code()
    else:
        Measure_Headless_User_Code()

    # Move all code from old directory into new directory
    # Clean_Up()

    # Delete the control Text File
    control_file.close()
    os.remove(Globe.Executing_Code_Str)

    # Ending Log Statement
    FrankenWeb.Log_Time("EF##-\tExecution Finished", dt.now(tz))

    return


# Main Execution
if __name__ == "__main__":
    main()
    # try:
    #    main()
    # except Exception as e:
    #    FrankenWeb.Log_Time("FATAL-*-\tSome Error Happened, Exiting Executor now", dt.now(tz), Override=True)
    #    FrankenWeb.Log_Time("FATAL-*-\tError:\n" + str(e), dt.now(tz), Override=True)
    #    os.remove(Globe.Executing_Code_Str)
    #    os.remove(Globe.Newly_Executed_Code_str)
    #    sys.exit(1)

    sys.exit(0)
