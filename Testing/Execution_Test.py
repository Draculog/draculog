

## TODO copy this into the main program for execution section

import os
import subprocess
import sys

minSize = 50000
maxSize = 200000
step = 50000
algorithms = ["b", "i", "f", "s"]
compiler = "python3"

# For Each Submission, Loop for Each size variation
for size in range(minSize, (maxSize + step), step):
    # For Each Submission of n size variation loop for each algorithm
    for algo in algorithms:
        command = [compiler, "helloworld.py", str(size), algo]
        output = None
        try:
            output = subprocess.run(command, timeout=10, capture_output=True, text=True)
        #      stdout=subprocess.DEVNULL
        except subprocess.TimeoutExpired:
            print("Failed Execution, Timed out")
        if output.returncode != 0:
            print("Error occurred, error is " + output.stderr)
            continue

        print(output.stdout, end="")

sys.exit()
