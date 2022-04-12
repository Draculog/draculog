

class GlobalSensorValues:
    IsOnLaptop = True
    continueLogging = False
    interval = 2

import time

class SensorThread:
    def __init__(self):
        return

    def join(self):
        while GlobalSensorValues.continueLogging:
            time.sleep(1)
        return