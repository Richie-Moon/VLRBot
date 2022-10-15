import requests
import json

# print(requests.get('https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/ap/000b645d-1e8f-5e9e-8cbd-3cbebb34a00e').text)

data = json.loads(requests.get('https://api.henrikdev.xyz/valorant/v3/matches/ap/csa/000').text)['data'][0]
data.pop('kills')
data.pop('rounds')

print(data)


# 000b645d-1e8f-5e9e-8cbd-3cbebb34a00e
