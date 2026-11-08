# Free Fire Like API

A FastAPI service for sending likes to Free Fire player profiles, with API key
auth, rate limiting, UID validation, multi-region support and Swagger docs.

It runs in **test mode** by default: likes are simulated in memory and no real
game account is touched.

## Important: about real likes

Garena does not offer a public API for sending profile likes. This project
**only** supports two providers:

| Mode | What it does |
|------|--------------|
| `test` (default) | Simulates likes in memory. No network calls. |
| `official` | Forwards requests to an HTTPS partner API you have **written permission** to use. Without one configured, it returns `503`. |

It does not include, and should not be extended with, private game-client
endpoints, bundled encryption keys, or pools of bot accounts. Those break the
game's Terms of Service and can get the target player's account banned.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # then set FFLIKE_API_KEYS
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** (Swagger UI) or `/redoc`.
Click **Authorize** and enter your API key to try requests in the browser.

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |
| GET | `/api/v1/regions` | Yes | List supported regions |
| POST | `/api/v1/likes` | Yes | Send likes to a UID |
| GET | `/api/v1/likes/{region}/{uid}` | Yes | Like count and today's quota |

### Example

```bash
curl -X POST http://localhost:8000/api/v1/likes \
  -H "X-API-Key: change-me" \
  -H "Content-Type: application/json" \
  -d '{"uid": "123456789", "region": "BD", "quantity": 10}'
```

```json
{
  "success": true,
  "data": {
    "uid": "123456789",
    "region": "BD",
    "nickname": "TestPlayer_BD_6789",
    "likes_before": 2410,
    "likes_added": 10,
    "likes_after": 2420,
    "daily_remaining": 90,
    "mode": "test",
    "simulated": true,
    "timestamp": "2026-11-08T12:00:00Z"
  },
  "request_id": "5f2c..."
}
```

Errors always have the same shape:

```json
{
  "success": false,
  "error": { "code": "validation_error", "message": "Invalid request.", "details": [...] },
  "request_id": "5f2c..."
}
```

| Status | `error.code` | When |
|--------|--------------|------|
| 401 | `invalid_api_key` | Missing or wrong `X-API-Key` |
| 404 | `player_not_found` | UID doesn't exist (in test mode: UIDs ending `0000`) |
| 422 | `validation_error` | Bad UID, region or quantity |
| 429 | `rate_limited` | Too many requests for this key (see `Retry-After`) |
| 429 | `daily_limit_reached` | UID hit its daily like cap |
| 502 | `upstream_error` | Partner API failed or timed out |
| 503 | `provider_unavailable` | Official mode without a configured partner API |

### Validation rules

- **UID**: 8–12 digits, must not start with `0`.
- **Region**: `BD`, `IND`, `ID`, `PK`, `SG`, `TH`, `VN`, `TW`, `ME`, `BR`, `SAC`, `NA`, `US`, `EU`, `RU`.
  Case-insensitive; aliases `Bangladesh`, `India`, `IN`, `Indonesia`, `Pakistan` also work.
- **quantity**: 1–100 (default 1). If the daily cap is nearly used up, only the remaining amount is sent.

## Configuration

All settings are environment variables with the `FFLIKE_` prefix (see `.env.example`).

| Variable | Default | Meaning |
|----------|---------|---------|
| `FFLIKE_API_KEYS` | `dev-test-key` | Comma-separated accepted keys. **Change this.** |
| `FFLIKE_PROVIDER_MODE` | `test` | `test` or `official` |
| `FFLIKE_RATE_LIMIT_REQUESTS` | `30` | Requests per key per window |
| `FFLIKE_RATE_LIMIT_WINDOW_SECONDS` | `60` | Window length |
| `FFLIKE_DAILY_LIKES_PER_UID` | `100` | Max likes per UID per UTC day |
| `FFLIKE_OFFICIAL_API_BASE_URL` | – | Partner API base URL (HTTPS only) |
| `FFLIKE_OFFICIAL_API_TOKEN` | – | Bearer token for the partner API |
| `FFLIKE_OFFICIAL_API_ALLOWED_HOSTS` | – | Hosts the provider may call; anything else is refused |

### Official mode security

- HTTPS only; plain `http://` URLs are rejected at startup.
- The base URL's host must be in `FFLIKE_OFFICIAL_API_ALLOWED_HOSTS`.
- Redirects are not followed, so it can't be bounced to another host.
- The expected partner API contract is documented at the top of
  `app/services/providers/official.py`.

## Project structure

```
app/
├── main.py                  # App factory, middleware, Swagger metadata
├── models.py                # Pydantic request/response schemas, UID validation
├── core/
│   ├── config.py            # Settings from env
│   ├── security.py          # X-API-Key auth (constant-time compare)
│   ├── rate_limit.py        # Sliding-window limiter per key
│   └── errors.py            # Error types + JSON error handlers
├── api/
│   ├── router.py            # /api/v1 router
│   ├── deps.py
│   └── routes/              # health, regions, likes
└── services/
    ├── regions.py           # Region enum + aliases
    ├── like_service.py      # Daily quota + provider orchestration
    └── providers/
        ├── base.py          # Provider interface
        ├── simulation.py    # Test mode
        └── official.py      # Authorized partner API adapter
tests/                       # pytest suite
```

## Tests

```bash
pytest
```

## Deployment

**Docker**

```bash
docker build -t fflike-api .
docker run -p 8000:8000 --env-file .env fflike-api
```

**Vercel**: `vercel.json` + `index.py` are included. Set the `FFLIKE_*` variables in the project settings.

Note: rate limits, daily quotas and test-mode like counts are kept in memory,
so they are per process and reset on restart. For multiple workers or
serverless deployments, move them to Redis or a database.
