import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base "./" -> assets load with relative paths, so Flask can serve dist from "/".
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: { outDir: "dist" },
});
