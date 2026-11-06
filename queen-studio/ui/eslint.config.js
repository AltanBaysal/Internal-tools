import js from "@eslint/js";
import { defineConfig, globalIgnores } from "eslint/config";
import tseslint from "typescript-eslint";

export default defineConfig([
  // The build's output and the types generated from the core's OpenAPI document are nobody's to edit.
  globalIgnores(["dist", "src/api/schema.d.ts"]),
  js.configs.recommended,
  tseslint.configs.strict,
]);
