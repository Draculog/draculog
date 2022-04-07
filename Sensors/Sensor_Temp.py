

import threading
import time

import psutil

from Sensors.Sensor import GlobalSensorValues as Globe

class Temperature:
    def __init__(self, name="Temp", interval=Globe.interval, organizeMe=True):
        self.interval = interval
        self.name = "Sensor-" + name
        self.thread = None
        self.data = []
        self.success = 0
        self.failure = 0
        self.cpuTemp = 0.0
        self.organizeMe = organizeMe
        return

    def Call_Me(self):
        print("Hi, I'm " + self.name + " running at " + self.interval)
        return

    def Build_Logger(self, function=None):
        if function is None:
            print("error: No function argument was passed, returning without building a logger.")
            return
        self.thread = threading.Thread(target=function, name=self.name)
        return

    def Start_Logging(self):
        self.thread.start()
        return

    def Log(self):
        self.cpuTemp = 0.0
        while Globe.continueLogging:
            try:
                # Grabs sensors, then the CPU specific temp, then PKG temp, then temp
                cpuTemp = psutil.sensors_temperatures()['coretemp'][0][1]
            except RuntimeError:
                self.failure += 1
                self.cpuTemp = 0.0
                pass
            this_time = time.time()
            if self.cpuTemp is not None:
                self.success += 1
            else:
                self.failure += 1
                self.cpuTemp = 0.0
            self.data.append((float(this_time), self.cpuTemp))
            time.sleep(self.interval)
        return

    def End_Logging(self):
        data_copy = self.data.copy()
        self.data.clear()
        self.thread.join()
        return data_copy

    def Get_Data(self):
        return self.data

    def Print_Data(self):
        print("==========Temperature==========")
        print("Success: " + str(self.success) + " Failures: " + str(self.failure))
        print("Measures: ")
        print(self.data)
        return
