

import pyRAPL
from datetime import datetime as dt
import os

from Sensors.Sensor import GlobalSensorValues as Globe

class PyRAPL:
    def __init__(self, name="PyRAPL", interval=Globe.interval, organizeMe=True):
        super().__init__()
        self.interval = interval
        self.name = "Sensor-" + name
        self.meter = None
        self.data = []
        try:
		pyRAPL.setup(devices=[pyRAPL.Device.PKG])
	except PermissionError:
		print("ERROR-*-\tPyRAPL Doesn't have the permissions it needs" + str(dt.now())
		print("ERROR-^-\tExecuting the following Command:")
		print("ERROR-^-\tsudo chmod -R a+r /sys/class/powercap/intel-rapl")
		os.system("sudo chmod -R a+r /sys/class/powercap/intel-rapl")

	self.organizeMe = organizeMe
        return

    def CallMe(self):
        print("Hi, I'm " + self.name + " running at " + self.interval)
        return

    def Build_Logger(self, function):
        sName = function()
        self.meter = pyRAPL.Measurement(sName)
        return

    def Start_Logging(self):
        self.meter.begin()
        return

    def Log(self):
        return self.name

    def Compile_Energy_Data(self):
        self.data.append(self.meter.result)
        return

    def End_Logging(self):
        self.meter.end()
        self.Compile_Energy_Data()
        self.meter = None
        data_copy = self.data.copy()
        self.data.clear()
        return data_copy

    def Get_Data(self):
        return self.data[0]

    def Print_Data(self):
        print("==========Energy==========")
        for result in self.data:
            print(result)
        return
