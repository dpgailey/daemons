from __future__ import print_function
import requests, json

rpcPort = 8332
rpcUser = <insert user> #'jamiecus'
rpcPassword = <insert password> #'gabpam24'
serverURL = 'http://' + rpcUser + ':' + rpcPassword + '@localhost:' + str(rpcPort)

headers = {'content-type': 'application/json'}
payload = json.dumps({"method": 'getblockhash', "params": ["150000"], "jsonrpc": "2.0"})
response = requests.get(serverURL, headers=headers, data=payload)

print(response.json()['result'])
