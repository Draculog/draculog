### Code Initializer for Draculog - Runs when Draculog is started and grabs variables needed for execution
##
#
import sys
import os
import subprocess
import configparser

### NOTE: This is the config file name, change this if you change the config file/location
configFileName = "ReadMe.ini"
### NOTE: This is the default params file name, change this if you change the params file/location
defaultParamsFile = "Source/params.ini"


class Installer:
    def __init__(self, firstTime=False, skipInstall=False):
        if firstTime and not skipInstall:
            print("Doing Fresh Install")
            self.Fresh_Install()
        elif not firstTime and not skipInstall:
            print("Doing Reinstall")
            self.Reinstall()
        return

    # Should only be done for the first execution, could be removed
    @staticmethod
    def Fresh_Install():
        ### NOTE the following only works on Linux based systems, and won't work on Windows in any form
        installation = subprocess.Popen("./install.sh", shell=True)
        installation.wait()

        configure = Config()
        if os.path.isfile("ReadMe.ini"):
            os.remove("ReadMe.ini")
        configure.build_config_file()
        if os.path.isfile("Source/params.ini"):
            os.remove("Source/params.ini")
        configure.build_params_file()

        return

    # Should just reinstall code (IE pull new code from website)
    @staticmethod
    def Reinstall():
        configure = Config()
        if os.path.isfile("ReadMe.ini"):
            os.remove("ReadMe.ini")
        configure.build_config_file()
        if os.path.isfile("Source/params.ini"):
            os.remove("Source/params.ini")
        configure.build_params_file()
        return

    @staticmethod
    def ReCompile(sourceDirectory):
        # Checks if String has a "/" at the end
        if sourceDirectory[:(len(sourceDirectory) - 1)] != '/':
            sourceDirectory += "/"

        # ReCompiles Code
        if not os.path.isdir(sourceDirectory):
            print("ERROR, Given Source Directory is DNE")
            return False

        if not os.path.isfile(sourceDirectory + "Makefile"):
            print("ERROR, source dir Makefile DNE")
            return False

        return True


class Config:

    def __init__(self):
        # Variables to read before execution of script
        self.controlTemp = False
        self.runCpuTempLog = False
        self.runDhtTempLog = False
        self.runEnergyLog = False
        self.useMakerHawk = False
        self.usePyRAPL = False
        self.showTempCycles = False
        self.runLoadLog = False
        self.runClean = False
        self.toCSV = False
        self.toJSON = False

        # Variables to read at execution (intervals only)
        self.cpuInterval = 6
        self.dhtInterval = 6
        self.loadInterval = 6
        self.energyInterval = 6
        self.timeInterval = 6

        # Variable used to maintain temperature (in C)
        self.baselineTemp = 60

        # Grab Code from "/Source/" folder so this should be typed as "/Source/codeToRun" (files only)
        self.configFileName = "ReadMe.ini"
        self.sourceDir = "Source/"
        self.paramsFile = "params.ini"
        self.executable = "file"
        self.csvFile = "raw_data_csv.csv"
        self.jsonFile = "raw_data_json.json"
        self.voltsFile = "file"
        self.ampsFile = "file"

        pass

    @staticmethod
    def build_config_file():
        with open(configFileName, 'w+') as configFile:
            configFile.write("### DracuLog Configuration File\n")
            configFile.write("##\n")
            configFile.write("#\n")
            configFile.write("[Description]\n")
            configFile.write(
                "# In this file contains the base parameters that our script uses to run your code and measure various\n")
            configFile.write(
                "# 'sensors' built into the script and your machine. Using a Pi 4b, a DHT22 sensor attached to the Pi, as well as\n")
            configFile.write(
                "# an energy monitoring device (such as a Makerhawk USB C energy monitor or a Log4 full fat energy monitor), this software\n")
            configFile.write(
                "# can measure how much energy your system used to run a script as well as your temperatures that occured\n")
            configFile.write("# while running your script\n")
            configFile.write("\n")
            configFile.write("[Instructions]\n")
            configFile.write(
                "# If you want to change a parameter, simply copy what was there and replace it with your own variables.\n")
            configFile.write(
                "# Our software looks specifically for the variables named here, so do not change those.\n")
            configFile.write("\n")
            configFile.write("[Parameters]\n")
            configFile.write("# Your source files location, followed by the name of your params file\n")
            configFile.write("SourceDir = Source/sorts/\n")
            configFile.write("ParamsFile = params.ini\n")
            configFile.write("# Whether or not you want to maintain a baseline temperature (in C)\n")
            configFile.write("ControlTemp = False\n")
            configFile.write("BaseLineTemp = 60\n")
            configFile.write("# If you want to monitor your CPU Temps alongside polling time\n")
            configFile.write("CpuTempLog = False\n")
            configFile.write("CpuInterval = 6\n")
            configFile.write("# If you want to monitor your Room Temps (Using a DHT22) alongside polling time\n")
            configFile.write("DhtTempLog = False\n")
            configFile.write("DhtInterval = 6\n")
            configFile.write("# If you want to monitor your Load (1 min Averages) alongside polling time\n")
            configFile.write("LoadLog = False\n")
            configFile.write("LoadInterval = 6\n")
            configFile.write(
                "# If you want to monitor your Energy Usage alongside polling time (Makerhawk is only intergrated into data, Log4 is a sensor)\n")
            configFile.write("EnergyLog = False\n")
            configFile.write("MakerHawk = False\n")
            configFile.write("PyRAPL = False\n")
            configFile.write("EnergyInterval = 6\n")
            configFile.write("ShowTempCycles = False\n")
            configFile.write("# If you want to compile the data into a record(s)\n")
            configFile.write("CleanData = False\n")
            configFile.write("# Choose if you want CSV or JSON (or both) Formating of your data\n")
            configFile.write("ToCSV = False\n")
            configFile.write("CsvFile = raw_data_csv.csv\n")
            configFile.write("ToJSON = False\n")
            configFile.write("JSONFile = raw_data_json.json\n")
        return

    @staticmethod
    def build_params_file():
        with open(defaultParamsFile, 'w+') as params:
            params.write("# This is a sample params file.\n")
            params.write("# '#' signifies a comment, for everything else put it on a single line.\n")
            params.write(
                "# For example, if your source code used a letter and a number to signify the params, put 'b 50000' on one line.\n")
        return

    def Read_Config_File(self):
        configReader = configparser.ConfigParser()
        if not os.path.isfile(configFileName):
            self.build_config_file()
            print("No config file found, creating one now then exiting")
            sys.exit(1)

        configReader.read(configFileName)

        self.sourceDir = configReader.get("Parameters", "SourceDir")
        self.paramsFile = configReader.get("Parameters", "ParamsFile")

        self.controlTemp = configReader.getboolean("Parameters", "ControlTemp")
        self.baselineTemp = configReader.getint("Parameters", "BaseLineTemp")

        self.runCpuTempLog = configReader.getboolean("Parameters", "CpuTempLog")
        self.cpuInterval = configReader.getint("Parameters", "CpuInterval")

        if onPI:
            self.runDhtTempLog = configReader.getboolean("Parameters", "DhtTempLog")
            self.dhtInterval = configReader.getint("Parameters", "DhtInterval")

        self.runLoadLog = configReader.getboolean("Parameters", "LoadLog")
        self.loadInterval = configReader.getint("Parameters", "LoadInterval")

        self.runEnergyLog = configReader.getboolean("Parameters", "EnergyLog")
        self.energyInterval = configReader.getint("Parameters", "EnergyInterval")
        self.useMakerHawk = configReader.getboolean("Parameters", "MakerHawk")
        self.usePyRAPL = configReader.getboolean("Parameters", "PyRAPL")
        self.showTempCycles = configReader.getboolean("Parameters", "EnergyLog")

        self.runClean = configReader.getboolean("Parameters", "CleanData")
        self.toCSV = configReader.getboolean("Parameters", "ToCSV")
        self.csvFile = configReader.get("Parameters", "CsvFile")
        self.toJSON = configReader.getboolean("Parameters", "ToJSON")
        self.jsonFile = configReader.get("Parameters", "JSONFile")
        return

    def Read_User_Configs(self):
        choice = input("Do you want to have a baseline temp? Y/N: ").upper()
        if choice == "Y" or choice == "YES":
            self.controlTemp = True
            self.baselineTemp = int(input("Please enter the baseline temp: "))
        else:
            self.controlTemp = False

        choice = input("Do you want to measure the CPU's temperatures? Y/N: ").upper()
        if choice == "Y" or choice == "YES":
            self.runCpuTempLog = True
            self.cpuInterval = int(input("Please enter the CPU polling interval: "))

        if onPI:
            choice = input("Do you want to measure Room temp (DHT22)? Y/N: ").upper()
            if choice == "Y" or choice == "YES":
                self.runDhtTempLog = True
                self.dhtInterval = int(input("Please enter the DHT polling interval: "))
            else:
                self.runDhtTempLog = False

        choice = input("Do you want to measure Loads? Y/N: ").upper()
        if choice == "Y" or choice == "YES":
            self.runLoadLog = True
            self.loadInterval = int(input("Please enter the Load polling interval: "))
        else:
            self.runLoadLog = False

        choice = input("Do you want to measure Energy? Y/N: ").upper()
        if choice == "Y" or choice == "YES":
            self.runEnergyLog = True
            choice = input("Do you want to use a MakerHawk USB Power Meter or a PyRAPL? M/P: ").upper()
            if choice == "M" or choice == "MAKERHAWK":
                self.useMakerHawk = True
                self.usePyRAPL = False
                self.energyInterval = int(
                    input("Please enter the Energy Polling Interval (in seconds, as poll is 6s / 11poll): "))
            elif choice == "P" or choice == "PYRAPL":
                self.useMakerHawk = False
                self.usePyRAPL = True
            else:
                print("Error, wrong choice was selected, choosing Makerhawk instead")
                self.useMakerHawk = True
                self.usePyRAPL = False
                self.energyInterval = int(
                    input("Please enter the Energy Polling Interval (in seconds, as poll is 6s / 11poll): "))
        else:
            self.runEnergyLog = False

        choice = input("Do you want to get a compiled record? Y/N: ").upper()
        if choice == "Y" or choice == "YES":
            self.runClean = True
            choice = input("Do you want a CSV File, a JSON file, or Both? C/J/B: ").upper()
            if choice == "C" or choice == "CSV" or choice == "B" or choice == "BOTH":
                self.toCSV = True
                self.csvFile = input("Please enter the CSV File name you want: ")
            if choice == "J" or choice == "JSON" or choice == "B" or choice == "BOTH":
                self.toJSON = True
                self.jsonFile = input("Please enter the JSON file name you want: ")
        else:
            self.runClean = False
        return

    def Return_Variables(self, variableDict):

        return


if __name__ == '__main__':
    install = Installer(True)
