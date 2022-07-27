import os
import sys
from datetime import datetime as dt

if os.path.isfile("../Crontab_Test.txt"):
	file = open("../Crontab_Test.txt", "a+")
	print("I can see the file")
else:
	file = open("../Crontab_Test.txt", "w+")
	print("I can't see the file")

file.write("Crontab ran @ " + str(dt.now()) + "\n")
file.write("CWD: " + os.getcwd() + "\n")
sys.exit(0)
