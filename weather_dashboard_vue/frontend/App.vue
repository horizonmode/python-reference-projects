<script>
import ForecastCard from './ForecastCard.vue';

// This is the initial page's data, not a second HTTP request.
const initial = JSON.parse(document.getElementById('initial-data').textContent);
const emptyForecast = () => ({
  location_name: '', latitude: 51.231, longitude: -2.3218,
  temperature: 0, humidity: 0, wind_speed: 0, description: '',
});
const fields = [
  {name: 'location_name', label: 'Location', type: 'text', maxlength: 200},
  {name: 'latitude', label: 'Latitude', type: 'number', min: -90, max: 90},
  {name: 'longitude', label: 'Longitude', type: 'number', min: -180, max: 180},
  {name: 'temperature', label: 'Temperature (°C)', type: 'number'},
  {name: 'humidity', label: 'Humidity (%)', type: 'number', min: 0, max: 100},
  {name: 'wind_speed', label: 'Wind (km/h)', type: 'number', min: 0},
  {name: 'description', label: 'Conditions', type: 'text', maxlength: 200},
];

export default {
  components: {ForecastCard},
  data: () => ({
    forecasts: initial.forecasts, coordinates: {latitude: 51.231, longitude: -2.3218},
    latestForecast: initial.forecasts[0] ?? null,
    count: initial.count, nextPage: initial.next, previousPage: initial.previous,
    busy: false, error: '', errors: {}, message: '', editorOpen: false,
    editingId: null, draft: emptyForecast(), fields, pendingDelete: null,
  }),
  computed: {
    latest() { return this.latestForecast; },
  },
  methods: {
    async request(url, method = 'GET', data) {
      const response = await fetch(url, {
        method, credentials: 'same-origin',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': initial.csrfToken},
        ...(data === undefined ? {} : {body: JSON.stringify(data)}),
      });
      if (response.status === 204) return null;
      const result = await response.json().catch(() => ({}));
      if (!response.ok) {
        this.errors = result.errors ?? {};
        throw new Error(result.error ?? `Request failed (${response.status}). Please try again.`);
      }
      return result;
    },
    async perform(action) {
      if (this.busy) return;
      this.busy = true; this.error = ''; this.errors = {}; this.message = '';
      try { await action(); }
      catch (error) { this.error = error.message; }
      finally { this.busy = false; }
    },
    upsert(forecast) {
      this.forecasts = [...this.forecasts.filter(item => item.id !== forecast.id), forecast]
        .sort((a, b) => b.fetched_at.localeCompare(a.fetched_at) || b.id - a.id);
      if (!this.latestForecast || this.latestForecast.id === forecast.id ||
          forecast.fetched_at > this.latestForecast.fetched_at ||
          (forecast.fetched_at === this.latestForecast.fetched_at && forecast.id > this.latestForecast.id)) {
        this.latestForecast = forecast;
      }
    },
    async loadPage(url = initial.forecastsUrl) {
      const result = await this.request(url);
      this.forecasts = result.forecasts;
      this.count = result.count;
      this.nextPage = result.next;
      this.previousPage = result.previous;
      if (!result.previous) this.latestForecast = result.forecasts[0] ?? null;
    },
    lookup() {
      return this.perform(async () => {
        const result = await this.request(initial.fetchUrl, 'POST', this.coordinates);
        this.upsert(result.forecast); this.message = 'Weather fetched and saved.';
        await this.loadPage();
      });
    },
    refresh(url = initial.forecastsUrl) {
      return this.perform(async () => {
        await this.loadPage(url);
        this.message = 'Forecasts refreshed.';
      });
    },
    edit(forecast = null) {
      this.error = ''; this.errors = {}; this.message = '';
      this.editingId = forecast?.id ?? null;
      this.draft = forecast
        ? Object.fromEntries(fields.map(field => [field.name, forecast[field.name]]))
        : emptyForecast();
      this.editorOpen = true;
      this.$nextTick(() => document.getElementById('editor-location_name').focus());
    },
    save() {
      return this.perform(async () => {
        const url = this.editingId ? `${initial.forecastsUrl}${this.editingId}/` : initial.forecastsUrl;
        const result = await this.request(url, this.editingId ? 'PUT' : 'POST', this.draft);
        this.upsert(result.forecast); this.editorOpen = false;
        this.message = 'Forecast saved.';
        await this.loadPage();
      });
    },
    remove() {
      return this.perform(async () => {
        const id = this.pendingDelete.id;
        await this.request(`${initial.forecastsUrl}${id}/`, 'DELETE');
        this.forecasts = this.forecasts.filter(item => item.id !== id);
        if (this.editingId === id) this.editorOpen = false;
        this.pendingDelete = null; this.message = 'Forecast deleted.';
        await this.loadPage();
      });
    },
  },
};
</script>

<template>
  <div>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p role="status" aria-live="polite">{{ busy ? 'Working…' : message }}</p>
    <section class="panel" aria-labelledby="lookup-heading">
      <h2 id="lookup-heading">Find weather</h2>
      <form @submit.prevent="lookup">
        <fieldset :disabled="busy">
          <div class="form-grid">
            <label>Latitude<input v-model.number="coordinates.latitude" type="number" step="any" min="-90" max="90" required>
              <span v-for="text in errors.latitude" :key="text" class="error">{{ text }}</span></label>
            <label>Longitude<input v-model.number="coordinates.longitude" type="number" step="any" min="-180" max="180" required>
              <span v-for="text in errors.longitude" :key="text" class="error">{{ text }}</span></label>
          </div>
          <button type="submit">Get and save weather</button>
        </fieldset>
      </form>
    </section>
    <ForecastCard v-if="latest" :forecast="latest" :busy="busy" @edit="edit" @delete="pendingDelete = $event" />
    <p v-else class="panel">No saved forecasts yet. Look up coordinates or add a forecast manually.</p>
    <section v-if="pendingDelete" class="panel" aria-labelledby="delete-heading">
      <h2 id="delete-heading">Delete forecast for {{ pendingDelete.location_name }}?</h2>
      <div class="actions"><button type="button" :disabled="busy" @click="remove">Confirm delete</button>
        <button type="button" class="secondary" :disabled="busy" @click="pendingDelete = null">Cancel</button></div>
    </section>
    <section v-if="editorOpen" class="panel" aria-labelledby="editor-heading">
      <h2 id="editor-heading">{{ editingId ? 'Edit forecast' : 'Add forecast' }}</h2>
      <form @submit.prevent="save">
        <fieldset :disabled="busy">
          <div class="form-grid">
            <label v-for="field in fields" :key="field.name" :for="'editor-' + field.name">{{ field.label }}
              <input :id="'editor-' + field.name" v-model="draft[field.name]" :type="field.type"
                :min="field.min" :max="field.max" :maxlength="field.maxlength" step="any" required>
              <span v-for="text in errors[field.name]" :key="text" class="error">{{ text }}</span>
            </label>
          </div>
          <div class="actions"><button type="submit">Save forecast</button>
            <button type="button" class="secondary" @click="editorOpen = false">Cancel</button></div>
        </fieldset>
      </form>
    </section>
    <section class="history" aria-labelledby="history-heading">
      <div class="section-header"><h2 id="history-heading">Saved forecasts ({{ count }})</h2>
        <div class="actions"><button type="button" :disabled="busy" @click="edit()">Add manually</button>
          <button type="button" class="secondary" :disabled="busy" @click="refresh()">Refresh</button></div>
      </div>
      <nav v-if="nextPage || previousPage" class="actions pagination" aria-label="Forecast history pages">
        <button type="button" class="secondary" :disabled="busy || !previousPage" @click="refresh(previousPage)">Previous</button>
        <button type="button" class="secondary" :disabled="busy || !nextPage" @click="refresh(nextPage)">Next</button>
      </nav>
      <div v-if="forecasts.length" class="table-scroll">
        <table><caption>Newest first. Times shown in your local timezone.</caption>
          <thead><tr><th>Saved at</th><th>Location</th><th>Conditions</th><th>°C</th><th>Humidity</th><th>Wind</th><th>Actions</th></tr></thead>
          <tbody><tr v-for="forecast in forecasts" :key="forecast.id">
            <td>{{ new Date(forecast.fetched_at).toLocaleString() }}</td><td>{{ forecast.location_name }}</td>
            <td>{{ forecast.description }}</td><td>{{ forecast.temperature }}</td><td>{{ forecast.humidity }}%</td><td>{{ forecast.wind_speed }} km/h</td>
            <td><div class="actions"><button type="button" class="secondary" :disabled="busy" @click="edit(forecast)" :aria-label="'Edit ' + forecast.location_name">Edit</button>
              <button type="button" class="secondary" :disabled="busy" @click="pendingDelete = forecast" :aria-label="'Delete ' + forecast.location_name">Delete</button></div></td>
          </tr></tbody>
        </table>
      </div>
    </section>
  </div>
</template>
