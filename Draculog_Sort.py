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
import Draculog_Executor as de


class DraculogSort:
  def __init__(self):
    logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    self.BaseDirectory = "cst238"
    self.CopyFiles = ["main.cpp", "mysorts.h", "Makefile"]

  # will build the code in the given directory
  # after copying the necessary files
  # will throw an exception if the target directory does not exist
  def buildCode(self, destinationDirectory):
    logging.debug("copying base files from " + self.BaseDirectory + " to " + destinationDirectory)


    # verify that the destination directory exists
    if not os.path.isdir(destinationDirectory):
      raise Exception("Attempting to copy to directory '" + destinationDirectory + ",' which doesn't exist")

    # verify that the source directory for the base files exist
    if not os.path.isdir(self.BaseDirectory):
      raise Exception("Attempting to copy from directory '" + self.BaseDirectory + "', which doesn't exist")

    # copy each file
    for file in self.CopyFiles:
      src = self.BaseDirectory + "/" + file
      if not os.path.exists(src):
        raise Exception("Attempting to copy file '" + src + "', which doesn't exist")
      shutil.copy2(src, destinationDirectory)

    logging.debug("  copying successful")
     
    logging.debug("starting build process")
    built = subprocess.run("cd " + destinationDirectory + " && make", shell=True, capture_output=True, text=True)
    if built.returncode != 0:
      status = 1
      de.Compile_To_Json(de.Compile_Headed_Data(destinationDirectory, status, built.stderr, "Failed-Compilation"), destinationDirectory)
      logging.error("failed to compile " + destinationDirectory + ": " + built.stderr)
    logging.debug("starting build process")
 
if __name__ == "__main__":
  ds = DraculogSort()
  ds.buildCode("Source/test238")
