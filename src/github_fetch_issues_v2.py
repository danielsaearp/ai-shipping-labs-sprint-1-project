import os
from datetime import datetime, timedelta, timezone
import requests
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

token = os.environ.get("GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github+json",
}

if token:
    headers["Authorization"] = f"Bearer {token}"

URL = "https://api.github.com/repos/apache/airflow/issues"
OVERLAP = timedelta(seconds=60)


def fetch_issues(since=None):
    all_issues = []
    

    with tqdm(desc="Fetching GitHub issue pages", unit=" page") as progress:
        while True:
            page = 1
            hit_cap = False
            last_updated = None

            while True:
                params = {
                    "state": "all",
                    "per_page": 100,
                    "sort": "updated",
                    "direction": "asc",
                    "page": page,
                }
                if since:
                    params["since"] = since

                try:
                    r = requests.get(URL, params=params, headers=headers)
                except requests.exceptions.RequestException:
                    raise

                if r.status_code == 422:
                    hit_cap = True
                    break

                r.raise_for_status()

                items = r.json()
                if not items:
                    break

                for item in items:
                    last_updated = item["updated_at"]
                    if "pull_request" in item:
                        continue
                    all_issues.append(item)

                progress.update(1)

                if "next" not in r.links:
                    break

                page += 1

            if not hit_cap or last_updated is None:
                # Stale-during-backfill (issues updated after we fetched them)
                # is intentionally left to a future incremental sync pass.
                return all_issues

            # Overlap by 60s so same-second issues split across the page-boundary
            # group aren't skipped; dedupe by id absorbs the refetch.
            cursor = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            next_since = (cursor - OVERLAP).strftime("%Y-%m-%dT%H:%M:%SZ")

            if next_since == since:
                return all_issues
            since = next_since

    return all_issues


if __name__ == "__main__":
    issues = fetch_issues()
    print(f"Fetched {len(issues)} issues")
