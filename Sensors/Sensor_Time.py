

import threading
import time

from Sensors.Sensor import GlobalSensorValues as Globe

class Time:
    def __init__(self, name="Time", interval=Globe.interval, organizeMe=True):
        self.interval = interval
        self.name = "Sensor-" + name
        self.thread = None
        self.data = []
        self.success = 0
        self.failure = 0
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
        while Globe.continueLogging:
            self.data.append(float(time.time()))
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
        print("==========Time==========")
        print("Measures: ")
        print(self.data)
        return
