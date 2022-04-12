import os
import sys
import time
import threading
import Sensor_Time
import Sensor_Load
import Sensor_Temp
import Sensor_PyRAPL
from Sensor import GlobalSensorValues as Globe

sensor_list = [Sensor_Time.Time(), Sensor_Load.Load(), Sensor_Temp.Temperature(), Sensor_PyRAPL.PyRAPL(organizeMe=False)]
sensor_threads = []
sensor_data = []
start_time = 0
end_time = 0
index = 0

def Build_Sensor_Threads():
    global index
    print("Building all sensor threads")
    global sensor_threads
    for sensor in sensor_list:
        if not sensor.organizeMe:
                sensor.Build_Logger()
                sensor_threads.append(sensor)
                continue
        t = sensor.Build_Logger(str(index), function=sensor.Log)
        print(t.name)
        sensor_threads.append(t)
    index+=1
    print("All sensor threads built")
    return

def Start_Sensor_Threads():
    print("Starting all sensor threads")
    for t in sensor_threads:
        if t in sensor_list:
                t.Start_Logging()
                t.Call_Me()
                continue
        print(t.name)
        t.start()
    print("All sensor threads started")
    return

def Wait_For_Sensor_Threads():
    print("Waiting for all sensor threads")
    for t in sensor_threads:
        if t in sensor_list:
                t.End_Logging()
                continue
        t.join()
    print("All sensor threads done")
    time.sleep(1)
    return

def Gather_Sensor_Data():
    print("Gathering all sensor data from ", sensor_list)
    for sensor in sensor_list:
        sensor_data.append(sensor.Get_Data())
    print("All data gathered")
    return

def Function_To_Test():
    global start_time, end_time
    print("Starting Function to Test")
    # Globe.continueLogging = True
    start_time = time.time()
    count = 0
    sleepTime = 10
    for i in range(0, sleepTime):
        count += 1
        time.sleep(1)
    end_time = time.time()
    Globe.continueLogging = False
    print("Ending function to test")
    return

if __name__ == "__main__":

    # Build Sensor Threads
    Build_Sensor_Threads()
    Globe.continueLogging = True
    # Start Sensor Threads
    Start_Sensor_Threads()
    # Run function to be measured
    Function_To_Test()
    # Wait for sensor threads
    Wait_For_Sensor_Threads()
    # Gather Sensor Data
    Gather_Sensor_Data()
    # print data
    print("Start time = " + str(start_time) + ", End time = " + str(end_time) + ", Delta time = " + str(end_time - start_time))
    print("Saved Local Data")
    for data in sensor_data:
        print("Data is: ", data)
    print("Sensor Data")
    for sensor in sensor_list:
        print("Sensor Data is: ", sensor.Get_Data())

    sys.exit(0)
