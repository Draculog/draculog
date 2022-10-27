import os
import sys
import requests

FrankenWebApiBase = "https://6451-73-231-117-15.ngrok.io/api/code/"
downloadToken = "getUncompiledCode"

headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {0}'.format(""),
           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
           'Accept': 'text/plain',
           'ngrok-skip-browser-warning': 'True'}

apiCall = '{0}{1}'.format(FrankenWebApiBase, downloadToken)
response = requests.get(apiCall, headers=headers)
print(response.text)