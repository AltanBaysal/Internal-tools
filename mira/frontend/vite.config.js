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
  },
});
