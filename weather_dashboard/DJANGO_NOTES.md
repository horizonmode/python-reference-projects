# Django boilerplate explained

These notes describe your `weather_dashboard` project, generated with Django 5.2. Examples marked **add later** are teaching examples, not changes already made to your application.

## 1. Project versus app

A **project** is the complete website and its configuration. An **app** is a Python package responsible for a feature within that website.

In your workspace:

- `weather_dashboard/` is the outer project directory. Run management commands here.
- `config/` is the project’s configuration package. The name `config` was your choice when running `startproject`.
- `weather/` is the Django app responsible for your weather pages.
- `../api/` is your existing Python package containing weather and location providers. A reusable Python package does not have to be a Django app.

Django creates the initial files with:

```bash
django-admin startproject config .
python manage.py startapp weather
```

The dot means “put the project files in the current directory.” An app can contain several pages; you do not need a separate app for every URL.

See Django’s [project and application explanation](https://docs.djangoproject.com/en/5.2/ref/applications/#projects-and-applications).

## 2. Your current structure

```text
weather_dashboard/
├── manage.py
├── pyproject.toml
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── weather/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── tests.py
    ├── views.py
    └── migrations/
        └── __init__.py
```

`startapp` does **not** generate `urls.py`, `forms.py`, a `templates/` directory, or a `static/` directory. You add these when needed.

Your current settings register `weather`, but the project URL configuration only routes `admin/`. Your `weather/views.py` is still a placeholder, so there is no weather page yet.

## 3. `manage.py`: the project command-line entry point

This file runs Django management commands using this project’s settings.

The important line is:

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
```

- `os.environ` is the process’s environment-variable mapping.
- `DJANGO_SETTINGS_MODULE` tells Django which Python module contains its configuration.
- `config.settings` is a Python import path, corresponding to `config/settings.py`.
- `setdefault` supplies this value only if it has not already been set. Another environment can select different settings.

Next:

```python
execute_from_command_line(sys.argv)
```

`sys.argv` contains the command-line arguments. When you run `python manage.py migrate`, Django reads `migrate` and dispatches to that management command.

The import error handler gives a clearer error if Django cannot be imported. The final `if __name__ == '__main__':` block runs `main()` when the file is executed directly.

You normally leave this file alone.

| Command in your project | Purpose |
| --- | --- |
| `uv run python manage.py runserver` | Start the local development server |
| `uv run python manage.py check` | Check project configuration for common problems |
| `uv run python manage.py startapp weather` | Generate an app; you have already done this |
| `uv run python manage.py makemigrations` | Generate migration files from model changes |
| `uv run python manage.py migrate` | Apply pending database migrations |
| `uv run python manage.py createsuperuser` | Create an administrator account |
| `uv run python manage.py shell` | Open Python with Django initialized |
| `uv run python manage.py test` | Run Django’s test suite |

`uv run` selects and synchronizes your project environment. `manage.py` handles the Django command itself.

## 4. `config/__init__.py`: the configuration package

An empty `__init__.py` marks this directory as a regular Python package, allowing imports such as `config.settings`.

It does not need to contain configuration. Avoid putting startup work or API calls here: importing a package should not fetch weather.

The same principle applies to `weather/__init__.py` and `weather/migrations/__init__.py`.

## 5. `config/settings.py`: configuration for the website

This is a normal Python module containing settings as module-level variables. Django supplies defaults for settings you do not override. Application code should access settings through `from django.conf import settings` rather than importing `config.settings` directly.

See the [settings guide](https://docs.djangoproject.com/en/5.2/topics/settings/) and [settings reference](https://docs.djangoproject.com/en/5.2/ref/settings/).

### `BASE_DIR`

```python
BASE_DIR = Path(__file__).resolve().parent.parent
```

`__file__` refers to `settings.py`. `resolve()` produces an absolute path; two `.parent` operations move from that file to `config/`, then to `weather_dashboard/`.

This lets you build paths independently of the terminal’s current working directory:

```python
BASE_DIR / 'db.sqlite3'
```

The `/` operator joins `Path` components; it is not division here.

### `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS`

| Setting | Meaning |
| --- | --- |
| `SECRET_KEY` | A secret used for cryptographic signing, including some authentication-related tokens. It is not a database password. |
| `DEBUG` | Enables detailed development error pages and other development behavior. |
| `ALLOWED_HOSTS` | Lists host/domain names this Django site accepts in incoming requests. Entries are not complete URLs. |

Keep a production secret outside committed source code, disable debug in production, and configure allowed hosts. With `DEBUG=True` and an empty host list, Django permits its documented localhost defaults. `ALLOWED_HOSTS` does not control which external weather APIs your Python code may call.

### `INSTALLED_APPS`

This tells Django which apps participate in the project. Your generated entries provide:

| App | Responsibility |
| --- | --- |
| `django.contrib.admin` | The administrative interface |
| `django.contrib.auth` | Users, groups, and permissions |
| `django.contrib.contenttypes` | Records identifying model types, used by features such as permissions |
| `django.contrib.sessions` | Session storage support |
| `django.contrib.messages` | Temporary messages, such as “Location saved” |
| `django.contrib.staticfiles` | Discovery and collection of CSS, JavaScript, and image assets |
| `weather` | Your weather functionality |

Your `"weather"` entry allows Django to discover `WeatherConfig` in `weather/apps.py`. You can instead use the explicit path `"weather.apps.WeatherConfig"`; do not add both.

Installing your `api` package makes it importable. It does not need an `INSTALLED_APPS` entry because it is currently an ordinary Python library without Django app features.

### `MIDDLEWARE`

Middleware wraps request handling. Requests pass through the configured sequence toward the view; responses pass back through the wrappers in reverse order. A middleware can also return a response before the view runs.

| Middleware | Main job |
| --- | --- |
| `SecurityMiddleware` | Applies configured security-related behavior and headers |
| `SessionMiddleware` | Makes session data available as `request.session` |
| `CommonMiddleware` | Handles common behavior such as configured URL normalization |
| `CsrfViewMiddleware` | Protects unsafe requests, such as form POSTs, against cross-site request forgery |
| `AuthenticationMiddleware` | Attaches the authenticated user or anonymous user to `request.user` |
| `MessageMiddleware` | Makes temporary messages available during the request |
| `XFrameOptionsMiddleware` | Adds framing protection through the `X-Frame-Options` header |

Order matters: authentication relies on sessions being available first. For a Django POST form, include `{% csrf_token %}` inside the form template.

### `ROOT_URLCONF`

```python
ROOT_URLCONF = 'config.urls'
```

This identifies the first URL configuration Django consults when routing requests.

### `TEMPLATES`

This configures HTML template rendering:

- `BACKEND` selects Django’s template engine.
- `DIRS` lists additional template search directories. Yours is empty.
- `APP_DIRS=True` enables searching inside installed apps’ `templates/` directories.
- `context_processors` supply common template context, such as the request, user, permissions, and messages, when rendering with a request.

For your app, a useful future path is:

```text
weather/templates/weather/index.html
```

The second `weather/` namespaces the template name, reducing collisions with templates from other apps. A view refers to it as `"weather/index.html"`.

### `WSGI_APPLICATION`

```python
WSGI_APPLICATION = 'config.wsgi.application'
```

This identifies the WSGI callable used by Django’s development server. Deployment servers also use the appropriate entry point described later.

### `DATABASES`

Your default configuration uses SQLite, with data stored in `db.sqlite3` under `BASE_DIR`. It needs no separate database server.

The database stores persistent application data. Your external API call does not automatically save its response to SQLite. To store favorite locations, you would add a model and explicitly save instances.

### `AUTH_PASSWORD_VALIDATORS`

These define password-quality checks used by Django’s password forms and management commands. The generated validators check similarity to user attributes, minimum length, common passwords, and entirely numeric passwords.

These checks do not automatically run every time you assign a model field or create a user programmatically. Password hashing is a separate concern; use Django’s password APIs rather than assigning plaintext passwords.

### Language and time settings

| Setting | Meaning in your project |
| --- | --- |
| `LANGUAGE_CODE = 'en-us'` | Default language code for Django’s translation machinery |
| `TIME_ZONE = 'UTC'` | Default project time zone |
| `USE_I18N = True` | Enables translation support |
| `USE_TZ = True` | Enables timezone-aware datetime handling |

For a UK dashboard you could choose `TIME_ZONE = 'Europe/London'` to account for GMT/BST. This setting does not discover the user’s location or automatically change Open-Meteo’s request parameters.

### Static files and primary keys

`STATIC_URL = 'static/'` configures the static-file URL prefix. It does not create a directory or set up production hosting. Static files are assets shipped with the application; user uploads are handled separately as media.

`DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'` selects a 64-bit auto-incrementing primary key for models without an explicitly declared primary key.

## 6. `config/urls.py`: the website’s route table

Django checks `urlpatterns` in order and uses the first matching route.

Your current route:

```python
path('admin/', admin.site.urls)
```

connects `/admin/` to Django’s admin routes. It does not create a route for `/`.

**Add later**, to connect the weather app:

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('weather.urls')),
    path('admin/', admin.site.urls),
]
```

`include()` delegates to another URL configuration after removing the matched prefix. An empty prefix delegates without removing any path segments. If the included patterns do not match, Django can continue checking later root patterns.

Routes omit the leading slash. Query parameters such as `?latitude=51.231` are read by the view, not matched by `path()`.

See [URL routing](https://docs.djangoproject.com/en/5.2/topics/http/urls/).

## 7. `config/wsgi.py` and `config/asgi.py`: server entry points

These files expose a variable called `application`, which is a callable a compatible server invokes.

Both select `config.settings`, then initialize Django:

```python
# wsgi.py
application = get_wsgi_application()

# asgi.py
application = get_asgi_application()
```

| File | Interface | Typical server |
| --- | --- | --- |
| `wsgi.py` | WSGI, a synchronous Python web-server interface | Gunicorn’s WSGI workers |
| `asgi.py` | ASGI, an asynchronous server interface | Uvicorn or Daphne |

They are alternative entry points, not two files every request passes through. Your current weather dashboard can use synchronous views. Having `asgi.py` does not make blocking `requests.get()` calls asynchronous. Django itself does not provide WebSocket consumers simply because an ASGI entry point exists.

You rarely edit these files while building ordinary pages. See [WSGI deployment](https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/) and [ASGI deployment](https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/).

## 8. `weather/apps.py`: metadata and startup configuration

Your generated class is:

```python
class WeatherConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'weather'
```

`name` is the full Python import path of the app. `default_auto_field` specifies this app’s default primary-key field type.

An app configuration can also define a human-readable `verbose_name` or a `ready()` method, commonly used to register signal handlers. Do not fetch weather or query the database in `ready()`: initialization happens for management commands too, and can run more than once in some circumstances.

## 9. `weather/views.py`: handling a request

A view receives an `HttpRequest` and returns an `HttpResponse` (or raises an exception Django handles). It decides what to do with form data, calls application logic, and prepares a response.

Your generated `render` import is a convenience for combining a template with context data to produce an HTTP response.

**Add later**, a minimal view:

```python
from django.http import HttpResponse


def index(request):
    return HttpResponse('Weather dashboard')
```

A template-based version would use:

```python
return render(request, 'weather/index.html', {'location_name': name})
```

Here `name` must be computed before that line. The dictionary makes `location_name` available to the template as `{{ location_name }}`.

For your dashboard, the view should validate input, call your existing providers, and pass their results to a template. Avoid `input()` in a view: browser input arrives through the request. Avoid relying on `print()` for the page: it writes to the server console, not the HTTP response.

## 10. `weather/models.py`: persistent data definitions

Models are Python classes describing stored data and its behavior. Django’s ORM translates operations on these classes into database queries.

**Add later**, a model for favorites:

```python
from django.db import models


class SavedLocation(models.Model):
    name = models.CharField(max_length=120)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name
```

Each instance represents a row. Fields describe columns. Django supplies an `id` primary key unless you specify another. `__str__` provides a useful display label, including in admin.

After adding or changing fields, create and apply migrations. Coordinate range validation still needs to be defined; a `FloatField` alone does not enforce geographic bounds. Model `save()` does not automatically call `full_clean()`.

You do not need a model just to display a live forecast. Your existing `WeatherForecast` dataclass represents data in memory; it is not automatically a database model.

## 11. `weather/migrations/`: database change history

Migration files record changes to model state and operations needed to evolve the database schema. Django builds a dependency graph from them.

```bash
uv run python manage.py makemigrations weather
uv run python manage.py migrate
```

- `makemigrations` compares current models with migration state and writes files such as `0001_initial.py`.
- `migrate` applies unapplied migrations to the configured database.
- `showmigrations` lists migrations and whether they have been applied.

Editing `models.py` does not immediately change database tables. Commit migration files with the corresponding model changes so other environments can apply them. Migrations are not database backups.

## 12. `weather/admin.py`: registering models with admin

This is where you expose your models through Django’s administrative interface.

**Add later**, once `SavedLocation` exists:

```python
from django.contrib import admin
from .models import SavedLocation

admin.site.register(SavedLocation)
```

The admin route is already present in `config/urls.py`. Run migrations and `createsuperuser` before signing in. Registering a model adds its management interface; it does not create the model’s database table.

Admin is useful for staff managing saved locations. Your public weather page still needs its own view and template.

## 13. `weather/tests.py`: automated checks

This generated file is a starting point for tests. Django discovers appropriately named test modules, so larger apps often replace it with a `tests/` package.

Use `django.test.TestCase` when tests need database isolation or Django’s test client. For pure provider logic without database access, ordinary unit tests can be sufficient.

Useful dashboard tests would verify:

- A GET request displays the form.
- Valid coordinates display a forecast and location name.
- Invalid coordinates produce form errors.
- Provider failures display an understandable message.

Mock external HTTP calls so the tests are independent of API uptime and current weather. Run with `uv run python manage.py test`.

## 14. Files you add yourself

| Path | Purpose |
| --- | --- |
| `weather/urls.py` | Routes belonging to the weather feature |
| `weather/forms.py` | Parses input, validates coordinates, and exposes cleaned values |
| `weather/templates/weather/index.html` | HTML layout for the form and results |
| `weather/static/weather/style.css` | Styling for the weather pages |

A Django form can use `FloatField(min_value=-90, max_value=90)` for latitude and corresponding bounds of −180 to 180 for longitude. Call `form.is_valid()` before using `form.cleaned_data`.

Keep HTTP-provider code in your existing `api` package. Django’s view is the web entry point; providers remain reusable by both the website and CLI.

## 15. Supporting files outside Django’s boilerplate

| File or directory | Role |
| --- | --- |
| `pyproject.toml` | Python project metadata, dependencies, and uv configuration |
| `uv.lock` | Resolved dependency versions used by uv, when generated |
| `.venv/` | Installed Python environment; generated locally |
| `db.sqlite3` | SQLite database, created when the database is initialized |
| `__pycache__/` | Python bytecode cache; generated automatically |

Your `pyproject.toml` uses an editable source for `api` at `../api`. That means your Django code imports the existing package rather than maintaining a copy of it.

## 16. Following one weather request

```text
Browser requests /
    ↓
Web server invokes Django
    ↓
Request middleware
    ↓
config/urls.py → weather/urls.py
    ↓
weather/views.py
    ├── weather/forms.py validates coordinates
    ├── ApiWeatherProvider fetches weather
    ├── PhotonLocationProvider fetches the place name
    └── render() combines results with a template
    ↓
Response middleware
    ↓
Browser receives HTML
```

This is the intended dashboard flow once you add the form, view, template, and route. A model only participates if you choose to read or write saved data. `manage.py` starts development commands; it is not a function the browser calls for each request.

## 17. What to work on first

1. Add a minimal `index` view and `weather/urls.py`.
2. Include the app’s routes from `config/urls.py`.
3. Verify the page with `uv run python manage.py runserver`.
4. Add a template and coordinate form.
5. Call your providers only after valid form input.
6. Add graceful API-error handling and tests.
7. Add `SavedLocation`, migrations, and admin registration when you want persistence.

Leave `manage.py`, `asgi.py`, `wsgi.py`, and the empty `__init__.py` files unchanged unless you have a specific reason to customize them.

For the official walkthrough, see [Django tutorial part 1](https://docs.djangoproject.com/en/5.2/intro/tutorial01/) for projects, views, and URLs, and [part 2](https://docs.djangoproject.com/en/5.2/intro/tutorial02/) for databases, models, migrations, and admin.
