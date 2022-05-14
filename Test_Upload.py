import os
import sys

from Draculog import SharedDraculogFunctions
GreenCode = SharedDraculogFunctions()

file = "Results.json"

if os.path.isfile(file):
    print("I can see the results example file")
else:
    print("I can't see the results example file")
    sys.exit(1)

# import requests as req

# print("Attempting a request call")
# os.environ['NO_PROXY'] = '127.0.0.1'
# resp = req.get("https://127.0.0.1:3000/code/notCompiled")
# print(resp)

if GreenCode.Upload_To_GreenCode(file):
    print("Upload did not fail")
else:
    print("Upload Failed")
