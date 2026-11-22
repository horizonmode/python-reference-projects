# Weather dashboard with Vue and Django REST Framework

A separate version of `../weather_dashboard`: Django owns the database and
weather providers, while Vue 3 renders the card, forms, and history. This project
has its own SQLite database; it does not copy or modify the original project's
saved forecasts.

The API uses Django REST Framework's `ModelSerializer`, `ModelViewSet`, and
router. Validation and JSON representation live in serializers, and provider
calls live in a separate service. See the [DRF quickstart](https://www.django-rest-framework.org/tutorial/quickstart/).

## Run

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/). From the workspace root:

```bash
cd weather_dashboard_vue
uv sync --locked
uv run python manage.py migrate
uv run python manage.py runserver 8001
```

Open **http://127.0.0.1:8001/**. The separate port lets the original dashboard
continue running on port 8000. Stop with Ctrl+C.

Vue components are single-file components (`.vue`) under `frontend/`, with
`<script>` and `<template>` sections. The compiled bundle includes Vue, so
running Django needs neither Node nor CDN access. To edit frontend code,
install Node.js 22.12+ and run:

```bash
npm ci
npm run build
# Or rebuild automatically as you edit:
npm run watch
```

Vite and the official Vue plugin compile SFCs into Django's static `app.js`.
No separate frontend server is needed. Internet access is needed for live
weather lookup; manual forecast CRUD does not call weather providers.

The database starts empty. Fetch a forecast using coordinates, or choose **Add
manually**. Edit or delete any record using its history row. The card displays
the newest saved record. **Refresh** reads current records from the API, useful
after changes in another tab. Saved timestamps are displayed in your local
timezone and do not change when a record is edited.

## Initial data arrives with the page

1. `GET /` loads the first 20 saved forecasts from SQLite.
2. The same DRF `ForecastSerializer` used by the API serializes the records.
3. The `json_script` template filter embeds safely escaped JSON in the HTML,
   including pagination metadata, the CSRF token, and API URLs.
4. `frontend/App.vue` parses `#initial-data` and initializes Vue's reactive state.
5. Vue renders immediately from that state, with **no startup API request**.
6. Later mutations use `fetch()` with JSON and an `X-CSRFToken` header. Vue
   applies the returned record and refreshes page one to keep history and totals
   accurate, without reloading the document.

This is server-provided initial data with client rendering, rather than Vue SSR
or hydration of server-rendered Vue markup. JavaScript is needed for the UI.
History has Previous/Next controls and 20 records per page. Browsing older
pages keeps the latest-forecast card visible. Mutations return history to page
one. Both the initial response and API use the same pagination class.

## Forecast API

All paths have trailing slashes. Write bodies use `Content-Type: application/json`.
The API is same-origin and retains Django's CSRF protection. It is a local
learning project with no user accounts or per-user record ownership.
`AllowAny` permissions are explicit in `REST_FRAMEWORK` settings. Session
authentication is configured, and `CSRFSessionAuthentication` also checks
anonymous writes, preserving the original app's protection. Standard DRF
session authentication only enforces CSRF after session authentication succeeds.
If accounts are added later, use `IsAuthenticated` and filter records by owner.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/api/forecasts/` | List 20 records, newest first, with pagination metadata |
| POST | `/api/forecasts/` | Create a supplied forecast; returns `201` and `{"forecast": {...}}` |
| GET | `/api/forecasts/<id>/` | Read one forecast |
| PUT | `/api/forecasts/<id>/` | Replace all editable fields |
| PATCH | `/api/forecasts/<id>/` | Update supplied editable fields |
| DELETE | `/api/forecasts/<id>/` | Delete a record; returns `204` |
| POST | `/api/forecasts/fetch/` | Fetch live weather for coordinates and save it; returns `201` |

List responses have the shape below. Follow `next` or `previous` links, or
request `/api/forecasts/?page=2`:

```json
{"forecasts": [], "count": 0, "next": null, "previous": null}
```

A create or full update body looks like:

```json
{
  "location_name": "Frome",
  "latitude": 51.231,
  "longitude": -2.3218,
  "temperature": 12,
  "humidity": 70,
  "wind_speed": 8,
  "description": "Cloudy"
}
```

Live lookup accepts just `{"latitude": 51.231, "longitude": -2.3218}`. IDs and
`fetched_at` are server-controlled. Coordinates, humidity (0–100), nonnegative
wind speed, finite numbers, and required text fields are validated on the server.
Validation failures return `400` with `error` and field `errors`, missing records
return `404`, unsupported content types return `415`, and provider failures
return `502`. Failed lookups do not save a record.
Unknown fields and attempts to write `id` or `fetched_at` return `400`.
The custom DRF exception handler keeps the Vue client's `error`/`errors`
response format consistent for parsing, validation, and HTTP errors.

## Files to follow

| File | Purpose |
| --- | --- |
| `weather/views.py` | Initial page using the shared API serializer and pagination |
| `weather/api/serializers.py` | Explicit fields, read-only metadata, and input validation |
| `weather/api/views.py` | CRUD viewset and live-fetch action |
| `weather/api/urls.py` | Router-generated API routes |
| `weather/api/pagination.py` | Shared first-page and API pagination |
| `weather/api/authentication.py` | Session authentication with CSRF for all writes |
| `weather/api/exceptions.py` | Consistent error responses |
| `weather/services.py` | Weather and location provider integration |
| `weather/urls.py` | Page route and API router inclusion |
| `weather/models.py` | Forecast database model |
| `weather/templates/weather/index.html` | Page shell and embedded initial JSON |
| `frontend/App.vue` | Vue state, API requests, forms, and history |
| `frontend/ForecastCard.vue` | Reusable Vue SFC card with an object prop |
| `weather/static/weather/styles.css` | Responsive styling |

Unlike a Django model, a JavaScript object can be passed directly between Vue
components: `<ForecastCard :forecast="latest" />` passes the object as a prop.
`frontend/main.js` mounts `App.vue`; `ForecastCard.vue` uses `<script setup>`
with `defineProps` and `defineEmits`. Edit the `.vue` sources and rebuild
`weather/static/weather/app.js`.
JSON is only needed when crossing the Python/browser boundary.

## Checks

For VS Code, open `weather_dashboard_vue` as the project folder. The local
`.vscode/settings.json` points to its `.venv`; if VS Code has already selected
another interpreter, use **Python: Select Interpreter** and choose
`weather_dashboard_vue/.venv/bin/python`. Opening the whole repository may
require selecting that interpreter explicitly as well.

`uv sync --locked` installs the development typing packages for Django, DRF,
and requests. The Pyright configuration in `pyproject.toml` uses this environment
and the sibling `api/src` package. Run `pyright` if it is installed to check types.

```bash
uv run python manage.py check
uv run python manage.py test weather
uv run python manage.py makemigrations --check --dry-run
```

Tests cover bootstrap escaping, CRUD, partial updates, invalid input, CSRF,
HTTP methods, pagination, authenticated/anonymous CSRF checks, and mocked
live-provider success/failure. To run the frontend
state/API-contract tests with Node:

```bash
npm ci
npm test
```

These tests do not mount Vue in a browser. Browser smoke check:
add a manual record, edit it, reload to verify persistence, and delete it. In
the browser Network tab, verify no `/api/forecasts/` request occurs until you
perform an action or choose Refresh. With over 20 records, verify Next/Previous
change the history while the latest-forecast card stays the same.
