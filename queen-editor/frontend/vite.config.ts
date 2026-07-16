import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Relative base so the built app works under any subpath (e.g. a Colab/Cloudflare
// tunnel), mirroring how the notebooks expose ComfyUI.
export default defineConfig({
  base: "./",
  plugins: [react()],
  server: { port: 5173 },
});
