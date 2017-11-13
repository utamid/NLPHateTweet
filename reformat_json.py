import json

with open('data.json', 'r') as fin:
    data = json.loads(fin.read())

with open('readable_data.json', 'wb') as fout:
    fout.write(json.dumps(data, indent=2).encode('utf-8'))
