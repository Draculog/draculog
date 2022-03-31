import os
import threading
import time

from Sensors.Sensor import GlobalSensorValues as Globe
from Sensors.Sensor import Sensor

class Load(Sensor):
    def __init__(self, interval, name):
        super().__init__()
        self.interval = interval
        self.name = "Sensor " + name
        self.thread = None
        self.data = []
        self.success = 0
        self.failure = 0

        return

    def callMe(self):
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
        load = 0.0
        while Globe.continueLogging:
            try:
                load = os.getloadavg()[0]
            except IndexError or RuntimeError:
                self.failure += 1
                load = 0.0
                pass
            this_time = time.time()
            if load is not None:
                self.success += 1
            else:
                self.failure += 1
                load = 0.0

            self.data.append((float(this_time), load))
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
        print("==========LOAD==========")
        print("Success: " + str(self.success) + " Failures: " + str(self.failure))
        print("Measures: ")
        print(self.data)
        return