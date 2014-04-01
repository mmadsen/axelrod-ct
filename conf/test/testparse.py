import json
from pprint import pprint

with open('conf/test-treestructured-axelrod.json') as data_file:    
    data = json.load(data_file)
#pprint(data)
for key, value in data.items():
    print "key: %s  value: %s" % (key, value)
