import {defineConfig} from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: 'weather/static/weather',
    emptyOutDir: false,
    lib: {entry: 'weather/static/weather/app/main.js', formats: ['es'], fileName: () => 'app.js'},
  },
});
