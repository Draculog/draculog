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
import json # used to read in params file (so that file can be called anything and can be anything)
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

data_list = [] # to store all data in 2D array [ [Time, Sensors, ...], [T, S, ...], ... ]
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
# Start Builder
	# TODO do I need this?
	def __init__(self, loggers):
		self.loggers = loggers

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

		with open(sourceDir+paramsFile) as f:
			variables = 
		#print(variables)

		return

	def build_source_code(self):
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
		# TODO Build loggers one at a time, using booleans to determine what to build
		# if runCpuLog then cpu = CpuLog(), self.logger.append(cpu)
		return

	def run_loggers(self):
		global continueLogging
		continueLogging = True
		time.sleep(1)

		self.startTime = time.time()
		self.dht.start_logging()
		self.cpu.start_logging()
		self.load.start_logging()

		# Do stuff
		# subprocess.Popen("./"+sourceDir+executable, shell=False)
		time.sleep(30)

		continueLogging = False
		self.endTime = time.time()
		self.elapsedTime = self.endTime - self.startTime
		print("Elapsed time is " + str(self.elapsedTime))
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
				#print("c-0.0,")
				self.failure+=1
				cpuTemp=0.0
				pass

			if cpuTemp is not None:
				self.success+=1
				#print("c-{0:0.01f},s-{1:d},f-{2:d}".format(cpuTemp,self.success,self.failure))
				#print("CPU TIME IS " + str(time.time()))

			else:
				#print("c-0.00,")
				self.failure+=1
				cpuTemp=0.00

			self.cpu_data_set.append(cpuTemp)
			time.sleep(self.cpuInterval)
		if runTest:
			print("CPU List time->temp")
			print(self.cpu_time_set)
			print(self.cpu_data_set)

	def start_logging(self):
		self.thread.start()

	def build_logger(self):
		self.thread = threading.Thread(target=self.log, name="CpuLogger")


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
		if dhtInterval <= 2:
			print("ERROR, too short of a time between polls, changing to 1/3")
			dhtInterval = 3
		self.dhtInterval = dhtInterval

	def log(self):
		while continueLogging:
			try:
				dhtTemp = self.DHT_SENSOR.temperature
				self.dht_time_set.append(time.time())

			except RuntimeError:
				self.failure+=1
				#print("d-0.0,")
				dhtTemp=0.0
				pass

			if dhtTemp is not None:
				self.success+=1
				#print("d-{0:0.01f},s-{1:d},f-{2:d}".format(dhtTemp, self.success,self.failure))
				#print("DHT TIME IS " + str(time.time()))

			else:
				self.failure+=1
				#print("d-0.00,")
				dhtTemp=0.00

			self.dht_data_set.append(dhtTemp)
			time.sleep(self.dhtInterval)
		if runTest:
			print("DHT List time->temp")
			print(self.dht_time_set)
			print(self.dht_data_set)

	def start_logging(self):
		self.thread.start()

	def build_logger(self):
		self.thread = threading.Thread(target=self.log, name="DhtLogger")

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
				#raw = subprocess.check_output('uptime').decode"utf8").replace(',','')
				#load = raw.split()[10]
				load_list = os.getloadavg()
				load = load_list[0]
				self.load_time_set.append(time.time())

			except IndexError:
				#load = raw.split()[7]
				pass
			except RunTimeError:
				pass

			if load is not None:
				self.success+=1
				#print("c-{0:0.01f},s-{1:d},f-{2:d}".format(load,self.success,self.failure))
				#print("LOAD TIME IS " + str(time.time()))

			else:
				#print("c-0.00,")
				self.failure+=1

			self.load_data_set.append(load)
			time.sleep(self.loadInterval)
		if runTest:
			print("Load List time->temp")
			print(self.load_time_set)
			print(self.load_data_set)

	def start_logging(self):
		self.thread.start()

	def build_logger(self):
		self.thread = threading.Thread(target=self.log, name="LoadLogger")


# End LoadLog




### Functions
##
#

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

loggers = []

builder = Builder(loggers)

if runConfig:
	builder.read_config()

builder.build_source_code()

builder.read_params()






# string control = ""
# while control is not "quit"
# loop and permutate asking for next permutaion
# if it is quit end looping
# if we have said to clean the data, clean the resultant data store in "/Results/"
