import os
from typing import Any

import requests
from dotenv import load_dotenv


BASE_URL = "https://api.github.com/repos/apache/airflow/issues"
PER_PAGE = 100
TIMEOUT_SECONDS = 30


def build_headers() -> dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github+json",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def fetch_open_issue_page(
    url: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
) -> requests.Response:
    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=TIMEOUT_SECONDS,
    )

    if response.status_code != 200:
        print(f"GitHub request failed with status {response.status_code}")
        print(response.text)
        response.raise_for_status()

    return response


def is_issue(item: dict[str, Any]) -> bool:
    return "pull_request" not in item


def fetch_open_issues() -> list[dict[str, Any]]:
    headers = build_headers()
    url = BASE_URL
    params = {
        "state": "open",
        "per_page": PER_PAGE,
        "sort": "created",
        "direction": "desc",
    }

    all_issues = []
    page_count = 0

    while True:
        response = fetch_open_issue_page(url, headers, params)
        data = response.json()

        if not isinstance(data, list):
            raise TypeError(f"Expected a list from GitHub, got {type(data).__name__}")

        page_count += 1
        issues_on_page = [item for item in data if is_issue(item)]
        all_issues.extend(issues_on_page)

        print(
            f"Fetched page {page_count}: "
            f"{len(data)} items, {len(issues_on_page)} issues"
        )

        next_link = response.links.get("next")
        if not next_link:
            break

        url = next_link["url"]
        params = None

    print(f"Total pages fetched: {page_count}")
    return all_issues


def main() -> None:
    load_dotenv()

    issues = fetch_open_issues()

    print(f"Total open issues: {len(issues)}")
    for issue in issues[:5]:
        print(f"#{issue['number']} {issue['title']}")


if __name__ == "__main__":
    main()
