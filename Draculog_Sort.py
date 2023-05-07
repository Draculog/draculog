# this file will contain the callback code for Joshua Gross's C++ homework 
# assignment (HW11 in CST238 at CSUMB)
# It will have at least three methods:
# 1. A method that, given a path to a student's source code, will 
#    necessary files (header, Makefile, and run program) and build the code
# 2. A method that will return a list of parameter combinations to run
# 3. A method that will clean up the code

import logging
import os
import shutil
import subprocess
import time
from collections import OrderedDict

from Draculog_ModularExec import DraculogRunner


class DraculogSort:
    def __init__(self):
        logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s',
                            level=logging.DEBUG)
        self.BaseDirectory = "cst238-sort"
        self.CopyFiles = ["main.cpp", "mysorts.h", "Makefile"]
        self.ParamDict = OrderedDict()
        self.Executable = "sort"
        self.CurrentUserDir = ""
        self.TimeoutSeconds = 1000
        self.AlgorithmList = ("bubble", "insertion", "fastinsertion", "selection")
        # not all sorts implemented yet
        # self.AlgorithmList = ("bubble", "insertion", "fastinsertion", "selection", "heap", "merge", "quick")
        self.SizeList = range(40000, 50001, 10000)
        self.TimeoutSeconds = 1000
        self.drac = DraculogRunner(self)

    # will build the code in the given directory
    # after copying the necessary files
    # will throw an exception if the target directory does not exist
    def buildCode(self, userDirectory):
        self.CurrentUserDir = userDirectory
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
            self.drac.Compile_To_Json(
                self.drac.Compile_Headed_Data(userDirectory, status, built.stderr, "Failed-Compilation"),
                userDirectory)
            logging.error("failed to compile " + userDirectory + ": " + built.stderr)
        logging.debug("ending build process")

    # get a list of execution combinations, which are the keys to the actual
    # execution string
    def get_algorithms(self):
        return self.AlgorithmList

    def execute(self, algorithm):
        algo_data = {
            "algorithmName": algorithm,
            "sizeRun": []
        }

        output = None

        start_time = time.time()
        # TODO Spin up other thread to wait X time for seg faults
        try:
            for size in self.SizeList:
                # start the sensors
                self.drac.StartSensors()

                # construct the command
                commands = "./%s/%s %s %s" % (self.CurrentUserDir, self.Executable, size, algorithm)

                # run the code
                start_time, end_time, status, output = self.drac.Execute_User_Code(commands,
                                                                                   self.TimeoutSeconds,
                                                                                   0)

                # shut down the sensors and store the results
                size_run_data = self.drac.compile_results(self.CurrentUserDir,
                                                          commands,
                                                          size,
                                                          start_time,
                                                          end_time,
                                                          status,
                                                          output)
                algo_data["sizeRun"].append(size_run_data)

        except subprocess.TimeoutExpired:
            self.drac.FrankenWeb.Log_Time("ERROR-CODE-*-\tDownloaded code timed out", time.time())
            status = 4

        if output.returncode != 0:
            self.drac.FrankenWeb.Log_Time("ERROR-CODE-*-\tDownloaded code error-ed out", time.time())
            status = 2

        end_time = time.time()
        return algo_data

    def validate_output(self, output):
        results_string = output.stdout.split()
        if 'sorted:' not in results_string:
          return False
        elif results_string[results_string.index("sorted:") + 1] != "true":
          return False
        else:
          return True
      

    def run(self):
        self.drac.run()


if __name__ == "__main__":
    ds = DraculogSort()
#    ds.buildCode("Source/test_238")
    ds.run()
