# Python program to read
# json file
 
import json
import base64
import zlib
 
# Opening JSON file
f = open('data-sample.json')
 
# returns JSON object as 
# a dictionary
data = json.load(f)

# Car Data
carData = zlib.decompress(base64.b64decode(data["R"]["CarData.z"]), -zlib.MAX_WBITS)
carData = json.loads(carData)
print(json.dumps(carData))

# Position Data
posData = zlib.decompress(base64.b64decode(data["R"]["Position.z"]), -zlib.MAX_WBITS)
posData = json.loads(posData)
print(json.dumps(posData))