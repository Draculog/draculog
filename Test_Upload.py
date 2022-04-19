import os
import sys

from Draculog import SharedDraculogFunctions
GreenCode = SharedDraculogFunctions()

file = "Results.json"

if os.path.isfile(file):
    print("I can see the results example file")
else:
    print("I can't see the results example file")

if GreenCode.Upload_To_GreenCode(file):
    print("Upload did not fail")
else:
    print("Upload Failed")
