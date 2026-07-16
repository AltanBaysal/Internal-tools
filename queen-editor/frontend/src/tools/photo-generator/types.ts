/** One scene = one generated photo. Position (001..N) is derived from array
    index, so deleting/reordering renumbers automatically (design rule). */
export interface Scene {
  id: string;
  prompt: string;
}

export type Mode = "Tekil" | "Liste";

/** What the editor is focused on: an existing scene, the "add new" tile, or nothing. */
export type Selection = { kind: "scene"; id: string } | { kind: "add" } | { kind: "none" };

/** Active generation, mapped to the design's "Üretiliyor" state. */
export type Generating = null | { kind: "new" } | { kind: "regen"; id: string };
