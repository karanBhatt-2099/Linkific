
import os
import json
import pandas as pd
from client import get, request_with_retry

BASE = "https://jsonplaceholder.typicode.com"


def collect_posts(pages=3, per_page=10):
    posts = []

    for page in range(1, pages + 1):
        response = get(
            f"{BASE}/posts",
            params={"_page": page, "_limit": per_page}
        )

        if response is None or not response.ok:
            break

        data = response.json()

        if not data:
            break

        posts.extend(data)
        print(f"Page {page}: {len(data)} posts")

    return posts


def http_methods_demo():
    post = {
        "title": "Hello",
        "body": "My first post",
        "userId": 1
    }

    response = request_with_retry(
        "POST", f"{BASE}/posts", json=post
    )
    print("POST:", response.status_code if response is not None else "Failed")

    response = request_with_retry(
        "PUT", f"{BASE}/posts/1", json={**post, "id": 1}
    )
    print("PUT:", response.status_code if response is not None else "Failed")

    response = request_with_retry("DELETE", f"{BASE}/posts/1")
    print("DELETE:", response.status_code if response is not None else "Failed")

    response = get(f"{BASE}/posts/99999")
    print("404 test:", response.status_code if response is not None else "Request failed")


def main():
    print("== JSONPlaceholder ==")

    posts = collect_posts()

    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)

    df = pd.DataFrame(posts)
    df.to_csv("data/processed/posts.csv", index=False)

    with open("data/raw/posts.json", "w") as file:
        json.dump(posts, file, indent=2)

    print(f"Saved {len(posts)} posts")

    http_methods_demo()


if __name__ == "__main__":
    main()
