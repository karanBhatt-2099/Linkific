"""Run every collector. Usage: python run_all.py"""
import sys
sys.path.insert(0, "src")

import jsonplaceholder, rest_countries, github_repos, openweather, news_api

for module in (jsonplaceholder, rest_countries, github_repos, openweather, news_api):
    try:
        module.main()
    except Exception as e:           # one failing API shouldn't stop the others
        print(f"{module.__name__} failed: {e}")
    print()
print("Done! Check the data/ folder.")
