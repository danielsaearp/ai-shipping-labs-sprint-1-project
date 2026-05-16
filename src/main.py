from elasticsearch_client import get_client, ingest_issues
import argparse
import random

def run_ingest(index, mode, since):
    client = get_client()
    ingest_issues(client=client, index=index, mode=mode, since=since)


def run_inspect(index):
    client = get_client()
    
    if not client.indices.exists(index=index):
        print(f"Index: {index}\nExists: no\nRun ingest first to create and populate it")
        return None
    else:
        count = client.count(index= index)['count']
        if count == 0:
            print(f"Index: {index}\nExists: yes\nDocuments: {count}\nSample issue: n/a")
        else:
            response = client.search(
            index=index,
            query={
                "function_score": {
                    "query": {"match_all": {}},
                    "random_score": {
                        "seed": random.randint(1, 10_000_000),
                        "field": "_seq_no"
                    }
                }
            },
            _source=True,
            size=1
            )
            hit = response["hits"][ "hits"][0]
            source = hit["_source"]
            random_number = source["number"]
            title = source["title"]
            print(f"Index: {index}\nExists: yes\nDocuments: {count}\nSample issue: #{random_number} - {title}")


def main():
    parser = argparse.ArgumentParser(description='a cli for inspecting and ingesting issues from github into elasticsearch.')
    parser.add_argument("command", choices=["ingest", "inspect"])
    parser.add_argument("index", help="the index name to be created or inspected" )
    parser.add_argument("mode", nargs="?", choices=["full_load", "backfill", "incremental_load"])
    parser.add_argument("--since", help="fetch issues updated since this timestamp")

    args = parser.parse_args()

    if args.command == "ingest":
        if not args.mode:
            parser.error("ingest requires a mode: full_load, backfill, or incremental_load")
        if not args.since and args.mode=="backfill":
            parser.error("ingest backfill requires a since date in the format YYYY-MM-DD HH:MM:SS")
        if args.mode in ["full_load", "incremental_load"] and args.since:
            parser.error("ingest full_load and incremental_load accept no since argument")
        run_ingest(args.index, args.mode, args.since)
    
    elif args.command == "inspect":
        run_inspect(args.index)

    

if __name__ == "__main__":
    main()