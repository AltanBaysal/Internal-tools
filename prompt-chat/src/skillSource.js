import { loadSkills } from "./skills.js";

// Vite inlines every SKILL.md at build time, which is what lets a page with no backend read files
// that live in the repo. `eager` keeps it synchronous, so the list is ready before the first
// render and no screen needs a loading state.
const files = import.meta.glob("../skills/*/SKILL.md", {
  query: "?raw",
  import: "default",
  eager: true,
});

export const { skills, errors } = loadSkills(files);
