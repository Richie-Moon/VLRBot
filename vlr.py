import requests
import json

# print(requests.get('https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/ap/000b645d-1e8f-5e9e-8cbd-3cbebb34a00e').text)

print(json.loads(requests.get('https://api.henrikdev.xyz/valorant/v3/matches/ap/csa/000?filter=competitive').text)['data'][0])


# 000b645d-1e8f-5e9e-8cbd-3cbebb34a00e
