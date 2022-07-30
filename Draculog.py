#### DracuLog   > Global Value and Function Classes
### Abstract    - Downloading/Uploading Hook for Green Code and DracuLog Integration & Global Variables for Draculog
## Created by Daniel Jacoby alongside Dr. Joshua Gross, Aaron Helman, and Austin Folster

import datetime
from email import header
from urllib import request

import pytz

class GlobalValues:
    # TimeZone String
    tzStr = "America/Los_Angeles"
    # Total Sensor count
    sensor_count = 2

    # Variables used for special execution
    testing = True  # Testing Execution
    dummy = True  # Dummy Data creation
    verbose = True
    verboseCode = False  # For whether student code speaks
    log = True
    timeoutSeconds = 1000
    header_file_usage = True

    # Variables used to control what to log
    Measure_CPU_Temps = False
    Measure_Load_Avgs = False
    Measure_CPU_Energy = False

    # Map of Sensors
    Sensor_List = {
        "Time": None,
        "Load": None,
        "Temp": None,
        "PyRapl": None
    }

    # Variables used for headless control
    minSize = 5000
    maxSize = 20000
    step = 5000
    algorithms = ["b", "i", "f", "s"]
    algorithmMap = {
        "b": "Bubble Sort",
        "i": "Insertion Sort",
        "f": "Fast Insertion Sort",
        "s": "Selection Sort",
        "h": "Heap Sort",
        "m": "Merge Sort",
        "q": "Quick Sort"
    }

    # Special Unifying Strings
    Executable_Str = "code"
    Results_Json_Str = "Results.json"
    Header_File_Location = "Headers"
    Main_Header_File_Str = "main.cpp"
    Header_File_Str = "header.h"

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
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os
import sys
import shutil
from datetime import datetime as time

class SharedDraculogFunctions:
    def __init__(self):
        # API Variables
        self.name = "FrankenWeb and Draculog Integration"
        self.FrankenWebApiToken = ""
        self.FrankenWebApiBase = "https://greencodemk2.herokuapp.com/code/"
        self.downloadToken = "notCompiled"
        self.uploadToken = "uploadResults"
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': 'Bearer {0}'.format(self.FrankenWebApiToken),
                        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
                        'Accept': 'text/plain'}
        self.LogFile = None

    def Call_Me(self):
        print("Hi, I'm " + self.name)
        return

    ### API Functions
    # Calls Green Code to download all un-compiled code from Green Code's Website
    def Download_From_FrankenWeb(self):
        apiCall = '{0}{1}'.format(self.FrankenWebApiBase, self.downloadToken)
        response = requests.get(apiCall, headers=self.headers)
        if response.status_code == 200:
            jsonContent = response.content.decode('utf-8')
            response.close()
            return json.loads(jsonContent)
        else:
            thisTime = time.today()
            if GlobalValues.verbose:
                print("ERROR-*-\tDownloading Code Failed @ " + str(thisTime))
                print("ERROR-^-\tResponse: " + str(response.raise_for_status()))
            if GlobalValues.log:
                self.Log_Time("ERROR-*-\tDownloading Code Failed", thisTime)
                self.Log_Time("ERROR-^-\tResponse: " + str(response.raise_for_status()), thisTime)
            response.close()
            return None

    # Calls Green code to upload a user's JSON result to Green Code's website
    def Upload_To_FrankenWeb(self, jsonResultFile):
        response = None
        headers = {'Content-type': 'application/json',
                    'Accept': 'text/plain'}
        apiCall = '{0}{1}'.format(self.FrankenWebApiBase, self.uploadToken)
        jsonObj = json.loads(open(jsonResultFile, 'r+').read())

        try:
            response = requests.post(apiCall, json=jsonObj)
            #print(response.text)
        except requests.exceptions.HTTPError as e:
            thisTime = time.now()
            self.Log_Time("FATAL-*-\tUploading Code Failed with HTTP Error Failed for " + jsonResultFile, thisTime)
            self.Log_Time("FATAL-^-\tError is " + str(e), thisTime)
            response.close()
            return False
        if response.status_code == 200:
            thisTime = time.now()
            self.Log_Time("UPDATE-*-\tUploading Code Succeeded for " + jsonResultFile, thisTime)
            response.close()
            return True
        else:
            thisTime = time.now()
            self.Log_Time("FATAL-*-\tUploading Code Failed for " + jsonResultFile, thisTime)
            self.Log_Time("FATAL-^-\tResponse: ", thisTime)  # Might not be doing what I want
            self.Log_Time(str(response.raise_for_status()), thisTime)  # Might not be doing what I want
            response.close()
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

    # Creates Dummy JSON file from given data
    @staticmethod
    def Create_Dummy_Data():
        f = open('Dummy_Data/Dummy_Data_Download.json')
        data = json.load(f)
        return data


### Functions for Basic Maintenance and Testing
# Removes Old Log File
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

