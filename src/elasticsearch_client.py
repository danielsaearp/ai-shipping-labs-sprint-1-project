from elasticsearch import Elasticsearch
from github_fetch_issues import fetch_issues

def get_client():
    return Elasticsearch("http://localhost:9200")

def create_index_if_missing(client, index):
    if not client.indices.exists(index=index):
        client.indices.create(index=index, settings={
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
        print("Creating index and moving on to indexing documents")
    else:
        print("Index already exists, moving on to indexing documents")

def index_issue(index, id, document, client):
    client.index(index=index, id=id, document=document)


def transform_issue(data):
    treated_document={
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
    return treated_document


def ingest_issues(client,index):
    create_index_if_missing(client=client,index=index)
    issues = fetch_issues()

    for data in issues:
        treated_json=transform_issue(data=data)
        index_issue(index=index, id=treated_json["id"], document=treated_json, client=client)
    client.indices.refresh(index=index)

def count_documents_created_before(client,index, max_time):
    count = client.count(
      index=index,
      query={
          "range": {
              "created_at": {
                  "lt": max_time
              }
          }
      }
    )["count"]

    return count





