from elasticsearch_client import get_client, ingest_issues, count_documents_created_before
import argparse

# def run_ingest():
#     client = get_client()
#     index = "github_issues"
#     if not client.indices.exists(index=index):
#         client.indices.delete(index= index)

#     ingest_issues(client=client, index=index)


# def run_inspect():
#     return None

def main():
    client = get_client()
    index = "github_issues"
    if client.indices.exists(index=index):
        client.indices.delete(index= index)

    ingest_issues(client=client, index=index)


    

if __name__ == "__main__":
    main()