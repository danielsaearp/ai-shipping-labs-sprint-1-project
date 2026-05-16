from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from github_fetch_issues_v2 import fetch_issues
from datetime import datetime, timezone

now = datetime.now(timezone.utc)


client = Elasticsearch("http://localhost:9200")

input_date = "2026-05-16 04:54:19"

dt = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
dt = dt.replace(tzinfo=timezone.utc)

elastic_date = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

client.count(
      index="new_index_v2",
      query={
          "range": {
              "created_at": {
                  "lt": elastic_date
              }
          }
      }
    )["count"]