import sys
from datetime import datetime as dt
import os

try:
    from Sensor import GlobalSensorValues as Globe
except ModuleNotFoundError as e:
    from Sensors.Sensor import GlobalSensorValues as Globe

def Dummy_Switch(data_to_dumb_down):
    if data_to_dumb_down == "Time":
        final_data = [69.69, 420.420, 69.69]
    elif data_to_dumb_down == "Temp":
        final_data = [(1, 69.69), (2, 420.420), (3, 69.69)]
    elif data_to_dumb_down == "Load":
        final_data = [(1, 69.69), (2, 420.420), (3, 69.69)]
    elif data_to_dumb_down == "PyRAPL":
        final_data = 69420.69
    else:
        final_data = 69420.69
    return final_data

class Dummy:
    def __init__(self, name="Dummy", interval=Globe.interval, organizeMe=False, threadMe=False, data_to_dumb_down="PyRAPL"):
        super().__init__()
        self.data_to_dumb_down = data_to_dumb_down
        self.threadMe = threadMe
        self.thread = None
        self.interval = interval
        self.name = "Sensor-" + name
        self.data = None
        self.organizeMe = organizeMe

        self.final_data = Dummy_Switch(data_to_dumb_down)
        return

    def Call_Me(self):
        print("Hi, I'm " + self.name + " running at ", self.interval)
        return

    def Build_Logger(self):
        self.data = None
        return

    def Start_Logging(self):
        return

    def Log(self):
        return self.name

    def Compile_Energy_Data(self):
        self.data = self.final_data
        return

    def End_Logging(self):
        self.Compile_Energy_Data()
        return

    def Get_Data(self):
        return self.data

    def Get_Carbon(self):
        return self.data

    def Print_Data(self):
        print("==========Dummy==========")
        print(self.data)
        return
