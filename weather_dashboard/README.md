# Weather dashboard

A Django project for displaying weather using the providers in the sibling
`api` package.

## Start the app

You need [uv](https://docs.astral.sh/uv/) installed. From the workspace root:

```bash
cd weather_dashboard
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

`uv sync` installs the project dependencies and the local `../api` package into
the project environment. `migrate` applies pending database migrations.

Open **http://127.0.0.1:8000/** in your browser. Enter latitude and longitude and
submit the form to fetch weather and a location name. Successful results are
saved in SQLite, and the page shows the latest forecast and up to 20 recent
forecasts. Fetching new results requires an internet connection.

Stop the development server with **Ctrl+C**. On subsequent runs:

```bash
cd weather_dashboard
uv run python manage.py runserver
```

Run `migrate` again whenever there are new migrations to apply. The development
server is for local development only.

## How we built the current code

These steps explain how to recreate the current structure, starting from the
existing sibling `api` package. The project and app already exist in this
checkout, so use **Start the app** above to run it rather than generating them
again.

1. **Create a separate Python project and environment.** From the workspace root,
   create `weather_dashboard/` and add a `pyproject.toml` with Python `>=3.13`,
   `django>=5.2,<5.3`, and `api` as dependencies. Point uv at the existing local
   package so changes to its providers are available to Django:

   ```toml
   [tool.uv.sources]
   api = { path = "../api", editable = true }
   ```

   Then install the dependencies:

   ```bash
   cd weather_dashboard
   uv sync
   ```

2. **Generate the Django project and weather app.** Run these inside the new
   directory:

   ```bash
   uv run django-admin startproject config .
   uv run python manage.py startapp weather
   ```

   `startproject` creates `manage.py` and the `config/` package, including settings,
   URL routing, and WSGI/ASGI server entry points. The dot puts these files in the
   current directory. `startapp` creates the `weather/` feature package.

3. **Register the app.** Add `"weather"` to `INSTALLED_APPS` in
   `config/settings.py`. Keep the generated SQLite database configuration.
   `WSGI_APPLICATION = "config.wsgi.application"` points to the callable that
   connects a WSGI web server to Django.

4. **Add the coordinate form.** Create `weather/forms.py` with a `WeatherForm`
   containing two `FloatField` fields: latitude from -90 to 90 and longitude
   from -180 to 180. Set their initial values to `51.231` and `-2.3218`.
   The view uses `is_valid()` before reading `cleaned_data`.

5. **Define stored forecasts.** Add the `Forecast` model in `weather/models.py`
   with a location name, coordinates, temperature, humidity, wind speed,
   description, and an automatically recorded `fetched_at` timestamp. Create
   and apply its database migration:

   ```bash
   uv run python manage.py makemigrations weather
   uv run python manage.py migrate
   ```

   `makemigrations` produces `weather/migrations/0001_initial.py`; `migrate`
   creates the database tables. The migration is already committed, so an
   existing checkout only needs `migrate`.

6. **Write the view.** In `weather/views.py`, make `index` display an unbound
   form on GET. On a valid POST, build a `LongLat`, call `ApiWeatherProvider`
   and `PhotonLocationProvider` from the existing `api` package, and save a
   `Forecast`. Redirect back to the page after saving so refreshing the result
   does not repeat the submission. Catch `requests.RequestException` to show
   an error if a provider request fails. Read the latest 20 saved forecasts
   and pass them, the form, and any error to the template.

7. **Add the HTML template and connect the URLs.** Create
   `weather/templates/weather/index.html` to render the form, CSRF token,
   errors, latest result, and forecast history. Create `weather/urls.py` with
   `path("", views.index, name="index")`. In `config/urls.py`, import `include`
   and add `path("", include("weather.urls"))`, keeping the generated admin
   route. A request to `/` now reaches the weather view.

8. **Check the behavior.** Add tests in `weather/tests.py` for the initial GET,
   successful submission and persistence, invalid coordinates, and API failures.
   Mock provider calls so the tests do not require live services. Run:

   ```bash
   uv run python manage.py check
   uv run python manage.py test weather
   ```

9. **Run locally.** Start `uv run python manage.py runserver` and open
   **http://127.0.0.1:8000/**. This command loads the project settings, checks
   the configuration, and starts Django's development HTTP server using the
   configured WSGI application. It normally reloads when Python files change.

## Lit card component

The latest forecast is wrapped in a `<weather-card>` custom element, defined in
`weather/static/weather/components/weather-card.js`. It extends Lit's
`LitElement`: `render()` creates a styled wrapper containing a `<slot>`.
Django renders the forecast HTML inside `<weather-card>`, and the slot displays
that content inside the wrapper. No JSON conversion is needed.
`static styles` defines the card's border,
background, spacing, and shadow inside its shadow DOM.

The template loads this JavaScript using Django's `{% static %}` tag and a
`type="module"` script. The component imports Lit 3's browser bundle from
jsDelivr, following the [Lit bundle setup](https://lit.dev/docs/getting-started/#use-bundles).
No npm installation or build command is needed; the browser needs internet
access to load Lit. Card styling requires JavaScript, but the Django-rendered
forecast content and history remain readable if JavaScript cannot load.

Run the app, submit coordinates, and check that the latest forecast appears in
a rounded card. Edit the component's styles and refresh to see changes. The
card appears after a forecast has been saved.

## Debug in VS Code

Launch configurations are provided for opening either the whole `python`
workspace or just the `weather_dashboard` folder in VS Code.

1. Install Microsoft's **Python** and **Python Debugger** VS Code extensions.
2. Complete the setup above (`uv sync` and `migrate`), then stop any running
   development server so port 8000 is free.
3. Open **Run and Debug** and select **Django: weather dashboard**.
4. Click beside a Python line number to set a breakpoint, then press **F5**.
5. Open **http://127.0.0.1:8000/** and visit the route that calls your code.

When execution pauses, inspect variables in the debug sidebar. Use **F10** to
step over, **F11** to step into, **F5** to continue, and **Shift+F5** to stop
(your keyboard may require the Fn key).

The configuration uses this project's `.venv` interpreter and disables Django's
automatic reload with `--noreload`. Stop and restart debugging after code changes.
Put a breakpoint inside `weather/views.py` and refresh the page to trigger it.
To reach the provider calls, submit valid coordinates through the form.

## Learning notes

See [Django boilerplate notes](DJANGO_NOTES.md) for detailed explanations of the
generated files, settings, request flow, and next steps for the weather page.
