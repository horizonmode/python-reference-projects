import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';
import vm from 'node:vm';
import {parse, compileScript} from '@vue/compiler-sfc';

const sfc = await readFile(new URL('../frontend/App.vue', import.meta.url), 'utf8');
const {descriptor} = parse(sfc);
const source = compileScript(descriptor, {id: 'app-test'}).content;
const saved = {id: 1, location_name: 'Frome', latitude: 51, longitude: -2,
  temperature: 12, humidity: 70, wind_speed: 8, description: 'Cloudy',
  fetched_at: '2026-11-22T10:00:00+00:00'};

// Exercise application state and the fetch contract without a browser or Vue CDN.
async function boot() {
  const calls = [];
  let config;
  let reply = {ok: true, status: 200, body: {}};
  let replies = [];
  const initial = {forecasts: [saved], csrfToken: 'test-token',
    count: 1, next: null, previous: null,
    forecastsUrl: '/api/forecasts/', fetchUrl: '/api/forecasts/fetch/'};
  const context = vm.createContext({
    document: {getElementById: () => ({textContent: JSON.stringify(initial), focus() {}})},
    fetch: async (url, options) => {
      calls.push({url, options});
      const current = replies.shift() ?? reply;
      return {ok: current.ok, status: current.status, json: async () => current.body};
    },
  });
  const module = new vm.SourceTextModule(source, {context});
  await module.link(async specifier => {
    return new vm.SyntheticModule(['default'], function () {
      this.setExport('default', {});
    }, {context});
  });
  await module.evaluate();
  config = module.namespace.default;
  const app = config.data();
  for (const [key, value] of Object.entries(config.methods)) app[key] = value.bind(app);
  app.$nextTick = callback => callback();
  return {app, calls, reply: value => {
    if (Array.isArray(value)) replies = value;
    else reply = value;
  }};
}

const page = (forecasts, extra = {}) => ({ok: true, status: 200,
  body: {forecasts, count: forecasts.length, next: null, previous: null, ...extra}});

test('bootstrap uses embedded forecasts without fetching', async () => {
  const {app, calls} = await boot();
  assert.equal(app.forecasts[0].location_name, 'Frome');
  assert.equal(calls.length, 0);
});

test('live lookup sends CSRF and inserts the returned record', async () => {
  const {app, calls, reply} = await boot();
  const forecast = {...saved, id: 2, fetched_at: '2026-11-22T11:00:00+00:00'};
  reply([{ok: true, status: 201, body: {forecast}}, page([forecast, saved])]);
  await app.lookup();
  assert.equal(calls[0].url, '/api/forecasts/fetch/');
  assert.equal(calls[0].options.headers['X-CSRFToken'], 'test-token');
  assert.equal(calls[0].options.method, 'POST');
  assert.equal(app.forecasts[0].id, 2);
  assert.equal(app.busy, false);
});

test('manual create and edit use POST and PUT without read-only fields', async () => {
  const {app, calls, reply} = await boot();
  reply([{ok: true, status: 201, body: {forecast: {...saved, id: 2}}}, page([{...saved, id: 2}, saved])]);
  app.edit();
  app.draft.location_name = 'Bath';
  await app.save();
  assert.equal(calls[0].options.method, 'POST');
  app.edit(saved);
  app.draft.temperature = 20;
  reply([{ok: true, status: 200, body: {forecast: {...saved, temperature: 20}}}, page([{...saved, temperature: 20}])]);
  await app.save();
  assert.equal(calls[2].url, '/api/forecasts/1/');
  assert.equal(calls[2].options.method, 'PUT');
  assert.equal('id' in JSON.parse(calls[2].options.body), false);
  assert.equal(app.forecasts.find(item => item.id === 1).temperature, 20);
});

test('deletion removes state only after successful response', async () => {
  const {app, reply} = await boot();
  app.pendingDelete = saved;
  reply({ok: false, status: 403, body: {error: 'Forbidden'}});
  await app.remove();
  assert.equal(app.forecasts.length, 1);
  assert.equal(app.error, 'Forbidden');
  reply([{ok: true, status: 204}, page([])]);
  await app.remove();
  assert.equal(app.forecasts.length, 0);
  assert.equal(app.pendingDelete, null);
  assert.equal(app.latestForecast, null);
});

test('validation keeps the editor open and exposes field errors', async () => {
  const {app, reply} = await boot();
  app.edit(saved);
  reply({ok: false, status: 400, body: {error: 'Check fields', errors: {humidity: ['Out of range']}}});
  await app.save();
  assert.equal(app.editorOpen, true);
  assert.equal(app.errors.humidity[0], 'Out of range');
  assert.equal(app.busy, false);
});

test('paging history keeps the latest card and uses the returned links', async () => {
  const {app, calls, reply} = await boot();
  reply(page([{...saved, id: 2, location_name: 'Older'}], {
    count: 21, previous: '/api/forecasts/?page=1',
  }));
  await app.refresh('/api/forecasts/?page=2');
  assert.equal(calls[0].url, '/api/forecasts/?page=2');
  assert.equal(app.forecasts[0].location_name, 'Older');
  assert.equal(app.latestForecast.location_name, 'Frome');
  assert.equal(app.count, 21);
  assert.equal(app.previousPage, '/api/forecasts/?page=1');
});
