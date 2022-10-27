import os
import sys
import requests
import json

jsonResultFile = "Downloaded_Code/Submission_3_Executed-1660774833/Results.json"

FrankenWebApiBase = " https://d62e-73-231-117-15.ngrok.io/api/"
downloadToken = "code/getUncompiledCode"
## /code/getUncompiledCode
## /submission/uploadResults
## /code/$id_number
uploadToken = "submission/uploadResults"
headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {0}'.format(""),
           'user-agent': 'Mozilla/5.0',
           'Accept': 'text/plain',
           'ngrok-skip-browser-warning': 'True'}  # This final header bit is for ngrok ONLY

response = None
# headers = {'Content-type': 'application/json',
#            'Accept': 'text/plain'}
apiCall = '{0}{1}'.format(FrankenWebApiBase, uploadToken)
jsonObj = json.loads(open(jsonResultFile, 'r+').read())

# files = {"results": open(jsonResultFile, 'rb')}

try:
    response = requests.post(apiCall, json=jsonObj, headers=headers)
    # print(response.text)
except requests.exceptions.HTTPError as e:
    print("HTTP ERROR")
    print(e)
    response.close()
if response.status_code == 200:
    print("SUCCESS")
    response.close()
else:
    print("OTHER ERROR")
    response.close()
