

## TODO copy this into the main program for execution section

import os
import subprocess
import sys

minSize = 5000
maxSize = 20000
step = 5000
algorithms = ["b", "i", "f", "s"]
compiler = "./code"

print("Starting Execution Testing")

# For Each Submission, Loop for Each size variation
for size in range(minSize, (maxSize + step), step):
    print("Size is: " + str(size))
    # For Each Submission of n size variation loop for each algorithm
    for algo in algorithms:
        print("Algo is: " + algo)
        command = [compiler, str(size), algo]
        print("Command is " + str(command))
        output = None
        try:
            output = subprocess.run(command, timeout=1000, capture_output=True, text=True)
        #      stdout=subprocess.DEVNULL
        except subprocess.TimeoutExpired:
            print("Failed Execution, Timed out")
        if output.returncode != 0:
            print("Error occurred, error is " + output.stderr)
            continue

        print(output.stdout, end="")

sys.exit()
