

import threading
import time

import psutil

try:
    from Sensor import GlobalSensorValues as Globe
except ModuleNotFoundError as e:
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
        print("Hi, I'm " + self.name + " running at ", self.interval)
        return

    def Build_Logger(self, Index, function=None):
        if function is None:
            print("error: No function argument was passed, returning without building a logger.")
            return
        self.thread = threading.Thread(target=function, name=self.name+"_"+Index)
        self.data.clear()
        return self.thread

    def Start_Logging(self):
        self.thread.start()
        return

    def Log(self):
        while Globe.continueLogging:
            # This is to catch and skip psutil errors on Danny's Laptop
            if Globe.IsOnLaptop:
                self.data.append((float(time.time()), 33.33))
                time.sleep(self.interval)
                continue
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
        return self.Get_Data()

    def Get_Data(self):
        return self.data

    def Print_Data(self):
        print("==========Temperature==========")
        print("Success: " + str(self.success) + " Failures: " + str(self.failure))
        print("Measures: ")
        print(self.data)
        return
