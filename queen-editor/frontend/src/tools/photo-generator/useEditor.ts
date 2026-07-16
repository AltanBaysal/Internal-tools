import { useMemo, useRef, useState } from "react";
import type { Generating, Mode, Scene, Selection } from "./types";

let idCounter = 0;
const newId = () => `s${++idCounter}`;

// Seed a few scenes so the populated states (selection, timeline, scrollbar) are
// visible on first load. Delete them all to reach the empty-editor state.
const SEED: Scene[] = [
  "gün batımında deniz kenarında oturan kadın, sıcak tonlar, film grain",
  "kahve fincanı, ahşap masa, soft ışık, üstten görünüm",
  "neon ışıklı dar sokak, yağmur, yansımalar, gece",
  "minimal beyaz oda, tek sandalye, doğal ışık",
].map((prompt) => ({ id: newId(), prompt }));

const GEN_MS = 1300; // mock generation duration (no backend yet)

/** Single source of truth for the photo-generator editor. Plain hooks for now —
    swap for a store later without touching the views. */
export function useEditor() {
  const [scenes, setScenes] = useState<Scene[]>(SEED);
  const [selection, setSelection] = useState<Selection>({ kind: "scene", id: SEED[0].id });
  const [generating, setGenerating] = useState<Generating>(null);
  const [mode, setMode] = useState<Mode>("Tekil");
  const [draft, setDraft] = useState<string>(SEED[0].prompt);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const timer = useRef<number | null>(null);

  const selectedIdx = useMemo(
    () => (selection.kind === "scene" ? scenes.findIndex((s) => s.id === selection.id) : -1),
    [selection, scenes]
  );

  function selectScene(id: string) {
    if (generating) return;
    setSelection({ kind: "scene", id });
    setDraft(scenes.find((s) => s.id === id)?.prompt ?? "");
  }

  function startAdd() {
    if (generating) return;
    setSelection({ kind: "add" });
    setDraft("");
  }

  function finishAfterDelay(fn: () => void) {
    if (timer.current) window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => {
      fn();
      setGenerating(null);
      timer.current = null;
    }, GEN_MS);
  }

  /** Üret: regenerate the selected scene, or append a new one. */
  function generate() {
    if (generating) return;
    const prompt = draft.trim();
    if (!prompt) return;

    if (selection.kind === "scene") {
      const id = selection.id;
      setGenerating({ kind: "regen", id });
      finishAfterDelay(() => setScenes((prev) => prev.map((s) => (s.id === id ? { ...s, prompt } : s))));
    } else {
      const scene: Scene = { id: newId(), prompt };
      setGenerating({ kind: "new" });
      finishAfterDelay(() => {
        setScenes((prev) => [...prev, scene]);
        setSelection({ kind: "scene", id: scene.id });
      });
    }
  }

  function requestDelete(id: string) {
    if (generating) return;
    setDeleteId(id);
  }
  function cancelDelete() {
    setDeleteId(null);
  }
  function confirmDelete() {
    if (!deleteId) return;
    setScenes((prev) => {
      const next = prev.filter((s) => s.id !== deleteId);
      // Move selection to a sensible neighbour (or empty/add).
      if (selection.kind === "scene" && selection.id === deleteId) {
        const idx = prev.findIndex((s) => s.id === deleteId);
        const neighbour = next[Math.min(idx, next.length - 1)];
        if (neighbour) {
          setSelection({ kind: "scene", id: neighbour.id });
          setDraft(neighbour.prompt);
        } else {
          setSelection({ kind: "none" });
          setDraft("");
        }
      }
      return next;
    });
    setDeleteId(null);
  }

  /** Move a scene from one position to another (drag-drop or number edit).
      Position == array index, so numbering renumbers automatically. */
  function reorder(fromIdx: number, toIdx: number) {
    if (generating) return;
    setScenes((prev) => {
      if (fromIdx < 0 || fromIdx >= prev.length) return prev;
      const to = Math.max(0, Math.min(prev.length - 1, toIdx));
      if (to === fromIdx) return prev;
      const next = prev.slice();
      const [moved] = next.splice(fromIdx, 1);
      next.splice(to, 0, moved);
      return next;
    });
    // Selection follows by id (set in scene objects), so no extra work needed.
  }

  function goto(delta: number) {
    if (generating || selectedIdx < 0) return;
    const next = scenes[selectedIdx + delta];
    if (next) selectScene(next.id);
  }

  return {
    scenes,
    selection,
    selectedIdx,
    generating,
    mode,
    draft,
    deleteId,
    setMode,
    setDraft,
    selectScene,
    startAdd,
    generate,
    requestDelete,
    cancelDelete,
    confirmDelete,
    reorder,
    goto,
  };
}

export type EditorState = ReturnType<typeof useEditor>;
