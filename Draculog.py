#### DracuLog   > Global Value and Function Classes
### Abstract    - Downloading/Uploading Hook for Green Code and DracuLog Integration & Global Variables
## Created by Daniel Jacoby alongside Dr. Joshua Gross, Aaron Helman, and Austin Folster
#
import datetime

import pytz

class GlobalValues:
    # TimeZone String
    tzStr = "America/Los_Angeles"
    # Total Sensor count
    sensor_count = 2

    # Variables used for special execution
    verbose = True
    log = True
    timeoutSeconds = 1000

    # Variables used to control what to log
    Measure_CPU_Temps = False
    Measure_Load_Avgs = False
    Measure_CPU_Energy = False

    # Special Unifying Strings
    Executable_Str = "code"
    Results_Json_Str = "Results.json"

    # String Version of File names (used as control variables)
    User_Code_Directory_Name = "Downloaded_Code"
    Downloading_Code_Str = "Downloading_Code.txt"
    Newly_Downloaded_Code_Str = "Newly_Downloaded_Code.txt"
    Executing_Code_Str = "Executing_Code.txt"
    Newly_Executed_Code_str = "Newly_Executed_Code.txt"
    Uploading_Code_Str = "Uploading_Code.txt"
    Newly_Uploaded_Code_str = "Newly_Uploaded_Code.txt"
    Log_File_Str = "Draculog_Log.txt"

# For the Shared Functions Below
import json
import requests
import os
import sys
import shutil
from datetime import datetime as time

class SharedDraculogFunctions:
    def __init__(self):
        # API Variables
        self.name = "GreenCode and Draculog Integration"
        self.greenCodeApiToken = ""
        self.greenCodeApiBase = "https://greencodemk2.herokuapp.com/code/"
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': 'Bearer {0}'.format(self.greenCodeApiToken)}
        self.downloadToken = "notCompiled"
        self.uploadToken = "uploadResults"
        self.LogFile = None

    def Call_Me(self):
        print("Hi, I'm " + self.name)
        return

    ### API Functions
    # Calls Green Code to download all un-compiled code from Green Code's Website
    def Download_From_GreenCode(self):
        apiCall = '{0}{1}'.format(self.greenCodeApiBase, self.downloadToken)
        response = requests.get(apiCall, headers=self.headers)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            thisTime = time.today()
            if GlobalValues.verbose:
                print("ERROR-*-\tDownloading Code Failed @ " + str(thisTime))
                print("ERROR-^-\tResponse: " + str(response.raise_for_status()))
            if GlobalValues.log:
                self.Log_Time("ERROR-*-\tDownloading Code Failed", thisTime)
                self.Log_Time("ERROR-^-\tResponse: " + str(response.raise_for_status()), thisTime)
            return None

    # Calls Green code to upload a user's JSON result to Green Code's website
    def Upload_To_GreenCode(self, jsonResultFile):
        response = None
        apiCall = '{0}{1}'.format(self.greenCodeApiBase, self.uploadToken)
        jsonObj = json.loads(open(jsonResultFile, 'r+').read())

        try:
            response = requests.post(apiCall, json=jsonObj)
            print(response.text)
        except requests.exceptions.HTTPError as e:
            thisTime = time.now()
            self.Log_Time("FATAL-*-\tUploading Code Failed with HTTP Error Failed for " + jsonResultFile, thisTime)
            self.Log_Time("FATAL-^-\tError is " + str(e), thisTime)
            return False
        if response.status_code == 200:
            thisTime = time.now()
            self.Log_Time("UPDATE-*-\tUploading Code Succeeded for " + jsonResultFile, thisTime)
            return True
        else:
            thisTime = time.now()
            self.Log_Time("FATAL-*-\tUploading Code Failed for " + jsonResultFile, thisTime)
            self.Log_Time("FATAL-^-\tResponse: ", thisTime)
            self.Log_Time(str(response.raise_for_status()), thisTime)
            return False

    ### Logging Functions
    # Takes in an Error string and the time this error happened, then logs it to a log file
    def Log_Time(self, action, timeGiven, OnlyPrint=False, Override=False):
        # TODO-Logging Keep log file under 100 lines in length
        if OnlyPrint and not Override:
            print(action + " @ " + str(timeGiven))
            return
        if GlobalValues.verbose or Override:
            print(action + " @ " + str(timeGiven))
        if GlobalValues.log or Override:
            if os.path.isfile(GlobalValues.Log_File_Str):
                self.LogFile = open(GlobalValues.Log_File_Str, "a+")
            else:
                self.LogFile = open(GlobalValues.Log_File_Str, "w+")
            self.LogFile.write(action + " was done @ " + str(timeGiven) + "\n")
            self.LogFile.close()
            self.LogFile = None
        return

### Functions for Basic Maintenance and Testing
def Remove_Log_File():
    os.remove("Draculog_Log.txt")
    LogFile = open(GlobalValues.Log_File_Str, "w+")
    LogFile.write("==========\tSTART OF DAY " + str(datetime.datetime.now(pytz.timezone(GlobalValues.tzStr))) + "\t==========\n")
    return


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if "Remake_Log_File" in sys.argv:
            Remove_Log_File()

    sys.exit(0)

