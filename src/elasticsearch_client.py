from elasticsearch import Elasticsearch
from github_fetch_issues import fetch_issues

client = Elasticsearch("http://localhost:9200")

if not client.indices.exists(index="github_issues"):
    client.indices.create(index='github_issues', settings={
        "number_of_shards":1,
        "number_of_replicas":0,
    },
    mappings={
            "properties": {
                "id": {"type": "long"},
                "number": {"type": "integer"},
                
                "title": {"type": "text"},
                "body": {"type": "text"},

                "labels": {"type": "keyword"},

                "comments_url": {"type": "keyword"},
                "html_url": {"type": "keyword"},
                "state": {"type": "keyword"},
                "locked": {"type": "boolean"},
                "repository": {"type": "keyword"},
                "author_id": {"type": "long"},
                "author_name": {"type": "keyword"},
                "author_url": {"type": "keyword"},

                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
                "closed_at": {"type": "date"},

                "comments": {"type": "integer"},
            }
        })


for data in fetch_issues():
    treated_json = {
    "id" : data["id"],
    "body" : data["body"],
    "number": data["number"],
    "title": data["title"],
    "comments_url":  data["comments_url"],
    "html_url":  data["html_url"],
    "state":  data["state"],
    "locked":  data["locked"],
    "repository":  "apache/airflow",
    "created_at":  data["created_at"],
    "updated_at":  data["updated_at"],
    "closed_at":  data["closed_at"],
    "comments":  data["comments"],
    "author_name":  data["user"]["login"],
    "author_id":   data["user"]["id"],
    "author_url":  data["user"]["url"],
    "labels": [item["name"] for item in data["labels"]]

    }

    client.index(index='github_issues', id=treated_json["id"], document=treated_json)








res = client.search(
index="github_issues",
size = 1,
query= {
    'match_all' : {}
},
)

print(res)
