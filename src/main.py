from elasticsearch_client import get_client, ingest_issues
import argparse
import random

def run_ingest(index):
    client = get_client()
    ingest_issues(client=client, index=index)


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

    args = parser.parse_args()

    if args.command == "ingest":
        run_ingest(args.index)
    
    if args.command == "inspect":
        run_inspect(args.index)

    

if __name__ == "__main__":
    main()