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

Open **http://127.0.0.1:8000/** in your browser. The weather page is not connected
yet, so the initial project displays Django's welcome page.

Stop the development server with **Ctrl+C**. On subsequent runs:

```bash
cd weather_dashboard
uv run python manage.py runserver
```

Run `migrate` again whenever there are new migrations to apply. The development
server is for local development only.

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
Once your weather view is connected, put a breakpoint inside it and refresh its
page to trigger the breakpoint. An unused view will not run merely because the
server starts.

## Learning notes

See [Django boilerplate notes](DJANGO_NOTES.md) for detailed explanations of the
generated files, settings, request flow, and next steps for the weather page.
