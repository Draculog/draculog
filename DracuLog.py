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
import adafruit_dht
import gpiod
import board
import pyserial

### Global Variables
##
# Basic Global Variables
highBaseTemp = 60 # Warm up to here
lowBaseTemp = 55 # Cool down to here

DHT_PIN = 4
DHT_SENSOR = adafruit_dht.DHT22(DHT_PIN)

### Pre Execution
## This is only for testing purposes currently
#
if len(sys.argv) > 1:
	if 'test' in sys.argv or 't' in sys.argv:
		print("You are now using the testing version of the software with preassigned variables")
		runTest = True
	else:
		print("You've used an unknown flag, ending program")
		sys.exit()


SourceCodeFiles="./Source"
ResultsFiles="./Results"

# Variables to read before execution
runCpuTempLog = False
runDhtTempLog = False
runEnergyLog = False
runLoadLog = False
runClean = False
runTest = False

# Variables to read at execution
cpuInterval = 1
dhtInterval = 2
length = 60
# Grab Code from "/Source/" folder so this should be typed as "/Source/codeToRun"
builtScript = "blank"
sourceScript = "blank"

### Classes
##
#

class Builder:
# Start Builder
	def __init__(self, loggers):
		self.loggers = loggers

	def build_source_code(self):
		if os.path.isdir(SourceCodeFiles):
			print("Found Files, building files within")
			files_to_build = input("What files should I build? Enter now:- ")
			# if files_to_build is DNE quit; else continue
			compiler = input("What Compiler should I use?\nClang, GCC, or Java?\nEnter now:- ")
			# if compiler is DNE (not clang, gcc, java etc (java to be left for last), exit; else continue

		else:
			print("No Files nor Folder found, making folder and exiting")
			os.mkdir(SourceCodeFiles)
			sys.exit()

	def build_results(self):
		if os.path.isdir(ResultsFiles):
			try:
				shutil.rmtree(ResultsFiles)
			except:
				print("Error while executing shutil")
		os.mkdir(ResultsFiles)

	def build_loggers(self):
		cpu = CpuLog(2)
		dht = DhtLog(5)

		cpu.build_logger()
		dht.build_logger()

	def run_loggers(self):
		global continueLogging
		continueLogging = True
		time.sleep(1)

		startTime = time.time()
		self.dht.start_logging()
		self.cpu.start_logging()

		# Do stuff
		time.sleep(10)

		continueLogging = False
		endTime = time.time()
		print("Elapsed time is " + str(endTime - startTime))
# End Builder

class CpuLog:
# Start CpuLog
	success = 0
	failure = 0
	def __init__(self, cpuInterval):
		self.cpuInterval = cpuInterval

	def log(self):
		self.counter = 0
		while continueLogging:
			try:
				tempfile = open('/sys/class/thermal/thermal_zone0/temp', "r")
				cpuTempRaw = float(tempfile.read())
				tempfile.close()
				cpuTemp = cpuTempRaw / 1000

			except RunTimeError:
				print("0.0,")
				self.failure+=1
				pass

			if cpuTemp is not None:
				self.success+=1
				print("{0:0.01f},{1:d}".format(cpuTemp,self.success))
			else:
				print("0.00,")
				self.failure+=1

			time.sleep(self.cpuInterval)
			self.counter+=1

	def start_logging(self):
		self.thread.start()

	def build_log(self):
		thread = threading.Thread(target=self.log, name="CpuLogger")


# End CpuLog

class DhtLog:
# Start DhtLog
	success = 0
	failure = 0
	def __init__(self, dhtInterval):
		self.dhtInterval = dhtInterval

	def log(self):
		self.counter = 0
		while continueLogging:
			try:
				dhtTemp = DHT_SENSOR.temperature
			except RunTimeError:
				self.failure+=1
				print("0.0,")
				pass

			if dhtTemp is not None:
				self.success+=1
				print("{0:0.01f}, success - {1:d}, failure - {2:d}".format(dhtTemp, self.success, self.failure))
			else:
				self.failure+=1
				print("0.00,")
			time.sleep(self.dhtInterval)

	def start_logging(self):
		self.thread.start()

	def build_logger(self):
		thread = threading.Thread(target=self.log, name="DhtLogger")

# End DhtLog

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

input_string = input("Please enter the logging systems you want to do, seperated by spaces:-")
loggers = input_string.split()

builder = Builder(loggers)
builder.build_loggers()
builder.run_loggers()

# string control = ""
# while control is not "quit"
# loop and permutate asking for next permutaion
# if it is quit end looping
# if we have said to clean the data, clean the resultant data store in "/Results/"
