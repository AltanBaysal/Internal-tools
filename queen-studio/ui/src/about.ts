import { info } from "./api/openapi.json";
import type { components } from "./api/schema";

// The UI calls no endpoint yet; Health's type is borrowed as the one consumer that proves the
// generated types reach tsc. Rename a field in the core and the build stops here.
type About = Pick<components["schemas"]["Health"], "app" | "version">;

/** "queen-studio", "1.0.0" -> "Queen Studio V1". */
export function appTitle({ app, version }: About): string {
  const words = app.split("-").map((word) => word.charAt(0).toUpperCase() + word.slice(1));
  return `${words.join(" ")} V${version.split(".")[0]}`;
}

// The name and version are written once, in core/about.py, and reach the UI in the OpenAPI document.
export const TITLE = appTitle({ app: info.title, version: info.version });
