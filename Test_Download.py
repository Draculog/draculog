import os
import sys

from Draculog import SharedDraculogFunctions
GreenCode = SharedDraculogFunctions()

folder = "Testing"

if os.path.isdir(folder):
    print("I can see the test folder")
else:
    print("I can't see the test folder")
    os.mkdir(folder)

print(GreenCode.Download_From_GreenCode())
