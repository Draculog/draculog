import sys

import pyRAPL
from datetime import datetime as dt
import os

try:
    from Sensor import GlobalSensorValues as Globe
    from Sensor import SensorThread
except ModuleNotFoundError as e:
    from Sensors.Sensor import GlobalSensorValues as Globe
    from Sensors.Sensor import SensorThread

class PyRAPL:
    def __init__(self, name="PyRAPL", interval=Globe.interval, organizeMe=True):
        super().__init__()
        self.thread = None
        self.interval = interval
        self.name = "Sensor-" + name
        self.meter = None
        self.data = None
        self.organizeMe = organizeMe
        try:
            pyRAPL.setup(devices=[pyRAPL.Device.PKG])
        except PermissionError:
            print("ERROR-*-\tPyRAPL Doesn't have the permissions it needs" + str(dt.now()))
            print("ERROR-^-\tExecuting the following Command:")
            print("ERROR-^-\t'sudo chmod -R a+r /sys/class/powercap/intel-rapl'")
            try:
                os.system("sudo chmod -R a+r /sys/class/powercap/intel-rapl")
            except Exception:
                print("FATAL-*-\tPyRAPL is not currently working, please consult documentation")
                sys.exit(1)
        return

    def Call_Me(self):
        print("Hi, I'm " + self.name + " running at ", self.interval)
        return

    def Build_Logger(self):
        # if Globe.IsOnLaptop:
        #    return None
        self.meter = pyRAPL.Measurement(self.name)
        # For integration into main execution
        # self.thread = SensorThread()
        self.data = None
        return

    def Start_Logging(self):
        self.meter.begin()
        return

    def Log(self):
        return self.name

    def Compile_Energy_Data(self):
        self.data = self.meter.result
        return

    def End_Logging(self):
        self.meter.end()
        self.Compile_Energy_Data()
        self.meter = None
        # data_copy = self.data.copy()
        # self.data.clear()
        return  # data_copy

    def Get_Data(self):
        return self.data.pkg[0]

    def Print_Data(self):
        print("==========Energy==========")
        for result in self.data:
            print(result)
        return
