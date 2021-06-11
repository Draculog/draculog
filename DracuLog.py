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
# Imports for external attachments
import adafruit_dht
import gpiod
import board


### Global Variables
##
# Basic Global Variables
basetemp = 55 # Warm up to here, cool down to here

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



### Functions
##
#

def WarmUp():
	print("Warm Up")
	return

def CoolDown():
	print("Cool Down")
	return

def CpuTempLog():
	print("CPU LOG")
	time.sleep(cpuInterval)
	return

def DhtTempLog():
	print("DHT LOG")
	time.sleep(dhtInterval)
	return

def EnergyLog():
	print("ENERGY LOG")
	return

def LoadLog():
	print("LOAD LOG")
	return

def Cleaner():
	print("CLEANER")
	return;


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


### Main Execution
##
#


# string control = ""
# while control is not "quit"
# loop and permutate asking for next permutaion
# if it is quit end looping
# if we have said to clean the data, clean the resultant data store in "/Results/"
