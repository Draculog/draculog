#### DracuLog - The one stop shop of CPU/PI logging software
### Created by Daniel Jacoby alongside Dr. Joshua Gross
##
#

### Imports
##
# Imports for basic system processes
import os
import sys
import time
import subprocess
import threading
import shutil
# Imports for external attachments
import adafruit_dht # for DHT Sensor
import gpiod # for DHT Sensor
import board # for DHT Sensor
from gpiozero import CPUTemperature # for CPU Temp
import serial

### Global Variables
##
# Basic Global Variables
highBaseTemp = 60 # Warm up to here
lowBaseTemp = 55 # Cool down to here

data_list = []

SourceCodeFiles="./Source"
ResultsFiles="./Results"

# Variables to read before execution
runCpuTempLog = False
runDhtTempLog = False
runEnergyLog = False
runLoadLog = False
runClean = False
runTest = False
runConfig = False

# Variables to read at execution
cpuInterval = 1
dhtInterval = 2
length = 60
# Grab Code from "/Source/" folder so this should be typed as "/Source/codeToRun"
builtScript = "blank"
sourceScript = "blank"

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
	#data_list = []

	def __init__(self, loggers):
		self.loggers = loggers

	def build_source_code(self):
		sourceDir = "source"

		if not runConfig:
			sourceDir = input("Folder name (/foldername/:")
			os.system("echo compiling source files via makefile using cmd make")
			os.system("make")
		else:
			print("Exit")

	def build_results(self):
		if os.path.isdir(ResultsFiles):
			try:
				shutil.rmtree(ResultsFiles)
			except:
				print("Error while executing shutil")
		os.mkdir(ResultsFiles)

	def build_loggers(self):
		self.cpu = CpuLog(3)
		self.dht = DhtLog(3)
		self.load = LoadLog(3)

		self.cpu.build_logger()
		self.dht.build_logger()
		self.load.build_logger()

	def run_loggers(self):
		global continueLogging
		continueLogging = True
		time.sleep(1)

		startTime = time.time()
		self.dht.start_logging()
		self.cpu.start_logging()
		self.load.start_logging()

		# Do stuff
		time.sleep(30)

		continueLogging = False
		endTime = time.time()
		print("Elapsed time is " + str(endTime - startTime))
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

#input_string = input("Please enter the logging systems you want to do, seperated by spaces:-")
loggers = "" #input_string.split()

builder = Builder(loggers)
builder.build_source_code()
#builder.build_loggers()
#builder.run_loggers()

# string control = ""
# while control is not "quit"
# loop and permutate asking for next permutaion
# if it is quit end looping
# if we have said to clean the data, clean the resultant data store in "/Results/"
