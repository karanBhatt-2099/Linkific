
import os
import time
import pandas as pd
from dotenv import load_dotenv
from client import get

load_dotenv()

URL = "https://api.github.com/search/repositories"


def build_headers():
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        print("Using GitHub without a token")

    return headers


def main(pages=3):
    print("== GitHub ==")
    headers = build_headers()
    repos = []

    for page in range(1, pages + 1):
        params = {
            "q": "topic:machine-learning",
            "sort": "stars",
            "order": "desc",
            "per_page": 30,
            "page": page
        }

        response = get(URL, headers=headers, params=params)

        if response is None:
            break

        data = response.json()

        for item in data.get("items", []):
            repos.append({
                "name": item["full_name"],
                "stars": item["stargazers_count"],
                "forks": item["forks_count"],
                "language": item["language"],
                "owner": item["owner"]["login"],
                "created_at": item["created_at"],
                "url": item["html_url"]
            })

        remaining = int(
            response.headers.get("X-RateLimit-Remaining", 1)
        )
        print("Requests remaining:", remaining)

        if remaining == 0:
            reset = int(
                response.headers.get("X-RateLimit-Reset", 0)
            )
            time.sleep(max(reset - time.time(), 0) + 1)

        time.sleep(1)

    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)

    df = pd.DataFrame(repos)
    df.to_csv("data/processed/github_repos.csv", index=False)
    df.to_json("data/raw/github_repos.json", orient="records", indent=2)

    print(f"Saved {len(df)} repositories")


if __name__ == "__main__":
    main()
