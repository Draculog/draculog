#### DracuLog - The one stop shop of CPU/PI logging software
### Created by Daniel Jacoby alongside Dr. Joshua Gross
##
#

#TODO impliment second cleaner script that is called from this script at the end, passing in 3 csv's (possibly)
# one for the cpu/dht/load/time raw data, one for volts and one for amps

### Imports
##
# Imports for basic system processes
import os # used all over for operations
import sys # now used to heat up the cpu
import time # used to time everything (and to sleep for xInterval)
import subprocess # used for code execution
import threading # used to multi thread the loggers/sensors
import multiprocessing # used to heat up the cpu
import shutil # used in results folder creation/deletion, install
import configparser # install using pip
import re # used to read in params file (stripping whitespace and checking for #
import csv # used for creation of CSV file of raw data
import shutil # used to copy raw csv's elsewhere
# Imports for external attachments
import adafruit_dht # for DHT Sensor, install
import gpiod # for DHT Sensor, install
import board # for DHT Sensor, install
from gpiozero import CPUTemperature # for CPU Temp, install
import serial # install
#import MakerHawkDataCompiler.py

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
useLog4 = False
runLoadLog = False
runClean = False
runTest = True
runConfig = False

# Variables to read at execution
cpuInterval = 6
dhtInterval = 6
loadInterval = 6
energyInterval = 6
timeInterval = 6

# Grab Code from "/Source/" folder so this should be typed as "/Source/codeToRun"
sourceDir = "Source/"
paramsFile = "file"
executable = "file"
csvFile = "file"
finalCsv = "file"
voltsFile = "file"
ampsFile = "file"

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
		global sourceDir,paramsFile,csvFile,controlTemp,baselineTemp,runCpuTempLog,cpuInterval,runDhtTempLog
		global dhtInterval,runLoadLog,loadInterval,runEnergyLog,energyInterval,useMakerHawk,useLog4,runClean

		configReader = configparser.ConfigParser()
		configReader.read("ReadMe.ini")

		sourceDir = configReader.get("Parameters", "SourceDir")
		paramsFile = configReader.get("Parameters", "ParamsFile")
		csvFile = configReader.get("Parameters", "CsvFile")

		controlTemp = configReader.getboolean("Parameters", "TempControl")
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
		useLog4 = configReader.getboolean("Parameters", "Log4")

		runClean = configReader.getboolean("Parameters", "CleanData")

		return

	def get_configs(self):
		global sourceDir,paramsFile,controlTemp,baselineTemp,runCpuTempLog,cpuInterval,runDhtTempLog,dhtInterval
		global runLoadLog,loadInterval,runEnergyLog,energyInterval,useMakerHawk,useLog4,runClean

		choice = bool(input("Do you want to have a baseline temp? Y/N: "))
		if upper(choice) == "Y" or upper(choice) == "YES":
			controlTemp = True
		else:
			controlTemp = False
		baselineTemp = int(input("Please enter the baseline temp: "))

		runCpuTempLog = distutils.util.strtobool(input("Do you want to measure CPU Temps? Y/N: "))
		cpuInterval = int(input("Please enter the CPU polling interval: "))

		runDhtTempLog = distutils.util.strtobool(input("Do you want to measure room temp? Y/N:  "))
		dhtInterval = int(input("Please enter the DHT polling interval: "))

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
			return

		if not os.path.isfile(sourceDir + "Makefile"):
			print("ERROR, source dir Makefile DNE")
			return

		print("Compiling Source Files using given Makefile")
		os.system("cd " + sourceDir + "&& make")

		for filename in os.listdir(sourceDir):
			if os.path.isfile(sourceDir+filename) and os.access(sourceDir+filename, os.X_OK):
				executable = filename
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
			if useMakerHawk:
				pass
			if useLog4:
				pass
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
			if key != "dht":
				self.loggers[key].rebuild_logger(runNumber)

	def run_loggers(self):
		print("Running Tests with all params using given source code")
		run_number = 0

		if runEnergyLog and useMakerHawk:
			confirm = input("Please get your MakerHawk software ready, then hit enter to start a 10 second countdown.....")
			self.count_down(10)

		for param in params_list:
			time.sleep(6)
			global continueLogging
			continueLogging = True
			print("Starting Tests and Logging using -> " + param)

			command = "./"+sourceDir+executable+" "+param

			results_file_string = sourceDir+param+"_results.txt"
			results_file = open(results_file_string, 'w')

			if run_number > 0:
				self.rebuild_loggers(run_number)
				if runDhtTempLog: # TODO Hot Fix issue where dht's data isn't cleared each run (idk why)
					self.loggers['dht'].dht_data_set.clear()

			for key in self.loggers:
				if key != "dht":
					print("Starting logger for " + key)
					self.loggers[key].start_logging()
				if key == "dht":
					print("Polling DHT")
					self.loggers['dht'].poll_dht22()

			self.warm_up()

			self.startTime =  time.time()
			output = subprocess.Popen(command,shell=True, stdout=results_file)
			output.wait()
			self.endTime = time.time()


			if runDhtTempLog:
				print("Polling DHT")
				self.loggers['dht'].poll_dht22()

			continueLogging = False
			self.elapsedTime = self.endTime - self.startTime
			print("Elapsed time is " + str(self.elapsedTime))

			self.cool_down()

			if runDhtTempLog:
				print("Polling DHT")
				self.loggers['dht'].poll_dht22()

			self.compile_data(param, run_number, results_file_string)
			run_number+=1
		print("Done with running tests")
		if runEnergyLog:
			print("Stop Energy Measures now and upload volts and watts data to this device in Source Folder")
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
		this_run["Cooldown Delta"] = self.cooldownDelta
		this_run["Cooldown Start"] = self.cooldownStart
		this_run["Cooldown End"] = self.cooldownEnd
		this_run["Warmup Delta"] = self.warmupDelta
		this_run["Warmup Start"] = self.warmupStart
		this_run["Warmup End"] = self.warmupEnd
		for key in self.loggers:
			this_run[key] = self.loggers[key].get_data_set().copy()
		# To Add avg room temp just in case
		dhtSum = 0.0
		measures = 0
		for dhtMeasure in this_run['dht']:
			if dhtMeasure != 0.0:
				dhtSum += dhtMeasure[1]
				measures += 1
		this_run["Avg Room Temp"] = dhtSum / measures

		global data_list
		data_list.append(this_run)
		return

	def round_robin(self):
		count = 0
		while CPUTemperature().temperature <= (baselineTemp):
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
		self.cooldownStart = time.time()
		while round(CPUTemperature().temperature) > (baselineTemp - 3):
			print("TOO WARM, COOLING " + str(CPUTemperature().temperature) + " -> " + str(baselineTemp - 3))
			time.sleep(5)
		self.cooldownEnd = time.time()
		self.cooldownDelta = self.cooldownEnd - self.cooldownStart

	def data_to_csv(self):
		global csvFile
		# TODO Make CSV File for raw data using data_list list of dicts
		csvFileName = sourceDir+csvFile
		basic_header_keys = ["Run Number", "Parameters", "Executable", "Results File", "Baseline CPU Temp",
					"Avg Room Temp"] #, "dht"]
		time_header_keys = ["Script Delta", "Script Start", "Script End",
					"Cooldown Delta", "Cooldown Start", "Cooldown End",
					"Warmup Delta", "Warmup Start", "Warmup End"]
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
				data_header = list(self.loggers.keys())
				csvWriter.writerow(data_header)

				data_row = []
				times = list(dict["time"])

				dhtFlop = False
				dhtIndex = 0

				for t in times:
					data_row.clear()
					for key in dict:
						#print(key)
						if key == "time":
							data_row.append(t)
							continue
						if key in basic_header_keys or key in time_header_keys:
							continue
						# TODO Make algorithm that only puts out dht data
						if key == "dht" and dhtIndex < 3:
							#print(dict[key][dhtIndex])
							#print(dict[key])
							data_row.append(dict[key][dhtIndex][1])
							dhtIndex += 1
							continue
						elif key == "dht" and dhtIndex == 3:
							#dhtFlop = True
							continue
						for data in dict[key]:
							if round(data[0]) == round(t):
								data_row.append(data[1])

					csvWriter.writerow(data_row)
				csvWriter.writerow(" ")
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
			# TODO maybe make it so that it's all automatic after a copy is executed? Idk
			print("You used Makerhawk for energy logging")
			print("Get ready to move your volts and amps files over to your source dir")
			confirm = input("Press enter when you've finished importing the Volts and Watts csv's.....")
			ampsFile = input("Please enter the name of your Amps File: ")
			voltsFile = input("Please enter the name of your Volts File:" )
			print("Compiling data from " + ampsFile + " and " + voltsFile)
			self.makerhawk = MakerHawk(ampsFile, voltsFile)
			self.makerhawk.compile_energy()
			self.makerhawk.print_data()
		else:
			return
		return
	def combine_energy_data(self):
		return

# End Builder

class TimeLog:
# Start TimeLog
	time_set = []

	def __init__(self, timeInterval):
		self.timeInterval = timeInterval

	def log(self):
		while continueLogging:
			self.time_set.append(float(time.time()))
			time.sleep(self.timeInterval)
		return

	def start_logging(self):
		self.thread.start()

	def build_logger(self):
		self.thread = threading.Thread(target=self.log, name="TimeLogger")

	def rebuild_logger(self,runNumber):
		self.thread = threading.Thread(target=self.log, name="TimeLogger"+str(runNumber))
		self.time_set.clear()

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
		self.cpu = CPUTemperature()

	def log(self):
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
		return

	def start_logging(self):
		self.thread.start()

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
		self.dhtInterval = 3

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

	def build_logger(self):
		self.thread = threading.Thread(target=self.log, name="LoadLogger")
	def rebuild_logger(self,runNumber):
		self.thread = threading.Thread(target=self.log, name="LoadLogger"+str(runNumber))
		self.load_data_set.clear()

	def print_data(self):
		print("==========LOAD==========")
		print("Success: " + str(self.success) + " Failures: " + str(self.failure))
		print("Measures: ")
		print(self.load_data_set)

	def get_data_set(self):
		return self.load_data_set

# End LoadLog

class MakerHawk:
# Start MakerHawk
	hawk_data_set = {}
	# Data stored somethig like "[(tick, first, second), (t,f,s),...]

	def __init__(self, ampsFile, voltsFile, source):
		self.ampsFile = ampsFile
		self.voltsFile = voltsFile
		self.source = source
		return

	def compile_energy(self):
		self.gather_averaged_amps()
		self.gather_averaged_volts()
		self.gather_averaged_watts()
		return

	def gather_averaged_amps(self):
		amps_list = []
		with open(self.ampsFile, 'r') as amps:
			lineCount = 0
			ampsReader = csv.DictReader(amps)
			for measure in ampsReader:
				if lineCount == 0:
					lineCount+=1
					continue
				avgIndex = 0
				avgAmps = 0.0
				while avgIndex < energyInterval:
					avgAmps += measure[1]
					avgIndex += 1
				amps_list.append(avgAmps / energyInterval)
		self.hawk_data_set['amps'] = amps_list
		return

	def gather_amps(self):
		amps_list = []
		with open(self.ampsFile, 'r') as amps:
			lineCount = 0
			ampsReader = csv.DictReader(amps)
			for measure in ampsReader:
				if lineCount == 0:
					lineCount+=1
					continue
				amps_list.append(avgAmps)
		self.hawk_data_set['amps'] = amps_list
		return

	def gather_averaged_volts(self):
		voltsAvg = 0.0
		voltsSum = 0.0
		voltsCount = 0
		with open(self.voltsFile, 'r') as volts:
			lineCount = 0
			voltsReader = csv.DictReader(volts)
			for measure in voltsReader:
				if lineCount == 0:
					lineCount+=1
					continue
				voltsSum += measure[1]
				voltsCount += 1
		self.hawk_data_set['volt'] = (voltsSum / voltsCount)
		return

	def gather_averaged_watts(self):
		watts_list = []
		for amps in self.hawk_data_set['amps']:
			watts_list.append(amps * self.hawk_data_set['volts'])
		self.hawk_data_set['watt'] = watts_list
		return

	def print_data(self):
		print("==========HAWK ENERGY==========")
		for key in self.hawk_data_set:
			print(key + "======")
			print(self.hawk_data_set[key])

	def get_data_set(self):
		return self.hawk_data_set

# End MakerHawk

### Functions
##
#

### Main Execution
##
#

builder = Builder()

if runConfig:
	builder.read_config()
else:
	builder.get_configs()

builder.read_params()

#builder.build_source_code()

#builder.build_loggers()

#builder.test()
#builder.run_loggers()

#if runClean:
#	builder.data_to_csv()
#else:
#	builder.print_data_list()

if runEnergyLog:
	builder.gather_energy_data()
	builder.makerhawk.print_energy()
# string control = ""
# while control is not "quit"
# loop and permutate asking for next permutaion
# if it is quit end looping
# if we have said to clean the data, clean the resultant data store in "/Results/"

