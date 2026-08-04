import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base "/" -> assets load from an absolute path, which is what the nested routes need. Flask
// serves dist at the root and falls back to index.html for unknown paths, so a relative
// "./assets/..." would resolve against /projects/<name>/ on a reload, hit that fallback, and load
// index.html as the module script -- a blank page. Covered by test_static.py.
export default defineConfig({
  plugins: [react()],
  base: "/",
  build: { outDir: "dist" },
  // Vitest reuses this config, so tests get the same JSX transform and module resolution as the
  // build. Test files live next to their source and are never imported, so they stay out of dist/.
  test: {
    environment: "jsdom",
    setupFiles: "./src/test-setup.js",
  },
});
