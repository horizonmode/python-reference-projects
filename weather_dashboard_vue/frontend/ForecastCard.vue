<script setup>
defineProps({forecast: {type: Object, required: true}, busy: Boolean});
defineEmits(['edit', 'delete']);
</script>

<template>
  <article class="forecast-card">
    <p class="eyebrow">LATEST SAVED FORECAST</p>
    <h2>{{ forecast.location_name }}</h2>
    <p class="temperature">{{ forecast.temperature }} <span>°C</span></p>
    <p>{{ forecast.description }}</p>
    <dl>
      <div><dt>Humidity</dt><dd>{{ forecast.humidity }}%</dd></div>
      <div><dt>Wind</dt><dd>{{ forecast.wind_speed }} km/h</dd></div>
      <div><dt>Coordinates</dt><dd>{{ forecast.latitude }}, {{ forecast.longitude }}</dd></div>
    </dl>
    <p class="muted">Saved {{ new Date(forecast.fetched_at).toLocaleString() }}</p>
    <div class="actions">
      <button type="button" :disabled="busy" @click="$emit('edit', forecast)">Edit forecast</button>
      <button type="button" class="secondary" :disabled="busy" @click="$emit('delete', forecast)">Delete</button>
    </div>
  </article>
</template>
