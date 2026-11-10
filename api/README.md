# Weather CLI

Run `uv run api` and enter `latitude,longitude`, for example `51.5,-0.1`.
Run tests with `uv run pytest`.

Weather comes from Open-Meteo. A separate Photon location provider looks up a
nearby place name and uses it as the location in the weather output. Names are
approximate; if no place is found or the lookup fails, weather is still shown
with the coordinates.

Location data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).
The [Photon public demo](https://github.com/komoot/photon#demo-server) is intended
for reasonable request volumes and has no availability guarantee.
