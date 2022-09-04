import requests
import json

data = requests.get('https://vlrggapi.vercel.app/match/results').text
print(data)

json_data = json.loads(data)

try:
    if json_data['Error'] == '500':
        print("Internal Server Error at VLR.gg/API Endpoint.")
except KeyError:
    json_data = json.loads(data)['data']
    print(json_data['segments'])



