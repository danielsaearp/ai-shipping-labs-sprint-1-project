from elasticsearch import Elasticsearch
import requests
import json

client = Elasticsearch("http://localhost:9200")

with open('src/example.json', 'r') as file:
    data=json.load(file)

#client.index(index='test', document=data)

res = client.search(
index="test",
size = 1,
query= {
    'match_all' : {}
},
)

print(res)