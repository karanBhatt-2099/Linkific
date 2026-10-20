
import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://example.com/data"

# 1. API key in URL
request1 = requests.Request(
    "GET", url,
    params={"appid": os.getenv("OPENWEATHER_API_KEY", "demo")}
)
print("API key in URL:", request1.prepare().url)

# 2. API key in header
request2 = requests.Request(
    "GET", url,
    headers={"X-Api-Key": os.getenv("NEWS_API_KEY", "demo")}
)
print("API key in header:", request2.prepare().headers)

# 3. Bearer token
request3 = requests.Request(
    "GET", url,
    headers={"Authorization": "Bearer " + os.getenv("GITHUB_TOKEN", "demo")}
)
print("Bearer token:", request3.prepare().headers)

# 4. OAuth 2.0
print("""
OAuth 2.0 steps:
1. Login to the provider.
2. Get an authorization code.
3. Exchange the code for an access token.
4. Use the token to access the API.
5. Refresh the token when it expires.
""")
