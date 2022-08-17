import Sensors.Sensor_PyRAPL
import time
PyRAPL = Sensors.Sensor_PyRAPL.PyRAPL()

PyRAPL.Build_Logger()
PyRAPL.Start_Logging()
time.sleep(10)
PyRAPL.End_Logging()
print(PyRAPL.Get_Data())