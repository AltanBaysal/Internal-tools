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
    // A worker carries a jsdom of its own, so a worker per core leaves every test file's
    // environment queuing for one machine's memory. In queen-agent's suite a test that reads 99ms
    // alone read 5107ms in that crowd, and the timeout measures the wall clock, so it called a
    // finished test stuck. Measured there on 1 September: every core 18-22s and red, half 8.3s and
    // green. No red was seen on this side, but the configuration, the file count and the machine
    // are the same, and the two tools do not carry different rules without a reason. A proportion
    // rather than a count, because a number that fits one machine would bind every other one.
    maxWorkers: "50%",
  },
});
