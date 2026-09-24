import { useCallback, useEffect, useRef, useState } from "react";

import {
  listReferences,
  referenceUrl,
  removeReference,
  saveReferenceOrder,
  uploadReferences,
} from "../../shared/api.js";
import ConfirmModal from "../../shared/ConfirmModal.jsx";
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Mono, Note } from "../../vendor/kit.jsx";
import { PhotoGlyph, SoundGlyph, VideoGlyph } from "./glyphs.jsx";

// The three rows, in the order the pool is read in. The words are the user's; the keys are H3's
// own labels, which is what the server answers with.
const ROWS = [
  { kind: "picture", title: "Fotoğraflar", Glyph: PhotoGlyph },
  { kind: "video", title: "Videolar", Glyph: VideoGlyph },
  { kind: "audio", title: "Sesler", Glyph: SoundGlyph },
];

// The pool in the middle, in place of the cards: the design's own room around it.
const PANEL = {
  padding: "24px 32px 48px",
  display: "flex",
  flexDirection: "column",
  gap: 14,
};

const TILES = { display: "flex", flexWrap: "wrap", gap: 6 };
const TILE = { position: "relative", width: 68, display: "flex", flexDirection: "column", gap: 2 };
const FRAME = { width: 68, height: 48, objectFit: "cover", background: "var(--bg-2)",
                border: "1px solid var(--border)", display: "block" };
const BIN = { position: "absolute", top: 2, right: 2, width: 16, height: 16, lineHeight: "14px",
              padding: 0, fontSize: 11, background: "var(--bg)", border: "1px solid var(--border)",
              color: "var(--ink-2)", cursor: "pointer" };
// A slot with nothing in it: drawn, because the user has to see the hole to drag it closed.
const HOLE = { width: 68, height: 48, border: "1px dashed var(--border)",
               background: "var(--bg-2)" };

/** How long a clip runs, in the user's own numbers. */
function ran(seconds) {
  return `${seconds.toFixed(1).replace(".", ",")} sn`;
}

/** One kind's row as places rather than as files: a slot nobody stands in comes back as null.
 *
 * The server says which slot each reference holds and says nothing about the empty ones -- there is
 * nothing to say. The row is as long as its last reference. */
function slotted(rows) {
  const last = rows.reduce((high, row) => Math.max(high, row.slot), 0);
  return Array.from({ length: last }, (_, index) =>
    rows.find((row) => row.slot === index + 1) || null);
}

function Tile({ project, row, onRemove, onDragStart, onDrop }) {
  const url = referenceUrl(project, row.name);
  return (
    // Draggable from the start, not after a hold: the browser decides at mousedown whether a press
    // may become a drag, so a tile armed later is never a drag source at all (the gallery's own
    // lesson).
    <div style={TILE} data-reference={row.name} draggable
         onDragStart={onDragStart}
         onDragOver={(e) => e.preventDefault()}
         onDrop={onDrop}>
      {row.kind === "picture" && <img src={url} alt={row.name} style={FRAME} />}
      {/* Muted and controlless: the browser draws the opening frame, which is all a tile needs. */}
      {row.kind === "video" && <video src={url} muted preload="metadata" style={FRAME} />}
      {row.kind === "audio" && (
        <div style={{ ...FRAME, display: "flex", alignItems: "center", justifyContent: "center",
                      color: "var(--ink-3)" }}>
          <SoundGlyph />
        </div>
      )}
      <button type="button" aria-label={`${row.name} referansını sil`} style={BIN}
              className="wf-stroke" onClick={() => onRemove(row.name)}>×</button>
      <Note size={10} style={{ color: "var(--ink-3)", overflow: "hidden",
                               textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        {row.name}
      </Note>
      {row.seconds != null && (
        <Note size={10} style={{ color: "var(--ink-2)" }}>{ran(row.seconds)}</Note>
      )}
    </div>
  );
}

/**
 * The project's reference pool, in the middle in place of the cards while the video panel is on
 * Referanstan (madde 318).
 *
 * It asks for its own pool rather than being handed one: nothing else on this screen has a use for
 * it, and the answer carries the limits it heads its rows with -- so the numbers are never written
 * down twice (madde 298 owns them).
 */
export default function ReferencePanel({ project }) {
  const [pool, setPool] = useState({ references: [], limits: {} });
  const [error, setError] = useState(null);
  const [asking, setAsking] = useState(null);
  const [busy, setBusy] = useState(false);
  // What is being dragged. A ref and not state: it is a gesture in flight, nothing is drawn from
  // it, and a drop has to read what the drag start wrote however the browser batched the two.
  const drag = useRef(null);

  const load = useCallback(() => {
    listReferences(project).then(setPool).catch((err) => setError(err.message));
  }, [project]);

  useEffect(load, [load]);

  async function handlePick(event) {
    const files = Array.from(event.target.files || []);
    // The same file picked twice in a row has to arrive twice: without this the input holds the
    // old value and fires nothing.
    event.target.value = "";
    if (!files.length) return;
    setError(null);
    setBusy(true);
    try {
      setPool(await uploadReferences(project, files));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  /** Where the drag ends: the row is rebuilt as a sequence, and the whole of it goes down.
   *
   * The slots are not sent -- a place in the list IS the slot. The dead names that were holding
   * empty slots are simply not in what the screen shows, which is how a gap closes.
   */
  async function handleDrop(kind, index) {
    const dragged = drag.current;
    drag.current = null;
    if (!dragged || dragged.kind !== kind) return;
    const names = pool.references.filter((row) => row.kind === kind).map((row) => row.name);
    const from = names.indexOf(dragged.name);
    const placed = names.filter((name) => name !== dragged.name);
    // Count the hole as a place: dropping into it is what fills it.
    placed.splice(Math.min(index, placed.length), 0, dragged.name);
    if (from === -1 || placed.join() === names.join()) return;
    try {
      setPool(await saveReferenceOrder(project, { [kind]: placed }));
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleRemove() {
    setBusy(true);
    try {
      setPool(await removeReference(project, asking));
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
      setAsking(null);
    }
  }

  return (
    <div style={PANEL}>
      {ROWS.map(({ kind, title, Glyph }) => {
        const rows = pool.references.filter((one) => one.kind === kind);
        return (
          <div key={kind} style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--ink-3)" }}>
              <Glyph />
              <Mono size={11} style={{ color: "var(--ink-2)" }}>
                {`${title} ${rows.length}/${pool.limits[kind] ?? 0}`}
              </Mono>
            </div>
            <div style={TILES}>
              {slotted(rows).map((row, index) => (row ? (
                <Tile key={row.name} project={project} row={row} onRemove={setAsking}
                      onDragStart={() => { drag.current = { kind, name: row.name }; }}
                      onDrop={() => handleDrop(kind, index)} />
              ) : (
                /* The hole a deleted reference left. It is a drop target too: dragging into it is
                   how the user closes it (madde 300). */
                <div key={`boş-${index}`} aria-label={`${index + 1}. yuva boş`} style={HOLE}
                     onDragOver={(e) => e.preventDefault()}
                     onDrop={() => handleDrop(kind, index)} />
              )))}
            </div>
          </div>
        );
      })}

      {/* A label rather than a button: the browser's own picker, wearing the app's button. */}
      <label className="wf-btn wf-btn--sm" style={{ justifyContent: "center", cursor: "pointer" }}>
        {busy ? "Yükleniyor…" : "Ekle"}
        <input type="file" multiple aria-label="Ekle" disabled={busy}
               style={{ display: "none" }} onChange={handlePick} />
      </label>

      {error && <StatusErrorCard text={error} />}

      {asking && (
        <ConfirmModal title={`${asking} silinsin mi?`}
                      body="Referans havuzdan kalıcı olarak silinir — bu geri alınamaz."
                      confirmLabel="Sil" busyLabel="Siliniyor…" danger busy={busy}
                      onCancel={() => setAsking(null)} onConfirm={handleRemove} />
      )}
    </div>
  );
}
