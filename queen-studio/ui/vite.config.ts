import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// The core serves dist at `/` (core/server.py), so the default base and outDir hold. Vitest reuses
// this config, so tests get the build's JSX transform.
export default defineConfig({
  plugins: [react()],
  test: { environment: "jsdom" },
});
