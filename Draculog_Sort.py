# this file will contain the callback code for Joshua Gross's C++ homework 
# assignment (HW11 in CST238 at CSUMB)
# It will have at least three methods:
# 1. A method that, given a path to a student's source code, will 
#    necessary files (header, Makefile, and run program) and build the code
# 2. A method that will return a list of parameter combinations to run
# 3. A method that will clean up the code

import sys
import os
import shutil
import logging
import subprocess
import Draculog_ModularExec as de
from collections import OrderedDict

class ParamSet:
  def __init__(self, algorithm, size, executionString):
    self.algorithm = algorithm
    self.size = size
    self.executionString = executionString

  def algorithm(self):
    return self.algorithm

  def size(self):
    return self.size

  def executionString(self):
    return self.executionString
    

class DraculogSort:
  def __init__(self):
    logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    self.BaseDirectory = "cst238-sort"
    self.CopyFiles = ["main.cpp", "mysorts.h", "Makefile"]
    self.ParamDict = OrderedDict()
    self.Executable = "sort"
    self.CurrentUserDirectory = ""
    self.TimeoutSeconds = 1000
    for sort in ("bubble", "insertion", "fastinsertion", "selection", "heap", "merge", "quick"):
      for size in range(10000, 50001, 10000):
        self.ParamDict[sort + "-" + str(size)] = ParamSet(sort, size, "sort " + str(size) + " false")

  # will build the code in the given directory
  # after copying the necessary files
  # will throw an exception if the target directory does not exist
  def buildCode(self, userDirectory):
    self.CurrentUserDirectory = userDirectory
    logging.debug("copying base files from " + self.BaseDirectory + " to " + userDirectory)


    # verify that the destination directory exists
    if not os.path.isdir(userDirectory):
      raise Exception("Attempting to copy to directory '" + userDirectory + ",' which doesn't exist")

    # verify that the source directory for the base files exist
    if not os.path.isdir(self.BaseDirectory):
      raise Exception("Attempting to copy from directory '" + self.BaseDirectory + "', which doesn't exist")

    # copy each file
    for file in self.CopyFiles:
      src = self.BaseDirectory + "/" + file
      if not os.path.exists(src):
        raise Exception("Attempting to copy file '" + src + "', which doesn't exist")
      shutil.copy2(src, userDirectory)

    logging.debug("  copying successful")
     
    logging.debug("starting build process")
    built = subprocess.run("cd " + userDirectory + " && make", shell=True, capture_output=True, text=True)
    if built.returncode != 0:
      status = 1
      de.Compile_To_Json(de.Compile_Headed_Data(userDirectory, status, built.stderr, "Failed-Compilation"), userDirectory)
      logging.error("failed to compile " + userDirectory + ": " + built.stderr)
    logging.debug("ending build process")

  # get a list of execution combinations, which are the keys to the actual 
  # execution string
  def getParamDict(self):
    return self.ParamDict

  def execute(self, status, params):
    output = None
    start_time = time.time()
    if status == 0 or status:
        # TODO Spin up other thread to wait X time for seg faults
        try:
            commands = "./%s/%s %s" % (self.CurrentUserDirectory, self.Executable, params)
            output = subprocess.run(commands, shell=True, timeout=timeoutSeconds, capture_output=True, text=True)
            # , stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) # Old Flags
        except subprocess.TimeoutExpired:
            FrankenWeb.Log_Time("ERROR-CODE-*-\tDownloaded code timed out", time.time())
            status = 4

    if output.returncode != 0:
        FrankenWeb.Log_Time("ERROR-CODE-*-\tDownloaded code error-ed out", time.time())
        status = 2

    end_time = time.time()
    SensorGlobe.continueLogging = False
    return start_time, end_time, status, output
    
 
if __name__ == "__main__":
  ds = DraculogSort()
  ds.buildCode("Source/test_238")
