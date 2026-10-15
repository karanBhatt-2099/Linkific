# API Data Collection Project

This project is about collecting data from different public APIs using Python. It covers how to make API requests, handle errors, use authentication, work with pagination, and save the collected data in CSV and JSON formats.

I have used five APIs to understand how different APIs work and how to handle their responses.

## Project Structure

```text
api_data_collection/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── run_all.py
├── src/
│   ├── client.py
│   ├── jsonplaceholder.py
│   ├── rest_countries.py
│   ├── github_repos.py
│   ├── openweather.py
│   ├── news_api.py
│   ├── auth_examples.py
│   └── pagination_examples.py
├── data/
│   ├── raw/
│   └── processed/
└── notes/
    └── api_basics.md
```

## Technologies Used

- Python
- Requests
- Pandas
- Python-dotenv
- REST APIs
- CSV and JSON

## Setup

Clone or download the project and open the project folder in your terminal.

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install the required libraries:

```bash
pip install -r requirements.txt
```

Create a `.env` file from the example file:

```powershell
copy .env.example .env
```

Add your API keys to `.env` wherever required.

## APIs Used

| API | Purpose |
|---|---|
| JSONPlaceholder | Fetch posts and test GET, POST, PUT and DELETE requests |
| REST Countries | Collect country details such as capital, population and region |
| GitHub API | Collect repository details such as stars, forks and programming language |
| OpenWeather | Get weather information for a location |
| News API | Fetch news articles |

JSONPlaceholder and GitHub's public repository search can be used without an API key, although GitHub has higher rate limits for authenticated requests. REST Countries access depends on the API version and its current authentication requirements. OpenWeather and News API require their respective API keys.

## How to Run

Run all scripts from the project root:

```bash
python run_all.py
```

To run an individual script:

```bash
python src/jsonplaceholder.py
python src/rest_countries.py
python src/github_repos.py
python src/openweather.py
python src/news_api.py
```

You can also run the authentication and pagination examples:

```bash
python src/auth_examples.py
python src/pagination_examples.py
```

Some scripts may require valid API keys before they can run successfully.

## What I Learned

While working on this project, I practised:

- Sending GET, POST, PUT and DELETE requests.
- Passing query parameters and request headers.
- Using API keys and Bearer token authentication.
- Handling request timeouts, errors and retries.
- Implementing page-number, link-header and cursor-based pagination.
- Reading nested JSON responses and converting them into structured data.
- Using Pandas to process data and save it as CSV and JSON files.
- Working with API rate limits and environment variables.

## Output

The collected data is saved in two folders:

- `data/raw/` — stores the data in JSON format.
- `data/processed/` — stores the data in CSV format.

The exact output files depend on which scripts run successfully.

## Troubleshooting

- **401 Unauthorized:** Check whether the API key or token is valid.
- **404 Not Found:** Check the API endpoint and requested resource.
- **429 Too Many Requests:** The API rate limit may have been reached.
- **ModuleNotFoundError:** Install the dependencies using `pip install -r requirements.txt`.
- **API response errors:** Check the API documentation, endpoint version and required parameters.

**Note:** Keep your API keys in `.env` and never upload that file to GitHub.