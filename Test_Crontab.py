import os
import sys
from datetime import datetime as dt
import pytz
#WEST_COAST = pytz.timezone("Pacific Coast")

if os.path.isfile("Crontab_Test.txt"):
	file = open("Crontab_Test.txt", "a+")
else:
	file = open("Crontab_Test.txt", "w+")

file.write("Crontab ran @ " + str(dt.now()) + "\n")

sys.exit(0)
