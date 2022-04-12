

import threading
import time

try:
    from Sensor import GlobalSensorValues as Globe
except ModuleNotFoundError as e:
    from Sensors.Sensor import GlobalSensorValues as Globe

class Time:
    def __init__(self, name="Time", interval=Globe.interval, organizeMe=True, threadMe=True):
        self.interval = interval
        self.name = "Sensor-" + name
        self.thread = None
        self.data = []
        self.success = 0
        self.failure = 0
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
            thisTime = time.time()
            self.data.append(float(thisTime))
            time.sleep(self.interval)
        return

    def End_Logging(self):
        return self.Get_Data()

    def Get_Data(self):
        return self.data

    def Print_Data(self):
        print("==========Time==========")
        print("Measures: ")
        print(self.data)
        return

if __name__ == '__main__':
    myTime = Time()
    myTime.test = True
    myTime.Build_Logger(function=myTime.Log)
    print("Testing Logging Functions")
    Globe.continueLogging = True
    myTime.Start_Logging()
    time.sleep(10)
    Globe.continueLogging = False
    result = myTime.End_Logging()
    print("Ending Logging Functions")
    print(result)
