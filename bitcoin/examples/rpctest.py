from __future__ import print_function
import requests, json

rpcPort = 8332
rpcUser = 'jamie'
rpcPassword = 'gabpam24'
serverURL = 'http://localhost:' + str(rpcPort)

headers = {'content-type': 'application/json'}
payload = json.dumps({"method": 'getblockhash', "params": ["0"], "jsonrpc": "2.0"})
response = requests.get(serverURL, headers=headers, data=payload)

print(response.json()['result'])
