# Airflow GitHub Issues Ingestion

Fetch open issues from the Apache Airflow GitHub repository, transform the raw API response, and index the documents into local Elasticsearch.

This is a learning project for Python project structure, APIs, Docker, Elasticsearch, and ingestion pipelines.

## What It Does

- Fetches open issues from `apache/airflow` using the GitHub API.
- Filters pull requests out of the issues endpoint response.
- Transforms raw GitHub issue JSON into a smaller Elasticsearch document.
- Creates a `github_issues` index with an explicit mapping.
- Indexes issues using the GitHub issue ID as the Elasticsearch document ID.
- Can be rerun without duplicating documents with the same ID.

## Tech Stack

- Python
- uv
- requests
- python-dotenv
- tqdm
- Elasticsearch Python client
- Docker Compose
- Elasticsearch

## Setup

Install dependencies:

```bash
uv sync
```

Create a `.env` file:

```bash
GITHUB_TOKEN=your_token_here
```

The GitHub token is optional, but recommended because unauthenticated API calls have a lower rate limit.

Start Elasticsearch:

```bash
docker compose up -d
```

Check Elasticsearch:

```bash
curl "http://localhost:9200"
```

## Usage

Fetch open Airflow issues:

```bash
uv run python src/github_fetch_issues.py
```

Ingest issues into an Elasticsearch index:

```bash
uv run python src/main.py ingest github_issues
```

Inspect an Elasticsearch index:

```bash
uv run python src/main.py inspect github_issues
```

You can also use a different index name for experiments:

```bash
uv run python src/main.py ingest test_index
uv run python src/main.py inspect test_index
```

Inspect all indices directly through Elasticsearch:

```bash
curl "http://localhost:9200/_cat/indices?v"
```

## CLI Commands

- `ingest`: fetch issues, transform them, create the index if needed, and index documents.
- `inspect`: show whether an index exists, its document count, and one sample issue.

## Current Document Shape

The current transformed Elasticsearch document looks like:

```python
{
    "id": issue["id"],
    "number": issue["number"],
    "title": issue["title"],
    "body": issue["body"],
    "comments_url": issue["comments_url"],
    "html_url": issue["html_url"],
    "state": issue["state"],
    "locked": issue["locked"],
    "repository": "apache/airflow",
    "created_at": issue["created_at"],
    "updated_at": issue["updated_at"],
    "closed_at": issue["closed_at"],
    "comments": issue["comments"],
    "author_name": issue["user"]["login"],
    "author_id": issue["user"]["id"],
    "author_url": issue["user"]["url"],
    "labels": [label["name"] for label in issue["labels"]],
}
```

## Repository Structure

- `src/github_fetch_issues.py`: GitHub API fetching logic.
- `src/elasticsearch_client.py`: Elasticsearch index creation, transformation, indexing, and count helpers.
- `src/experienced_programmer_script.py`: comparison script with a cleaner GitHub fetching structure.
- `src/main.py`: CLI entry point with `ingest` and `inspect` commands.
- `docker-compose.yml`: local Elasticsearch service.
- `pyproject.toml`: Python project metadata and dependencies.
- `uv.lock`: locked dependency versions.
- `PROJECT_CONTEXT.md`: sprint goals and learning philosophy.
- `LEARNING_NOTES.md`: lessons learned during the sprint.
- `SESSION_HANDOFF.md`: current state and next-step context.

## Project Status

Current phase: Week 2 complete; Week 3 is next.

Completed:

- Week 1 setup and first experiments.
- GitHub issue fetching.
- Local Elasticsearch through Docker Compose.
- Explicit Elasticsearch mapping.
- Basic transform from raw GitHub issue JSON to indexable documents.
- Idempotent indexing by using stable document IDs.
- Refactoring script logic into reusable functions.
- Simple CLI with `ingest` and `inspect` commands.
- Progress bar for GitHub page fetching with `tqdm`.

Next:

- Week 3 update detection.
- Incremental fetching with `state=all`, `updated_at`, and `since`.
- Comments ingestion.
