import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github+json",
}

if token:
    headers["Authorization"] = f"Bearer {token}"

def fetch_issues():

    page=1
    all_issues=[]

    while True:
        url = "https://api.github.com/repos/apache/airflow/issues"
        params={
            "state": "all",
            "per_page": 100,
            "sort": "created",
            "direction": "desc",
            "page": page,
        }
        
        try:
            r=requests.get(url
                , params=params, headers=headers,     )
            r.raise_for_status()
        except Exception as e:
            print(e)
            break

        for item in r.json():
            if "pull_request" not in item:
                all_issues.append(item)
    
        if "next" not in r.links:
            break
    
        page = page + 1

    return all_issues


if __name__ == "__main__":
    issues = fetch_issues()