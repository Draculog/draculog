

import threading
import time

import psutil

from Sensors.Sensor import GlobalSensorValues as Globe
from Sensors.Sensor import Sensor

class Temperature(Sensor):
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
        cpuTemp = 0.0
        while Globe.continueLogging:
            try:
                # Grabs sensors, then the CPU specific temp, then PKG temp, then temp
                cpuTemp = psutil.sensors_temperatures()['coretemp'][0][1]
            except RuntimeError:
                self.failure += 1
                cpuTemp = 0.0
                pass
            this_time = time.time()
            if cpuTemp is not None:
                self.success += 1
            else:
                self.failure += 1
                cpuTemp = 0.0
            self.data.append((float(this_time), cpuTemp))
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
        print("==========Temperature==========")
        print("Success: " + str(self.success) + " Failures: " + str(self.failure))
        print("Measures: ")
        print(self.data)
        return
