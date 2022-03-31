

class GlobalSensorValues:
    continueLogging = False

class Sensor:
    def __init__(self):
        self.count = 0
        return

    def Log_Test(self):
        while GlobalSensorValues.continueLogging:
            self.count += 1
        return

    def Clear_Values(self):
        return