
import requests
import time


def request_with_retry(
    method, url, headers=None, params=None, json=None, max_retries=4
):
    for attempt in range(max_retries):
        wait = 2 ** attempt

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json,
                timeout=10
            )

            if response.ok:
                return response

            if response.status_code == 429 or response.status_code >= 500:
                print("Retrying after", wait, "seconds")
                time.sleep(wait)
            else:
                print("Request failed:", response.status_code)
                return response

        except requests.RequestException:
            print("Connection error. Retrying...")
            time.sleep(wait)

    print("All retries failed.")
    return None


def get(url, headers=None, params=None):
    return request_with_retry(
        "GET", url, headers=headers, params=params
    )
