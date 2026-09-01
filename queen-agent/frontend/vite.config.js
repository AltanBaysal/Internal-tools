import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base "/" -> assets load from an absolute path, which the nested routes need. Flask serves dist at
// the root and falls back to index.html for unknown paths, so a relative "./assets/..." would
// resolve against /projects/<id>/ on a reload, hit that fallback and load index.html as the module
// script -- a blank page.
export default defineConfig({
  plugins: [react()],
  base: "/",
  build: { outDir: "dist" },
  // Dev only: the UI runs on Vite's own server and talks to Flask across ports. The built app is
  // served by Flask itself, so this proxy never applies in use.
  server: { proxy: { "/api": "http://127.0.0.1:8100" } },
  // Vitest reuses this config, so tests get the same JSX transform as the build. Test files live
  // next to their source and are never imported, so they stay out of dist/.
  test: {
    environment: "jsdom",
    setupFiles: "./src/test-setup.js",
    // A worker carries a jsdom of its own, so a worker per core leaves thirty-five environments
    // queuing for one machine's memory. A test that reads 99ms alone read 5107ms in that crowd,
    // and the timeout measures the wall clock, so it called a finished test stuck. Measured on 1
    // September: every core 18-22s and red, two workers 20.6s and green, half 8.3s and green --
    // fewer workers is both steadier and faster. A proportion rather than a count, because a
    // number that fits this machine would bind every other one.
    maxWorkers: "50%",
  },
});
