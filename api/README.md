# The mentor over HTTP

The same mentor as a plain REST API: the reference library, the three calculators,
and the rules the other ports run on. Nothing is reimplemented — the docs are read
from `embedded-iot-mentor/` and the calculators shell out to its scripts, so an
answer here is the answer the skill would give.

Use this when the caller is code rather than a chat client: a build script that
wants a BOM total, a dashboard that wants a battery estimate, or your own model
that wants the mentor's rules as a system prompt.

## Run it

```
pip install -r api/requirements.txt
uvicorn api.main:app --reload
```

Then open <http://127.0.0.1:8000/docs>. Run it from the repository root, not from
this folder, or `api.main` will not import.

## Routes

| Route | Does |
|---|---|
| `GET /healthz` | Liveness. The one route that never needs a key |
| `GET /version` | The skill's own version, read from `SKILL.md` |
| `GET /instructions` | The mentor's rules, for your own model's system prompt |
| `GET /references` | Names of the reference documents |
| `GET /references/{name}` | One document, verbatim |
| `GET /search?q=` | Substring search across the library, with line numbers |
| `POST /cost` | BOM total. `{"items": [{"qty": 1, "unit_price": 4.5, "description": "ESP32"}]}` |
| `POST /sleep-budget` | Battery runtime and what dominates the drain |
| `POST /footprint` | Whether a package is hand-solderable |

Bad input fails twice over: the request models reject it before a process starts,
and the scripts reject what only they can judge — an awake time longer than the
wake interval, say. The first is a 422, the second a 400 carrying the script's own
message.

## Settings

All optional. The defaults suit a local run; a deployment should at least think
about the first two.

| Variable | Default | Does |
|---|---|---|
| `EIM_API_KEY` | unset (open) | Require `X-API-Key` on every route but `/healthz` |
| `EIM_CORS_ORIGINS` | none | Comma-separated origins allowed to call from a browser |
| `EIM_RATE_LIMIT_PER_MIN` | `60` | Requests per IP per minute, counted per instance |
| `EIM_MAX_CONCURRENT_SCRIPTS` | `4` | Calculations running at once; the rest queue |
| `EIM_SKILL_DIR` | the sibling folder | Where the skill lives, if it was copied elsewhere |

Setting `EIM_API_KEY` also locks `/docs`, since Swagger sends no key — expected on
a deployed instance, surprising the first time.

## Test it

```
python api/test_api.py
```


No pytest, and the routes are called as plain functions, so this needs nothing the
API does not already need. CI runs it on every push.