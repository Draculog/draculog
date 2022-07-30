import os
import sys
import subprocess

#built = os.system("cd " + "Downloaded_Code/0000/80/" + "&& make")
commands = ["./Headers/code", "10000", "i", "false"]
commandsStr = "./Headers/code" + " " + "10000" + " " + "i" + " " + "false"
built = subprocess.run(commandsStr, timeout=100, shell=True, capture_output=True, text=True)


print(built)
result = built.stdout.split()
print(result)
print(result[result.index("sorted:")+1])

#print(built.stdout.split()[7])
#print(built.stdout.split()[7].lower() == "true")
