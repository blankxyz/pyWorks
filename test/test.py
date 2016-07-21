import json
import tempfile

data = [{'a': 'A', 'b': (2, 4), 'c': 3.0}]

f = open('1.json', mode='w+')
json.dump(data, f)
f.flush()
f.seek(0)
jstr =  open(f.name, 'r').read()

print json.load(f)
