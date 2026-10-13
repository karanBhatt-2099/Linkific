# API Basics Cheat Sheet

## REST API
An API that uses URLs (resources) and HTTP methods to read/change data. Responses are usually JSON.

## HTTP Methods
| Method | Purpose | Example |
|---|---|---|
| GET | Read data | get a list of posts |
| POST | Create data | add a new post |
| PUT | Update/replace data | edit post 1 |
| DELETE | Remove data | delete post 1 |

## Status Codes
| Code | Meaning | What to do |
|---|---|---|
| 200 | OK | parse the data |
| 201 | Created | POST worked |
| 400 | Bad request | fix your params |
| 401 | Unauthorized | check your key/token |
| 403 | Forbidden | no permission / rate limit |
| 404 | Not found | wrong URL or id |
| 429 | Too many requests | wait, then retry |
| 500/503 | Server error | retry with backoff |

## Request parts
- **URL**: `https://api.site.com/users`
- **Parameters**: `?page=2&limit=10`
- **Headers**: metadata, e.g. `Authorization: Bearer abc123`
- **Body**: JSON data sent with POST/PUT
- **Response**: status code + headers + body

## Exponential backoff
Wait longer after every failure: 1s, 2s, 4s, 8s. Gives the server time to recover.

## OAuth 2.0 (basics)
User logs in on the provider -> you get a code -> swap it for an access token -> use it as a Bearer token -> refresh when it expires.
