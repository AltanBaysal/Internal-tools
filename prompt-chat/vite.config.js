import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vitest reuses this config, so tests get the same JSX transform as the dev server. Test files sit
// next to their source and are never imported by the app.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: "./src/test-setup.js",
  },
});
