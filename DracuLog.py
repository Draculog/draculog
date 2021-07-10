#### DracuLog - The one stop shop of CPU/PI logging software
### Created by Daniel Jacoby alongside Dr. Joshua Gross
##
#

### Imports
##
# Imports for basic system processes
import os # used all over for operations
import sys
import time # used to time everything (and to sleep for xInterval)
import subprocess # used for code execution
import threading # used to multi thread the loggers/sensors
import shutil # used in results folder creation/deletion, install
import configparser # install using pip
import re # used to read in params file (stripping whitespace and checking for #
# Imports for external attachments
import adafruit_dht # for DHT Sensor, install
import gpiod # for DHT Sensor, install
import board # for DHT Sensor, install
from gpiozero import CPUTemperature # for CPU Temp, install
import serial # install

### Global Variables
##
# Basic Global Variables
highBaseTemp = 60 # Warm up to here
lowBaseTemp = 55 # Cool down to here

data_list = [] # to store all data in 2D Dictonary structured as such ->
# data_list = [
#			{	'run_1':"parameters_1",
#				'sensor_1_time':[time_data,time_data,...],
#				'sensor_1_data':[m_data,m_data,m_data,...], ...
#			},
#			{	'run_2':"parameters_2",
#					'...':[...],
#					'...':[...], ...
#			}, ...
#		]

params_list = []

# Variables to read before execution
controlTemp = False
runCpuTempLog = False
runDhtTempLog = False
runEnergyLog = False
useMakerHawk = False
useLog4 = False
runLoadLog = False
runClean = False
runTest = True
runConfig = False

# Variables to read at execution
cpuInterval = 1
dhtInterval = 2
loadInterval = 5
energyInterval = 2

# Grab Code from "/Source/" folder so this should be typed as "/Source/codeToRun"
sourceDir = "Source/"
paramsFile = "file"
executable = "file"

### Pre Execution
##
#
if len(sys.argv) > 1:
	if 'test' in sys.argv or 't' in sys.argv:
		print("You are now using the testing version of the software with preassigned variables")
		runTest = True
	if 'config' in sys.argv or 'c' in sys.argv:
		print("Using config.ini file instead of prompts")
		runConfig = True
	else:
		print("You've used an unknown flag, ending program")
		sys.exit()

### Classes
##
#

class Builder:
# Start Builde
	def __init__(self):
		self.loggers = {}

	def read_config(self):
		global sourceDir,paramsFile,controlTemp,runCpuTempLog,cpuInterval,runDhtTempLog,dhtInterval
		global runLoadLog,loadInterval,runEnergyLog,energyInterval,useMakerHawk,useLog4,runClean

		configReader = configparser.ConfigParser()
		configReader.read("ReadMe.ini")

		sourceDir = configReader.get("Parameters", "SourceDir")
		paramsFile = configReader.get("Parameters", "ParamsFile")
		controlTemp = configReader.getboolean("Parameters", "TempControl")

		runCpuTempLog = configReader.getboolean("Parameters", "CpuTempLog")
		cpuInterval = configReader.getint("Parameters", "CpuInterval")

		runDhtTempLog = configReader.getboolean("Parameters", "DhtTempLog")
		dhtInterval = configReader.getint("Parameters", "DhtInterval")

		runLoadLog = configReader.getboolean("Parameters", "LoadLog")
		loadInterval = configReader.getint("Parameters", "LoadInterval")

		runEnergyLog = configReader.getboolean("Parameters", "EnergyLog")
		energyInterval = configReader.getint("Parameters", "EnergyInterval")
		useMakerHawk = configReader.getboolean("Parameters", "MakerHawk")
		useLog4 = configReader.getboolean("Parameters", "Log4")

		runClean = configReader.getboolean("Parameters", "CleanData")

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
			v = re.sub(r"\s+","",var,flags=re.UNICODE)
			if not v[0] == '#':
				params_list.append(var.rstrip())
		return

	def build_source_code(self): #TODO retool so I can systematically build executable files with certain params
		global sourceDir,executable,paramsFile
		#check if we are going to use java vs c++

		if not runConfig:
			# grab source files from user prompt
			sourceDir = input("Folder name (foldername/): ")
		else:
			# grab source files from config.ini
			print("Grabbed Source Code, building code located at: " + sourceDir)

		if not os.path.isdir(sourceDir):
			print("ERROR, source dir DNE")
			return

		if not os.path.isfile(sourceDir + "Makefile"):
			print("ERROR, source dir Makefile DNE")
			return

		print("Compiling Source Files using given Makefile")
		os.system("cd " + sourceDir + "&& make")

		for filename in os.listdir(sourceDir):
			if os.path.isfile(sourceDir+filename) and os.access(sourceDir+filename, os.X_OK):
				executable = sourceDir+filename
		return

	def build_results(self):
		if os.path.isdir(ResultsFiles):
			try:
				shutil.rmtree(ResultsFiles)
			except:
				print("Error while executing shutil")
		os.mkdir(ResultsFiles)
		return

	def build_loggers(self):
		if runCpuTempLog:
			cpu = CpuLog(cpuInterval)
			cpu.build_logger()
			self.loggers['cpu'] = cpu
		if runDhtTempLog:
			dht = DhtLog()
			self.loggers['dht'] = dht
		if runLoadLog:
			load = LoadLog(loadInterval)
			load.build_logger()
			self.loggers['load'] = load
		return

	def run_loggers(self): # TODO take in Param used to execute, since we know executable file, sourcedir, but not curr param
		global continueLogging
		continueLogging = True
		print("Starting Tests and Logging using ->")
		print(params_list)
		time.sleep(1)

		for key in self.loggers:
			if key != "dht":
				print("Starting logger for " + key)
				self.loggers[key].start_logging()

		self.loggers['dht'].poll_dht22()
		self.startTime =  time.time()

		# subprocess.Popen("./"+sourceDir+executable+" "+param, shell=False) # looks like ./sorts bubble 100000
		time.sleep(15)

		self.loggers['dht'].poll_dht22()

		continueLogging = False
		self.endTime = time.time()
		self.elapsedTime = self.endTime - self.startTime
		print("Elapsed time is " + str(self.elapsedTime))

		time.sleep(5) # temp for cooling down

		self.loggers['dht'].poll_dht22()

		for key in self.loggers:
			self.loggers[key].print_data()
		return

	def compile_data(self, param, runNumber):
		data_list.append({"run_"+str(runNumber):str(param)})
		for key in self.loggers:
			data_list[runNumber][key+"_t"] = self.loggers[key].get_time_set()
			data_list[runNumber][key+"_d"] = self.loggers[key].get_data_set()
		return

# End Builder

class CpuLog:
# Start CpuLog
	cpu_data_set = []
	cpu_time_set = []
	success = 0
	failure = 0

	def __init__(self, cpuInterval):
		self.cpuInterval = cpuInterval
		self.cpu = CPUTemperature()

	def log(self):
		while continueLogging:
			try:
				#tempfile = open('/sys/class/thermal/thermal_zone0/temp', "r")
				#cpuTempRaw = float(tempfile.read())
				#tempfile.close()
				#cpuTemp = cpuTempRaw / 1000
				cpuTemp = self.cpu.temperature
				self.cpu_time_set.append(time.time())

			except RunTimeError:
				self.failure+=1
				cpuTemp=0.0
				pass

			if cpuTemp is not None:
				self.success+=1
			else:
				self.failure+=1
				cpuTemp=0.00
			self.cpu_data_set.append(cpuTemp)
			time.sleep(self.cpuInterval)
		return

	def start_logging(self):
		self.thread.start()

	def build_logger(self):
		self.thread = threading.Thread(target=self.log, name="CpuLogger")

	def print_data(self):
		print("==========CPU==========")
		print("Success: " + str(self.success) + " Failures: " + str(self.failure))
		print("Times: ")
		print(self.cpu_time_set)
		print("Measures: ")
		print(self.cpu_data_set)

	def get_time_set(self):
		return self.cpu_time_set

	def get_data_set(self):
		return self.cpu_data_set


# End CpuLog

class DhtLog:
# Start DhtLog
	dht_data_set = []
	dht_time_set = []
	success = 0
	failure = 0

	DHT_PIN = 4
	DHT_SENSOR = adafruit_dht.DHT22(DHT_PIN)

	def __init__(self, dhtInterval):
		self.dhtInterval = dhtInterval
	def __init__(self):
		self.dhtInterval = 3

	def log(self):
		while continueLogging:
			try:
				dhtTemp = self.DHT_SENSOR.temperature
				self.dht_time_set.append(time.time())
			except RuntimeError:
				self.failure+=1
				dhtTemp=0.0
				pass
			if dhtTemp is not None:
				self.success+=1
			else:
				self.failure+=1
				dhtTemp=0.00
			self.dht_data_set.append(dhtTemp)
			time.sleep(self.dhtInterval)
		return

	def start_logging(self):
		self.thread.start()

	def build_logger(self):
		self.thread = threading.Thread(target=self.log, name="DhtLogger")

	def poll_dht22(self):
		try:
			dhtTemp = self.DHT_SENSOR.temperature
			self.dht_time_set.append(time.time())
		except RuntimeError:
			self.failure+=1
			dhtTemp=0.0
			pass
		if dhtTemp is not None:
			self.success+=1
		else:
			self.failure+=1
			dhtTemp=0.00
		self.dht_data_set.append(dhtTemp)

	def print_data(self):
		print("==========DHT==========")
		print("Success: " + str(self.success) + " Failures: " + str(self.failure))
		print("Times: ")
		print(self.dht_time_set)
		print("Measures: ")
		print(self.dht_data_set)

	def get_time_set(self):
		return self.dht_time_set

	def get_data_set(self):
		return self.dht_data_set

# End DhtLog

class LoadLog:
# Start LoadLog
	load_data_set = []
	load_time_set = []
	success = 0
	failure = 0

	def __init__(self, loadInterval):
		self.loadInterval = loadInterval

	def log(self):
		self.counter = 0
		while continueLogging:
			try:
				load_list = os.getloadavg()
				load = load_list[0]
				self.load_time_set.append(time.time())
			except IndexError:
				pass
			except RunTimeError:
				pass

			if load is not None:
				self.success+=1
			else:
				self.failure+=1

			self.load_data_set.append(load)
			time.sleep(self.loadInterval)
		return

	def start_logging(self):
		self.thread.start()

	def build_logger(self):
		self.thread = threading.Thread(target=self.log, name="LoadLogger")

	def print_data(self):
		print("==========LOAD==========")
		print("Success: " + str(self.success) + " Failures: " + str(self.failure))
		print("Times: ")
		print(self.load_time_set)
		print("Measures: ")
		print(self.load_data_set)

	def get_time_set(self):
		return self.load_time_set

	def get_data_set(self):
		return self.load_data_set

# End LoadLog




### Functions
##
#

def RunTests():
	print("Running Desired Loggers and Tests!")
	return

def WarmUp():
	print("Warm Up")
	return

def CoolDown():
	print("Cool Down")
	return

def Cleaner():
	print("CLEANER")
	return;


### Main Execution
##
#

builder = Builder()

if runConfig:
	builder.read_config()

builder.read_params()

builder.build_source_code()

builder.build_loggers()

builder.run_loggers()

builder.compile_data(params_list[0],0)

print(data_list)


# string control = ""
# while control is not "quit"
# loop and permutate asking for next permutaion
# if it is quit end looping
# if we have said to clean the data, clean the resultant data store in "/Results/"
