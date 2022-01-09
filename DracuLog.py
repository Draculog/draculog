#### DracuLog - The one stop shop of CPU/PI logging software
### Created by Daniel Jacoby alongside Dr. Joshua Gross
##
#

# TODO change interval stuff to be a global variable, not a by case variable (if we want 6 sec intervals for CPU temp and Energy, we also would want that for loads)

# Basic Variable to determine what our script does
import sys

onPI = True
runTest = False
runConfig = False
buildConfig = False
buildParams = False
runBaseline = False
### Pre Execution
##
#
if len(sys.argv) > 1:
	if 'test' in sys.argv or 't' in sys.argv:
		print("You are now using the testing version of the software with preassigned variables")
		runTest = True
	elif 'config' in sys.argv or 'c' in sys.argv:
		print("Using ReadMe.ini file instead of prompts")
		runConfig = True
	elif 'buildConfig' in sys.argv or 'bc' in sys.argv:
		print("Will build config file then exit")
		buildConfig = True
	elif 'buildParam' in sys.argv or 'bp' in sys.argv:
		print("Will build sample params file then exit")
		buildParams = True
	elif 'baseline' in sys.argv or 'b' in sys.argv:
		print("Will only sit idle for x seconds (in config file) to gather baseline data")
		runConfig = True
		runBaseline = True
	elif 'help' in sys.argv or 'h' in sys.argv:
		print("Commands are as follows:\nconfig/c == Use the config.ini file (ReadMe.ini) instead of taking in input at run time\n")
		print("builddConfig/bc == Build a stock config.ini file if you have deleted yours\n")
		print("buildParap/bp == Build a sample param.ini file in your source folder if you don't have one\n")
		sys.exit()
	else:
		print("You've used an unknown flag, ending program")
		sys.exit()

### Imports
##
# Imports for basic system processes
import os # used all over for operations
import time # used to time everything (and to sleep for xInterval)
import subprocess # used for code execution
import threading # used to multi thread the loggers/sensors
import multiprocessing # used to heat up the cpu
import shutil # used in results folder creation/deletion, install
import configparser # install using pip
import re # used to read in params file (stripping whitespace and checking for #
import csv # used for creation of CSV file of raw data (dict to CSV)
import json # used for creation of JSON file of raw data (dict to JSON)
import shutil # used to copy raw csv's elsewhere
import math # used for energy intergration
# Imports for external attachments
import adafruit_dht # for DHT Sensor, install
import gpiod # for DHT Sensor, install
try:
	import board # for DHT Sensor, install
except:
	print("This software is running on a non-PI system, skipping board library import")
	onPI=False
if onPI:
	from gpiozero import CPUTemperature # for CPU Temp, install
else:
	import psutil

import serial # install for something, can't remember atm
import pyRAPL # for the energy measurement of the CPU
import datetime # for date processing for pyRAPL

### Global Variables
##
# Basic Global Variables
baselineTemp = 60

data_list = [] # to store all data in 2D Dictonary structured as such ->
# data_list = [
#			{	'run_number':"run x",
#				'parameters':"parameters",
#				'executable':"executable file name",
#				'length':"delta time",
#				'start time':"start time",
#				'end time':"end time",
#				'other deltas':"other deltas",
#				'other start times':"other start times",
#				'other end times':"other end times",
#				...,
#				'sensor_1':[(time_data,measure_data),(t_data,m_data),...],
#				'sensor_2':[(t_data,m_data),(t_data,m_data),...],
#				...
#			},
#			{	'run_2':"parameters_2",
#					'...':[...],
#					'...':[...], ...
#			}, ...
#		]
energy_list = []
params_list = []

# Variables to read before execution
controlTemp = False
runCpuTempLog = False
runDhtTempLog = False
runEnergyLog = False
useMakerHawk = False
usePyRAPL = False
showTempCycles = False
runLoadLog = False
runClean = False
toCSV = False
toJSON = False

# Variables to read at execution
cpuInterval = 6
dhtInterval = 6
loadInterval = 6
energyInterval = 6
timeInterval = 6

# Grab Code from "/Source/" folder so this should be typed as "/Source/codeToRun"
configFileName = "ReadMe.ini"
sourceDir = "Source/"
paramsFile = "params.ini"
executable = "file"
csvFile = "raw_data_csv.csv"
jsonFile = "raw_data_json.json"
voltsFile = "file"
ampsFile = "file"

### Classes
##
#

class Manager:
# Start Manager
	run_number = 0

	def __init__(self):
		self.loggers = {}

	def build_config_file(self):
		with open(configFileName, 'w+') as configFile:
			configFile.write("### DracuLog Configutation File\n")
			configFile.write("##\n")
			configFile.write("#\n")
			configFile.write("[Description]\n")
			configFile.write("# In this file contains the base parameters that our script uses to run your code and measure various\n")
			configFile.write("# 'sensors' built into the script and your machine. Using a Pi 4b, a DHT22 sensor attached to the Pi, as well as\n")
			configFile.write("# an energy monitoring device (such as a Makerhawk USB C energy monitor or a Log4 full fat energy monitor), this software\n")
			configFile.write("# can measure how much energy your system used to run a script as well as your temperatures that occured\n")
			configFile.write("# while running your script\n")
			configFile.write("\n")
			configFile.write("[Instructions]\n")
			configFile.write("# If you want to change a parameter, simply copy what was there and replace it with your own variables.\n")
			configFile.write("# Our software looks specifically for the variables named here, so do not change those.\n")
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
			configFile.write("# If you want to monitor your Energy Usage alongside polling time (Makerhawk is only intergrated into data, Log4 is a sensor)\n")
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

	def build_params_file(self):
		with open("Source/params.ini", 'w+') as params:
			params.write("# This is a sample params file.\n")
			params.write("# '#' signifies a comment, for everything else put it on a single line.\n")
			params.write("# For example, if your source code used a letter and a number to signify the params, put 'b 50000' on one line.\n")
		return

	def read_configs(self):
		# TODO make it so that if you delete or move the config file, we create a new one with NONE/False
		global sourceDir,paramsFile,csvFile,jsonFile,toCSV,toJSON,controlTemp,baselineTemp,runCpuTempLog,cpuInterval,runDhtTempLog
		global dhtInterval,runLoadLog,loadInterval,runEnergyLog,energyInterval,useMakerHawk,usePyRAPL,runClean

		if runConfig:
			configReader = configparser.ConfigParser()
			if not os.path.isfile(configFileName):
				self.build_config_file()
				print("No config file found, creating one now then exiting")
				sys.exit(1)

			configReader.read(configFileName)
			sourceDir = configReader.get("Parameters", "SourceDir")
			paramsFile = configReader.get("Parameters", "ParamsFile")

			controlTemp = configReader.getboolean("Parameters", "ControlTemp")
			baselineTemp = configReader.getint("Parameters", "BaseLineTemp")

			runCpuTempLog = configReader.getboolean("Parameters", "CpuTempLog")
			cpuInterval = configReader.getint("Parameters", "CpuInterval")

			runDhtTempLog = configReader.getboolean("Parameters", "DhtTempLog")
			dhtInterval = configReader.getint("Parameters", "DhtInterval")

			runLoadLog = configReader.getboolean("Parameters", "LoadLog")
			loadInterval = configReader.getint("Parameters", "LoadInterval")

			runEnergyLog = configReader.getboolean("Parameters", "EnergyLog")
			energyInterval = configReader.getint("Parameters", "EnergyInterval")
			useMakerHawk = configReader.getboolean("Parameters", "MakerHawk")
			usePyRAPL = configReader.getboolean("Parameters", "PyRAPL")
			showTempCycles = configReader.getboolean("Parameters", "EnergyLog")

			runClean = configReader.getboolean("Parameters", "CleanData")
			toCSV = configReader.getboolean("Parameters", "ToCSV")
			csvFile = configReader.get("Parameters", "CsvFile")
			toJSON = configReader.getboolean("Parameters", "ToJSON")
			jsonFile = configReader.get("Parameters", "JSONFile")
		else:
			choice = input("Do you want to have a baseline temp? Y/N: ").upper()
			if choice == "Y" or choice == "YES":
				controlTemp = True
				baselineTemp = int(input("Please enter the baseline temp: "))
			else:
				controlTemp = False

			choice = input("Do you want to measure the CPU's temperatures? Y/N: ").upper()
			if choice == "Y" or choice == "YES":
				runCpuTempLog = True
				cpuInterval = int(input("Please enter the CPU polling interval: "))

			choice = input("Do you want to measure Room temp (DHT22)? Y/N: ").upper()
			if choice == "Y" or choice == "YES":
				runDhtTempLog = True
				dhtInterval = int(input("Please enter the DHT polling interval: "))
			else:
				runDhtTempLog = False

			choice = input("Do you want to measure Loads? Y/N: ").upper()
			if choice == "Y" or choice == "YES":
				runLoadLog = True
				loadInterval = int(input("Please enter the Load polling interval: "))
			else:
				runLoadLog = False

			choice = input("Do you want to measure Energy? Y/N: ").upper()
			if choice == "Y" or choice == "YES":
				runEnergyLog = True
				choice = input("Do you want to use a MakerHawk USB Power Meter or a PyRAPL? M/P: ").upper()
				if choice == "M" or choice == "MAKERHAWK":
					useMakerHawk = True
					usePyRAPL = False
					energyInterval = int(input("Please enter the Energy Polling Interval (in seconds, as poll is 6s / 11poll): "))
				elif choice == "P" or choice == "PYRAPL":
					useMakerHawk = False
					usePyRAPL = True
				else:
					print("Error, wrong choice was selected, choosing Makerhawk instead")
					useMakerHawk = True
					usePyRAPL = False
					energyInterval = int(input("Please enter the Energy Polling Interval (in seconds, as poll is 6s / 11poll): "))
			else:
				runEnergyLog = False

			choice = input("Do you want to get a compiled record? Y/N: ").upper()
			if choice == "Y" or choice == "YES":
				runClean = True
				choice = input("Do you want a CSV File, a JSON file, or Both? C/J/B: ").upper()
				if choice == "C" or choice == "CSV" or choice == "B" or choice == "BOTH":
					toCSV = True
					csvFile = input("Please enter the CSV File name you want: ")
				if choice == "J" or choice == "JSON" or choice == "B" or choice == "BOTH":
					toJSON = True
					jsonFile = input("Please enter the JSON file name you want: ")
			else:
				runClean = False
		return
	def read_params(self):
		global params_list, paramsFile
		if not runConfig:
			paramsFile = input("Please enter the name of your params file: ")
		else:
			print("Grabbing Paramaters from given file, located at " + sourceDir+paramsFile)

		openParamsFile = open(sourceDir+paramsFile)
		lines = openParamsFile.readlines()
		for var in lines:
			if var.strip():
				v = var.strip()
				if v[0] != '#':
					params_list.append(var.rstrip())
		return

	def build_source_code(self): #TODO retool so I can systematically build executable files with certain params
		global sourceDir,executable,paramsFile
		#check if we are going to use java vs c++

		if not runConfig:
			# grab source files from user prompt
			sourceDir = input("Folder name (Source/foldername/): ")
		else:
			# grab source files from config.ini
			print("Grabbed Source Code, building code located at: " + sourceDir)

		if not os.path.isdir(sourceDir):
			print("ERROR, source dir DNE")
			sys.exit(1)

		if not os.path.isfile(sourceDir + "Makefile"):
			print("ERROR, source dir Makefile DNE")
			sys.exit(1)

		print("Compiling Source Files using given Makefile")
		os.system("cd " + sourceDir + "&& make")

		for filename in os.listdir(sourceDir):
			if os.path.isfile(sourceDir+filename) and os.access(sourceDir+filename, os.X_OK):
				executable = filename
		return

	def run_baseline(self):
		param="Baseline"
		# run_number=0
		results_file_string="ResultsBaseline"

		try:
			configReader.read(configFileName)
			bec = configReader.get("Parameters", "BaselineExecutionTime")
		except:
			bec = 60
		if bec is None:
			bec = 60

		if runEnergyLog and useMakerHawk and not runTest and not usePyRAPL:
			print("Please get your MakerHawk software ready, as there will be a 15 second count down once you hit enter below")
			print("This is needed to align your Amp's CSV data from your Makerhawk with your other sensor data")
			print("So make sure you clear the AMPS data/sensor/log in the Makerhawk software first please!")
			confirm = input("Hit Enter, then a 15 second countdown will start.....")
			self.count_down(15)

		if runLoadLog:
			print("Clearing Load Min Average by Sleeping for 60 seconds")
			time.sleep(60)

		global continueLogging
		continueLogging = True

		self.rebuild_loggers(self.run_number)
		if runDhtTempLog:
			self.loggers['dht'].dht_data_set.clear()

		for key in self.loggers:
			if key != "dht" and key != "pyrapl":
				print("Starting logger for " + key)
				self.loggers[key].start_logging()
			if key == "dht":
				print("Polling DHT")
				self.loggers['dht'].poll_dht22()
			if key == "pyrapl":
				print("Building Meter for this run")
				self.loggers['pyrapl'].create_meter(param)
		if controlTemp:
			self.warm_up()

		### Script Execution Start
		if usePyRAPL:
			self.loggers['pyrapl'].meter.begin()

		self.startTime =  time.time()

		### Actual Script Execution
		time.sleep(bec)
		### End of Actual Script Execution

		self.endTime = time.time()

		if usePyRAPL:
			self.loggers['pyrapl'].meter.end()
		### Script Execution End

		if runDhtTempLog:
			print("Polling DHT")
			self.loggers['dht'].poll_dht22()

		continueLogging = False
		self.elapsedTime = self.endTime - self.startTime
		print("Elapsed time is " + str(self.elapsedTime))

		if controlTemp:
			self.cool_down()

		if runDhtTempLog:
			print("Polling DHT")
			self.loggers['dht'].poll_dht22()

		self.compile_data(param, self.run_number, results_file_string)

		print("Done with gathering baseline data, taking a 10 second break")
		time.sleep(10)
		self.run_number+=1
		return

	def build_loggers(self):
		timeLog = TimeLog(timeInterval)
		timeLog.build_logger()
		self.loggers['time'] = timeLog

		if runCpuTempLog:
			cpu = CpuLog(cpuInterval)
			cpu.build_logger()
			self.loggers['cpu'] = cpu
		if runLoadLog:
			load = LoadLog(loadInterval)
			load.build_logger()
			self.loggers['load'] = load
		if runDhtTempLog:
			dht = DhtLog()
			self.loggers['dht'] = dht
		if runEnergyLog:
			if usePyRAPL:
				pyrapl = PyRAPLLog()
				pyrapl.build_logger()
				self.loggers['pyrapl'] = pyrapl
		return

	def count_down(self, timelimit):
		print("Starting count down (click reset logs when count down ends)")
		i = timelimit
		while i >= 0:
			print("Starting in " + str(i))
			i-=1
			time.sleep(1)
		return

	def rebuild_loggers(self, runNumber):
		print("Rebuilding Threads")
		for key in self.loggers:
			if key != "dht" and key != "pyrapl":
				self.loggers[key].rebuild_logger(runNumber)
		return

	def run_loggers(self):
		print("Running Tests with all params using given source code")
		# run_number = 0

		if runEnergyLog and useMakerHawk and not runTest and not usePyRAPL:
			print("Please get your MakerHawk software ready, as there will be a 10 second count down once you hit enter below")
			print("This is needed to align your Amp's CSV data from your Makerhawk with your other sensor data")
			print("So make sure you clear the AMPS data/sensor/log in the Makerhawk software first please!")
			confirm = input("Hit Enter, then a 15 second countdown will start.....")
			self.count_down(15)

		for param in params_list:

			if param.lower() == "baseline":
				print("Running Baseline")
				self.run_baseline()
				continue

			if runLoadLog:
				print("Clearing Load Min Average by Sleeping for 60 seconds")
				time.sleep(60)


			global continueLogging
			continueLogging = True
			print("Starting Tests and Logging using -> " + param)

			# Change this for other languages
			command = "./"+sourceDir+executable+" "+param

			results_file_string = sourceDir+param+"_results.txt"
			results_file = open(results_file_string, 'w')

			if self.run_number > 0:
				self.rebuild_loggers(self.run_number)
				if runDhtTempLog: # TODO Hot Fix issue where dht's data isn't cleared each run (idk why)
					self.loggers['dht'].dht_data_set.clear()

			for key in self.loggers:
				if key != "dht" and key != "pyrapl":
					print("Starting logger for " + key)
					self.loggers[key].start_logging()
				if key == "dht":
					print("Polling DHT")
					self.loggers['dht'].poll_dht22()
				if key == "pyrapl":
					print("Building Meter for this run")
					self.loggers['pyrapl'].create_meter(param)
			if controlTemp:
				self.warm_up()

			### Script Execution Start
			if usePyRAPL:
				self.loggers['pyrapl'].meter.begin()

			self.startTime =  time.time()
			output = subprocess.Popen(command,shell=True, stdout=results_file)
			output.wait()
			self.endTime = time.time()

			if usePyRAPL:
				self.loggers['pyrapl'].meter.end()
			### Script Execution End

			if runDhtTempLog:
				print("Polling DHT")
				self.loggers['dht'].poll_dht22()

			continueLogging = False
			self.elapsedTime = self.endTime - self.startTime
			print("Elapsed time is " + str(self.elapsedTime))

			if controlTemp:
				self.cool_down()

			if runDhtTempLog:
				print("Polling DHT")
				self.loggers['dht'].poll_dht22()

			self.compile_data(param, self.run_number, results_file_string)
			self.run_number+=1

		print("Done with running all tests, taking a 10 second break")
		time.sleep(10)

		return

	def compile_data(self, param, runNumber, results_file):
		this_run = {}
		this_run["Run Number"] = str(runNumber)
		this_run["Parameters"] = str(param)
		this_run["Executable"] = str(executable)
		this_run["Results File"] = "NONE" if results_file is None else results_file
		this_run["Baseline CPU Temp"] = baselineTemp
		this_run["Script Delta"] = self.elapsedTime
		this_run["Script Start"] = self.startTime
		this_run["Script End"] = self.endTime
		if controlTemp:
			this_run["Cooldown Delta"] = self.cooldownDelta
			this_run["Cooldown Start"] = self.cooldownStart
			this_run["Cooldown End"] = self.cooldownEnd
			this_run["Warmup Delta"] = self.warmupDelta
			this_run["Warmup Start"] = self.warmupStart
			this_run["Warmup End"] = self.warmupEnd
		for key in self.loggers:
			this_run[key] = self.loggers[key].get_data_set().copy()

		if runDhtTempLog:
			# TODO Bug here, DHT avg still keeps the 0.0 result, which is wack
			dhtSum = 0.0
			measures = 0
			for dhtMeasure in this_run['dht']:
				if dhtMeasure != 0.0:
					dhtSum += dhtMeasure[1]
					measures += 1
			this_run["Avg Room Temp"] = dhtSum / measures

		if runEnergyLog and usePyRAPL:
			# Add energy value only
			try:
				this_run["Total Energy (Micro Joules)"] = self.loggers['pyrapl'].meter.result.pkg[0]
			except:
				print("Idk why but this_run has no energy measure")
				print(string(self.loggers['pyrapl'].meter.result.pkg[0]))
			#this_run["Total Energy (MilliWatt Hours)"] = 0.0

		global data_list
		data_list.append(this_run)
		return

	def round_robin(self):
		if onPI:
			count = 0
			while CPUTemperature().temperature <= (baselineTemp):
				number = 0
				if number >= sys.maxsize:
					number = 0
				else:
					number = number + 1
				count+=1
		else:
			count = 0
			while round(psutil.sensors_temperatures()['coretemp'][0][1]) <= (baselineTemp):
				number = 0
				if number >= sys.maxsize:
					number = 0
				else:
					number = number + 1
				count+=1


	def warm_up(self):
		self.warmupStart = time.time()
		process_count = 1
		while process_count <= multiprocessing.cpu_count():
			process_not_to_be_seen_again = multiprocessing.Process(target=self.round_robin)
			process_not_to_be_seen_again.start()
			process_count+=1

		self.warmupEnd = time.time()
		self.warmupDelta = self.warmupEnd - self.warmupStart
		print("Delta Warm Up time is " + str(self.warmupDelta))

	def cool_down(self):
		if onPI:
			self.cooldownStart = time.time()
			while round(CPUTemperature().temperature) > (baselineTemp - 3):
				#print("TOO WARM, COOLING " + str(CPUTemperature().temperature) + " -> " + str(baselineTemp - 3))
				time.sleep(5)
			self.cooldownEnd = time.time()
			self.cooldownDelta = self.cooldownEnd - self.cooldownStart
			print("Delta Cool Down time is " + str(self.cooldownDelta))
		else:
			self.cooldownStart = time.time()
			while round(psutil.sensors_temperatures()['coretemp'][0][1]) > (baselineTemp - 3):
				time.sleep(5)
			self.cooldownEnd = time.time()
			self.cooldownDelta = self.cooldownEnd - self.cooldownStartprint("Delta Cool Down time is " + str(self.cooldownDelta))

	def data_to_csv(self):
		global csvFile
#		if runEnergyLog and useMakerHawk:
#			self.gather_energy_data()
#			self.combine_energy_data()

		csvFileName = csvFile
		print("Saving all data to " + csvFileName)
		basic_header_keys = ["Run Number", "Parameters", "Executable", "Results File", "Baseline CPU Temp"]
		if runDhtTempLog:
			basic_header_keys.append("Avg Room Temp")
		if runEnergyLog and useMakerHawk:
			basic_header_keys.append("Avg Volts")
		if runEnergyLog and usePyRAPL:
			basic_header_keys.append("Total Energy (Micro Joules)")
			# basic_header_keys.append("Total Energy (MilliWatt Hours)")
		time_header_keys = ["Script Delta", "Script Start", "Script End"]
		if controlTemp:
			time_header_keys.append(["Cooldown Delta", "Cooldown Start", "Cooldown End", "Warmup Delta", "Warmup Start", "Warmup End"])
		header_row = []
		time_row = []
		with open(csvFileName, 'w', newline='') as csvFile:
			csvWriter = csv.writer(csvFile)
			for dict in data_list:
				header_row.clear()
				time_row.clear()
				for header in basic_header_keys:
					header_row.append(header + ":")
					header_row.append(dict[header])
				for time in time_header_keys:
					time_row.append(time + ":")
					time_row.append(dict[time])
				csvWriter.writerow(header_row)
				csvWriter.writerow(time_row)
				csvWriter.writerow(" ")

				if runEnergyLog and useMakerHawk:
					#self.loggers["amps"] = "ampsKey"
					self.loggers["watts"] = "wattsKey"
					self.loggers["wattHours"] = "wattHourKey"
					if controlTemp:
						wattRunOff = {}
						wattRunOff["wattsWarm"] = dict["wattsWarm"].insert(0,"Watts Warm:")
						wattRunOff["wattsCool"] = dict["wattsCool"].insert(0,"Watts Cool:")
						wattRunOff["wattHoursWarm"] = dict["wattHoursWarm"].insert(0,"Watt Hours Warm:")
						wattRunOff["wattHoursCool"] = dict["wattHoursCool"].insert(0,"Watt Hours Cool:")

				data_header = list(self.loggers.keys())
				if runEnergyLog and usePyRAPL:
					data_header.remove('pyrapl')

				csvWriter.writerow(data_header)
				print("Data to store in CSV")
				print(data_header)
				data_row = []
				times = list(dict["time"])

				dhtIndex = 0

				for t in times:
					data_row.clear()
					for key in dict:
						if key == "time":
							data_row.append(t)
							continue
						if key in basic_header_keys or key in time_header_keys:
							continue
						if key == "dht" and dhtIndex < 3:
							data_row.append(dict[key][dhtIndex][1])
							dhtIndex += 1
							continue
						elif key == "dht" and dhtIndex == 3:
							data_row.append(0.0)
							continue
						if key == "wattHoursWarm" or key == "wattHoursCool":
							continue
						if key == "wattsWarm" or key == "wattsCool":
							continue
						if key == "pyrapl":
							continue
						for data in dict[key]:
							if round(data[0]) == round(t):
								data_row.append(data[1])
								break

					csvWriter.writerow(data_row)
				csvWriter.writerow(" ")
				if controlTemp and showTempCycles:
					for key in wattRunOff:
						csvWriter.writerow(wattRunOff[key])
		return

	def data_to_json(self):
		global jsonFile

		with open(jsonFile, 'w') as json:
			for run in data_list:
				json.dump(run, json)
				json.write(",\n")

		return

	def print_data_list(self):
		for dict in data_list:
			for key in dict:
				print(key + ": " + str(dict[key]))
			print('\n')
		return

	def gather_energy_data(self):
		global ampsFile, voltsFile, finalCsv, energy_list
		if useMakerHawk:
			if runTest:
				self.makerhawk = MakerHawk("Amps.txt", "Volts.txt", sourceDir)
				self.makerhawk.compile_energy()
				return
			print("You used Makerhawk for energy logging")
			print("Get ready to move your volts and amps files over to your source dir")
			confirm = input("Press enter when you've finished importing the Amps and Volts csv's into your Source/dir folder (where you code is).....")
			ampsFile = input("Please enter the name of your Amps File (Don't include Source/dir): ")
			voltsFile = input("Please enter the name of your Volts File (Don't include Source/dir): " )
			#ampsFile="/Amps.txt"
			#voltsFile="Volts.txt"
			print("Compiling data from " + ampsFile + " and " + voltsFile)
			self.makerhawk = MakerHawk(ampsFile, voltsFile, sourceDir)
			self.makerhawk.compile_energy()
		else:
			return
		return

	def combine_energy_data(self):
		global data_list
		print("Parsing energy dictonary into the bigger data dictonary")
		energyIndex = 0
		runCoolDTime = 0.0
		runWarmUpTime = 0.0
		runEnergyCoolDPolls = 0
		runEnergyWarmUpPolls = 0
		for dict in data_list:
			# get time data from this run first (warm up is pre, cool down is post)
			# if warm up/cool down is <= 1s, skip that then
			runTotalTime = dict["Script Delta"]
			runEnergyTotalPolls = math.ceil(runTotalTime / energyInterval)
			if controlTemp:
				runCoolDTime = dict["Cooldown Delta"]
				runEnergyCoolDPolls = math.floor(runCoolDTime / energyInterval)
				runWarmUpTime = dict["Warmup Delta"]
				runEnergyWarmUpPolls = math.floor(runWarmUpTime / energyInterval)
			timeArray = dict["time"]
			#print("Len Time: ", len(timeArray))
			dict['Avg Volts'] = self.makerhawk.get_data_set()['volt']

			#amps = []
			#ampsCool = []
			#ampsWarm = []

			watts = []
			wattsCool = []
			wattsWarm = []

			wattHours = []
			wattHCool = []
			wattHWarm = []

			# this gives us the energy used pre script execution
			if runEnergyWarmUpPolls >= 1 and controlTemp:
				wH = 0
				warmUpPollLimit = energyIndex + runEnergyWarmUpPolls
				while energyIndex < warmUpPollLimit:
					#ampsWarm.append( (t,self.makerhawk.get_data_set()['amps'][energyIndex]) )
					wattsWarm.append( (t,self.makerhawk.get_data_set()['watt'][energyIndex]) )
					if energyIndex != runEnergyWarmUpPolls:
						# formula is wh(Current) = wH(Previous)+((wP+wC)/2)*(6/11)*(1/3600)
						wP = self.makerhawk.get_data_set()['watt'][energyIndex - 1]
						wC = self.makerhawk.get_data_set()['watt'][energyIndex]
						wH = wH + ((wP+wC)/2) * (6/11) * (1/3600)
					wattHWarm.append( (t,wH) )
					energyIndex+=1
				#print("Warm Should be " + str(runEnergyWarmUpPolls + energyIndex) + ", it is " + str(energyIndex))

			# this gives us the energy used during script execution
			wH = 0
			for t in timeArray:
				#print("M-Data at " + str(energyIndex) + " = ",self.makerhawk.get_data_set()['amps'][energyIndex])
				#amps.append( (t,self.makerhawk.get_data_set()['amps'][energyIndex]) )
				watts.append( (t,self.makerhawk.get_data_set()['watt'][energyIndex]) )
				if energyIndex != runEnergyTotalPolls:
					# formula is wh(Current) = wH(Previous)+((wP+wC)/2)*(6/11)*(1/3600)
					#print("WattHours at " + str(energyIndex) + " is " + str(wH))
					wP = self.makerhawk.get_data_set()['watt'][energyIndex - 1]
					wC = self.makerhawk.get_data_set()['watt'][energyIndex]
					#print("Formula is " + str(wH) + " + (" + str(wP) + " + " + str(wC) + ")/2 * (6/11) * (1/3600)")
					wH = wH + ((wP+wC)/2) * (6/11) * (1/3600)
					#print("Which equals " + str(wH))
				wattHours.append( (t,wH) )
				energyIndex+=1
			#print("Main Should be " + str(runEnergyTotalPolls) + ", it is " + str(energyIndex))

			# this gives us the energy used after execution
			if runEnergyCoolDPolls >= 1 and controlTemp:
				#print("Going to - ", (energyIndex + runEnergyCoolDPolls))
				#print("From " + str(energyIndex) + " and " + str(runEnergyCoolDPolls))
				wH = 0
				coolDownPollLimit = energyIndex + runEnergyCoolDPolls
				while energyIndex < coolDownPollLimit:
					#print("I am at " + str(energyIndex))
					#print("Heading to " + str(energyIndex + runEnergyCoolDPolls))
					#print("C-Data at " + str(energyIndex) + " = ",self.makerhawk.get_data_set()['amps'][energyIndex])
					#ampsCool.append( (t,self.makerhawk.get_data_set()['amps'][energyIndex]) )
					wattsCool.append( (t,self.makerhawk.get_data_set()['watt'][energyIndex]) )
					if energyIndex != runEnergyCoolDPolls:
						# formula is wh(Current) = wH(Previous)+((wP+wC)/2)*(6/11)*(1/3600)
						wP = self.makerhawk.get_data_set()['watt'][energyIndex - 1]
						wC = self.makerhawk.get_data_set()['watt'][energyIndex]
						wH = wH + ((wP+wC)/2) * (6/11) * (1/3600)
					wattHCool.append( (t,wH) )
					energyIndex+=1
				#print("Cool Should be " + str(runEnergyCoolDPolls) + ", it is " + str(energyIndex))

			#dict["amps"] = amps
			#dict["ampsWarm"]= ampsWarm
			#dict["ampsCool"]= ampsCool
			dict["watts"] = watts
			dict["wattsWarm"] = wattsWarm
			dict["wattsCool"] = wattsCool
			dict["wattHours"] = wattHours
			dict["wattHoursWarm"] = wattHWarm
			dict["wattHoursCool"] = wattHCool
		return

# End Manager

class TimeLog:
# Start TimeLog
	time_set = []

	def __init__(self, timeInterval):
		self.timeInterval = timeInterval
		return

	def log(self):
		while continueLogging:
			self.time_set.append(float(time.time()))
			time.sleep(self.timeInterval)
		return

	def start_logging(self):
		self.thread.start()
		return

	def build_logger(self):
		self.thread = threading.Thread(target=self.log, name="TimeLogger")
		return

	def rebuild_logger(self,runNumber):
		self.thread = threading.Thread(target=self.log, name="TimeLogger"+str(runNumber))
		self.time_set.clear()
		return

	def get_data_set(self):
		return self.time_set

# End TimeLog

class CpuLog:
# Start CpuLog
	cpu_data_set = []
	success = 0
	failure = 0

	def __init__(self, cpuInterval):
		self.cpuInterval = cpuInterval
		if onPI:
			self.cpu = CPUTemperature()
		return

	def log(self):
		if onPI:
			while continueLogging:
				try:
					#tempfile = open('/sys/class/thermal/thermal_zone0/temp', "r")
					#cpuTempRaw = float(tempfile.read())
					#tempfile.close()
					#cpuTemp = cpuTempRaw / 1000
					cpuTemp = self.cpu.temperature
				except RunTimeError:
					self.failure+=1
					cpuTemp=0.0
					pass
				this_time = time.time()
				if cpuTemp is not None:
					self.success+=1
				else:
					self.failure+=1
					cpuTemp=0.00
				self.cpu_data_set.append( (float(this_time),cpuTemp) )
				time.sleep(self.cpuInterval)
		else:
			while continueLogging:
				try:
					cpuTemp = psutil.sensors_temperatures()['coretemp'][0][1] # Grabs sensors, then the CPU specific temp, then PKG temp, then temp
				except RunTimeError:
					self.failure+=1
					cpuTemp=0.0
					pass
				this_time = time.time()
				if cpuTemp is not None:
					self.success+=1
				else:
					self.failure+=1
					cpuTemp=0.00
				self.cpu_data_set.append( (float(this_time),cpuTemp) )
		return

	def start_logging(self):
		self.thread.start()
		return

	def build_logger(self):
		self.thread = threading.Thread(target=self.log, name="CpuLogger")
	def rebuild_logger(self,runNumber):
		self.thread = threading.Thread(target=self.log, name="CpuLogger"+str(runNumber))
		self.cpu_data_set.clear()

	def print_data(self):
		print("==========CPU==========")
		print("Success: " + str(self.success) + " Failures: " + str(self.failure))
		print("Measures: ")
		print(self.cpu_data_set)

	def get_data_set(self):
		return self.cpu_data_set

# End CpuLog

class DhtLog:
# Start DhtLog
	dht_data_set = []
	success = 0
	failure = 0

	DHT_PIN = 4
	DHT_SENSOR = adafruit_dht.DHT22(DHT_PIN)

	def __init__(self, dhtInterval):
		self.dhtInterval = dhtInterval
	def __init__(self):
		self.dhtInterval = 6

	def log(self):
		while continueLogging:
			try:
				dhtTemp = self.DHT_SENSOR.temperature
			except RuntimeError:
				self.failure+=1
				dhtTemp=0.0
				pass
			this_time = time.time()
			if dhtTemp is not None:
				self.success+=1
			else:
				self.failure+=1
				dhtTemp=0.00
			self.dht_data_set.append( (float(this_time),dhtTemp) )
			time.sleep(self.dhtInterval)
		return

	def start_logging(self):
		self.thread.start()

	def build_logger(self):
		self.thread = threading.Thread(target=self.log, name="DhtLogger")
	def rebuild_logger(self,runNumber):
		self.thread = threading.Thread(target=self.log, name="DhtLogger"+str(runNumber))
		self.dht_data_set.clear()

	def poll_dht22(self):
		try:
			dhtTemp = self.DHT_SENSOR.temperature
		except RuntimeError:
			self.failure+=1
			dhtTemp=0.0
			pass
		this_time = time.time()
		if dhtTemp is not None:
			#print("Polled a temp of " + str(dhtTemp))
			self.success+=1
		else:
			self.failure+=1
			dhtTemp=0.00
		self.dht_data_set.append( (float(this_time),dhtTemp) )
		time.sleep(2)

	def print_data(self):
		print("==========DHT==========")
		print("Success: " + str(self.success) + " Failures: " + str(self.failure))
		print("Measures: ")
		print(self.dht_data_set)

	def get_data_set(self):
		return self.dht_data_set

# End DhtLog

class LoadLog:
# Start LoadLog
	load_data_set = []
	success = 0
	failure = 0

	def __init__(self, loadInterval):
		self.loadInterval = loadInterval
		return

	def log(self):
		self.counter = 0
		while continueLogging:
			try:
				load_list = os.getloadavg()
				load = load_list[0]
			except IndexError:
				pass
			except RunTimeError:
				pass
			this_time = time.time()
			if load is not None:
				self.success+=1
			else:
				self.failure+=1

			self.load_data_set.append( (float(this_time),load) )
			time.sleep(self.loadInterval)
		return

	def start_logging(self):
		self.thread.start()
		return

	def build_logger(self):
		self.thread = threading.Thread(target=self.log, name="LoadLogger")
		return
	def rebuild_logger(self,runNumber):
		self.thread = threading.Thread(target=self.log, name="LoadLogger"+str(runNumber))
		self.load_data_set.clear()
		return

	def print_data(self):
		print("==========LOAD==========")
		print("Success: " + str(self.success) + " Failures: " + str(self.failure))
		print("Measures: ")
		print(self.load_data_set)
		return

	def get_data_set(self):
		return self.load_data_set

# End LoadLog

class MakerHawk:
# Start MakerHawk
	hawk_data_set = {}
	# Data stored somethig like "[(tick, first, second), (t,f,s),...]

	def __init__(self, ampsFile, voltsFile, source):
		self.source = source
		with open(source + ampsFile, 'r', encoding="utf8") as file:
			lines = file.readlines()
		lines = [line.replace(' ', '') for line in lines]
		lines = [line.replace('\t',',') for line in lines]
		with open(source + ampsFile, 'w', encoding="utf8") as file:
			file.writelines(lines)
		self.ampsFile = source + ampsFile
		self.ampsKey = "Current(A)-Currentgraph"

		with open(source + voltsFile, 'r', encoding="utf8") as file:
			lines = file.readlines()
		lines = [line.replace(' ', '') for line in lines]
		lines = [line.replace('\t',',') for line in lines]
		with open(source + voltsFile, 'w', encoding="utf8") as file:
			file.writelines(lines)
		self.voltsFile = source + voltsFile
		self.voltsKey = "Voltage(V)-Voltagegraph"

		# Every 6 seconds == 11 Makerhawk Polls
		self.energyInterval = (11 / 6) * energyInterval
		return

	def compile_energy(self):
		self.gather_averaged_amps()
		self.gather_averaged_volts()
		self.gather_averaged_watts()
		print("Successfully compiled all energy data into one dictonary!")
		return

	def gather_averaged_amps(self):
		amps_list = []
		with open(self.ampsFile, 'r') as amps:
			ampsReader = csv.DictReader(amps)
			for amps in ampsReader:
				avgIndex = 0
				avgAmps = 0.0
				while avgIndex < self.energyInterval:
					avgAmps += round(float(amps[self.ampsKey]), 3)
					avgIndex += 1
				amps_list.append(round(avgAmps / self.energyInterval, 3))
		self.hawk_data_set['amps'] = amps_list
		return

	def gather_amps(self):
		amps_list = []
		with open(self.ampsFile, 'r') as amps:
			ampsReader = csv.DictReader(amps)
			for amps in ampsReader:
				amps_list.append(round(float(amps[self.ampsKey]), 3))
		self.hawk_data_set['amps'] = amps_list
		return

	def gather_averaged_volts(self):
		voltsSum = 0.0
		voltsCount = 0
		with open(self.voltsFile, 'r') as volts:
			voltsReader = csv.DictReader(volts)
			for volt in voltsReader:
				voltsSum += round(float(volt[self.voltsKey]), 2)
				voltsCount += 1
		self.hawk_data_set['volt'] = round(voltsSum / voltsCount, 4)
		return

	def gather_averaged_watts(self):
		watts_list = []
		for amps in self.hawk_data_set['amps']:
			watts_list.append(round(amps * self.hawk_data_set['volt'], 4))
		self.hawk_data_set['watt'] = watts_list
		return

	def print_data(self):
		print("==========HAWK ENERGY==========")
		for key in self.hawk_data_set:
			print(key + "======")
			print(self.hawk_data_set[key])

	def get_data_set(self):
		return self.hawk_data_set

class PyRAPLLog:

	pyraplDataSet = []
	meter = None
	# Holds a series of meters like [meter.results(1), meter.results(2),..., meter.results(N)]
	#meter.result returns an object like class pyRAPL.Result(label, timestamp, duration, pkg=None, dram=None)
	# label (str) – measurement label
	# timestamp (float) – measurement’s beginning time (expressed in seconds since the epoch)
	# duration (float) – measurement’s duration (in micro seconds)
	# pkg (Optional[List[float]]) – list of the CPU energy consumption -expressed in micro Joules- (one value for each socket) if None, no CPU energy consumption was recorded
	# dram (Optional[List[float]]) – list of the RAM energy consumption -expressed in seconds- (one value for each socket) if None, no RAM energy consumption was recorded


	def __init__(self):
		return

	def build_logger(self):
		pyRAPL.setup(devices=[pyRAPL.Device.PKG])
		return

	def create_meter(self, paramString):
		self.meter = pyRAPL.Measurement(paramString)
		return

	def compile_energy(self, meter):
		self.pyraplDataSet.append( (float(meter.timestamp), meter.result) )
		return

	def rebuild_logger(self, valueToBeTrashed):
		create_meter()
		return

	def print_data(self):
		print("==========PYRAPL ENERGY==========")
		for result in self.pyraplDataSet:
			print(result)
		return

	def get_data_set(self):
		return self.pyraplDataSet

# End PyRAPL

### Functions
##
#

### Main Execution
##
#

manager = Manager()

if buildConfig or buildParams:
	if buildConfig:
		print("Building Config")
		manager.build_config_file()
	if buildParams:
		print("Building Params")
		manager.build_params_file()
	sys.exit()

manager.read_configs()

if not runBaseline:
	manager.build_source_code()
	manager.read_params()

manager.build_loggers()

if runBaseline:
	manager.run_baseline()
else:
	manager.run_loggers()

if runClean:
	if runEnergyLog and useMakerHawk:
		manager.gather_energy_data()
		manager.combine_energy_data()
		#manager.makerhawk.print_data()
	if toCSV:
		manager.data_to_csv()
	if toJSON:
		manager.data_to_json()
