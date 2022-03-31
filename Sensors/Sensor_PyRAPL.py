

import pyRAPL

from Sensors.Sensor import GlobalSensorValues as Globe
from Sensors.Sensor import Sensor

class PyRAPL(Sensor):
    def __init__(self, interval, name):
        super().__init__()
        self.interval = interval
        self.name = "Sensor " + name
        self.meter = None
        self.data = []
        return

    def CallMe(self):
        print("Hi, I'm " + self.name)
        return

    def Build_Logger(self, sName):
        pyRAPL.setup(devices=[pyRAPL.Device.PKG])
        self.meter = pyRAPL.Measurement(sName)
        return

    def Start_Logging(self):
        self.meter.begin()
        return

    def Log_Test(self):
        super().Log_Test()
        return

    def Compile_Energy_Data(self):
        self.data.append((float(self.meter.timestamp), self.meter.result))
        return

    def End_Logging(self):
        self.meter.end()
        del self.meter
        self.meter = None
        return

    def Get_Data(self):
        return self.data

    def Print_Data(self):
        print("==========Energy==========")
        for result in self.data:
            print(result)
        return