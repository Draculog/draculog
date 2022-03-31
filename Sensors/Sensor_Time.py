

import threading
import time

from Sensors.Sensor import GlobalSensorValues as Globe
from Sensors.Sensor import Sensor

class Time(Sensor):
    def __init__(self, interval, name):
        super().__init__()
        self.interval = interval
        self.name = "Sensor " + name
        self.thread = None
        self.data = []
        self.success = 0
        self.failure = 0
        return

    def Call_Me(self):
        print("Hi, I'm " + self.name)
        return

    def Build_Logger(self, function=None):
        if function is None:
            function = self.Log_Test
        self.thread = threading.Thread(target=function, name=self.name)
        return

    def Start_Logging(self):
        self.thread.start()
        return

    def Log(self):
        while Globe.continueLogging:
            self.data.append(float(time.time()))
            time.sleep(self.interval)
        return

    def Log_Test(self):
        super().Log_Test()
        return

    def End_Logging(self):
        return

    def Get_Data(self):
        return self.data

    def Print_Data(self):
        print("==========Time==========")
        print("Measures: ")
        print(self.data)
        return