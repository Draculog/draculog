
import subprocess
import os
import time
import sys
import datetime
import energyusage
import pyRAPL

seconds=20
otherEnergy=False

if len(sys.argv) > 1:
	if 's' in sys.argv or 'short' in sys.argv:
		seconds=5
	if 'l' in sys.argv or 'long' in sys.argv:
		seconds=45
	if 'e' in sys.argv:
		otherEnergy=True

#Find a way to list all sockets
pyRAPL.setup(devices=[pyRAPL.Device.PKG])

#csv_output = pyRAPL.outputs.CSVOutput('resultTest.csv')
#meter = pyRAPL.Measurement('energy')

#report = pyRAPL.outputs.DataFrameOutput()

print("This is the pyRAPL testing script to measure power used by system to execute a variety of tasks")
#@pyRAPL.measureit(output=csv_output)
meter = pyRAPL.Measurement('bar')

def funcA(seconds):
	meter.begin()
	index=0
	for i in range(seconds):
		print("FuncA(): Waiting " + str(index) + " / " + str(seconds) + " seconds")
		time.sleep(1)
		index+=1
	meter.end()

def funcB(seconds):
	for i in range(seconds):
		print("FuncB(): Waiting " + str(index) + " / " + str(seconds) + " seconds")
		time.sleep(1)
		index+=1

print("Checking PyRAPL Pkg now....")
print("Running FuncA()....")

funcA(seconds)

print("Checking meter.result obj...")

#meter.result returns an object like class pyRAPL.Result(label, timestamp, duration, pkg=None, dram=None)
# label (str) – measurement label
# timestamp (float) – measurement’s beginning time (expressed in seconds since the epoch)
# duration (float) – measurement’s duration (in micro seconds)
# pkg (Optional[List[float]]) – list of the CPU energy consumption -expressed in micro Joules- (one value for each socket) if None, no CPU energy consumption was recorded
# dram (Optional[List[float]]) – list of the RAM energy consumption -expressed in seconds- (one value for each socket) if None, no RAM energy consumption was recorded

print("Label: " + meter.result.label)
print("Timestamp: " + str( datetime.datetime.fromtimestamp( meter.result.timestamp) ) )
print("Total time taken: " + str( datetime.timedelta(microseconds=meter.result.duration) ) + " seconds" )
print("Total energy used: " + str(meter.result.pkg[0]) + " Micro Joules")
print("Total energy used: " + str( meter.result.pkg[0] / 1000000.0 ) + " Joules")
print("Total energy used: " + str( (meter.result.pkg[0] / 1000000.0) / seconds ) + " Watt/Second" )

if otherEnergy:
	print("Checking Energy Usage Pkg now....")
	print("Running FuncB()....")

	energyusage.evaluate(funcB, 40, pdf=False, locations=["California"], year=2021)

