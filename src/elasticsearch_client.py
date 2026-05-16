from elasticsearch import Elasticsearch
from github_fetch_issues_v2 import fetch_issues
from datetime import datetime, timezone
import json
from pathlib import Path

STATE_FILE = Path("ingestion_state.json")

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



def load_ingestion_state():
    if not STATE_FILE.exists():
        return {}
    with STATE_FILE.open() as f:
        return json.load(f)


def save_ingestion_state(state):
    with STATE_FILE.open("w") as f:
        json.dump(state, f, indent=2)


def get_last_ingest_at(index):
    state = load_ingestion_state()
    index_state = state.get(index, {})
    return index_state.get("last_ingest_at")


def save_last_ingest_at(index, last_ingest_at):
    state = load_ingestion_state()
    state[index] = {
        "last_ingest_at": last_ingest_at
    }
    save_ingestion_state(state)


def format_user_since_for_github(since):
    try:
        dt = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        dt = datetime.strptime(since, "%Y-%m-%d")
    dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def current_utc_timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")



def ingest_issues(client,index,mode,since=None):
    run_started_at = current_utc_timestamp()

    if mode == "backfill":
        create_index_if_missing(client=client,index=index)
        since = format_user_since_for_github(since)

    elif mode == "full_load":
        create_index_if_missing(client=client,index=index)
        since = None

    elif mode == "incremental_load":
        if not client.indices.exists(index=index):
            print("index does not exist, run full_load or backfill first")
            return
        since = get_last_ingest_at(index)
        if not since:
            print("no last_ingest_at found, run full_load or backfill first")
            return

    print(f"Mode: {mode}")
    print(f"GitHub since: {since or 'none'}")

    issues = fetch_issues(since=since)

    for data in issues:
        treated_json=transform_issue(data=data)
        index_issue(index=index, id=treated_json["id"], document=treated_json, client=client)
    client.indices.refresh(index=index)
    save_last_ingest_at(index, run_started_at)

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



