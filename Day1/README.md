# Python Data Ingestion Pipeline (PokeAPI)

Fetch Pokemon records from https://pokeapi.co/api/v2/pokemon/<name> (free, no API key)
-> save raw JSON -> extract fields -> validate and clean -> remove duplicates -> export CSV -> summary.

## Run
```bash
pip install -r requirements.txt
python pipeline.py            # live API (falls back to sample data if offline)
python pipeline.py --sample   # force the built-in sample data
```

## Output (created on first run)
```
output/raw/    pokemon_raw_<time>.json        untouched API responses
output/clean/  pokemon_clean_<time>.csv       cleaned, de-duplicated records
               pokemon_rejected_<time>.csv    invalid records with a reject reason
```

## Steps (one function each in pipeline.py)
| Step | Function | Notes |
|---|---|---|
| Fetch | `fetch_pokemon`, `fetch_all` | timeout, 2 attempts, 404 not retried, stops if internet is down |
| Save raw | `save_raw` | raw JSON kept for reproducibility |
| Extract | `extract` | flattens nested JSON (types, abilities, stats) |
| Validate/clean | `validate_and_clean` | required fields, numeric checks, height/weight > 0, unit conversion (dm -> m, hg -> kg), title-case names |
| Deduplicate | `remove_duplicates` | one record per `pokemon_id` |
| Export | `write_csv` | clean CSV + rejected CSV |
| Summary | `main` | fetched / failed / rejected / duplicates / processed + file paths |

The list `POKEMON` deliberately has a repeated name (duplicate test) and a fake name
(404 failure test). Edit it to fetch any Pokemon you like.

