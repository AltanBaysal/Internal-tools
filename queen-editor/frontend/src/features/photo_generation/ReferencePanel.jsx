import { useCallback, useEffect, useRef, useState } from "react";

import {
  listReferences,
  referenceUrl,
  removeReference,
  saveReferenceOrder,
  uploadReferences,
} from "../../shared/api.js";
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Mono, Note } from "../../vendor/kit.jsx";
import { PhotoGlyph, PlusGlyph, SoundGlyph, VideoGlyph } from "./glyphs.jsx";

// The three rows, in the order the pool is read in. The words are the user's; the keys are H3's
// own labels, which is what the server answers with. `accept` only narrows the browser's picker --
// it can be switched to every file, and which row a file may go in is the server's to say
// (FOUNDATION 4).
const ROWS = [
  { kind: "picture", title: "Fotoğraflar", Glyph: PhotoGlyph, accept: "image/*",
    picker: "fotoğraf ekle" },
  { kind: "video", title: "Videolar", Glyph: VideoGlyph, accept: "video/*", picker: "video ekle" },
  { kind: "audio", title: "Sesler", Glyph: SoundGlyph, accept: "audio/*", picker: "ses ekle" },
];

// The pool in the middle, in place of the cards: the design's own room around it.
const PANEL = {
  padding: "24px 32px 48px",
  display: "flex",
  flexDirection: "column",
  gap: 28,
};

// The design's own measures (proje-ekrani-tam: .rv-*).
const TILES = { display: "flex", flexWrap: "wrap", gap: 12 };
const TILE = { position: "relative", width: 144, display: "flex", flexDirection: "column", gap: 4 };
const FRAME = { width: 144, height: 108, objectFit: "cover", background: "var(--bg-2)",
                border: "1px solid var(--border)", borderRadius: "var(--r-sm)",
                boxSizing: "border-box", display: "block" };
const BIN = { position: "absolute", top: 6, right: 6, width: 18, height: 18, lineHeight: "16px",
              padding: 0, fontSize: 12, background: "var(--bg)", border: "1px solid var(--border)",
              color: "var(--ink-2)", cursor: "pointer", borderRadius: 3 };
// The slot number is the one a prompt calls the reference by, so it sits on the picture.
const SEQ = { position: "absolute", top: 6, left: 6, background: "rgba(10, 8, 7, .75)" };
// The card after a row's last reference is where a file goes in: dashed, because nothing is
// there yet.
const ADD = { width: 144, height: 108, border: "1px dashed var(--border)",
              background: "var(--bg-2)", borderRadius: "var(--r-sm)", boxSizing: "border-box",
              display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
              fontSize: 12, color: "var(--ink-3)" };
// The gallery's own lift for the tile in flight (Gallery.jsx, DRAGGED -- the design's .dragged).
const DRAGGED = { transform: "rotate(-3deg) scale(1.04) translate(14px, -10px)",
                  filter: "drop-shadow(0 12px 24px rgba(0,0,0,.55))", zIndex: 5,
                  position: "relative" };
// Where the tile in flight would land: the tile under the pointer gives its place to the gallery's
// dashed slot, drawn over its face at the face's own size (the design's .rv-tile.is-over::before).
const SLOT = { position: "absolute", top: 0, left: 0, width: 144, height: 108,
               border: "2px dashed var(--accent)", borderRadius: "var(--r-sm)",
               background: "var(--bg-3)", boxSizing: "border-box" };

/** How long a clip runs, in the user's own numbers. */
function ran(seconds) {
  return `${seconds.toFixed(1).replace(".", ",")} sn`;
}

function Tile({ project, row, lifted, open, onRemove, onDragStart, onDragOver, onDrop,
                onDragEnd }) {
  const url = referenceUrl(project, row.name);
  // Under the slot the words keep their place unseen, so the row keeps its height.
  const unseen = open ? { visibility: "hidden" } : null;
  return (
    // Draggable from the start, not after a hold: the browser decides at mousedown whether a press
    // may become a drag, so a tile armed later is never a drag source at all (the gallery's own
    // lesson).
    <div style={lifted ? { ...TILE, ...DRAGGED } : TILE} data-reference={row.name} draggable
         onDragStart={onDragStart}
         onDragOver={onDragOver}
         onDrop={onDrop}
         onDragEnd={onDragEnd}>
      {/* Not draggable itself, as in the gallery: otherwise the browser drags the bare picture
          instead of the tile. */}
      {row.kind === "picture" && (
        <img src={url} alt={row.name} style={FRAME} draggable={false} />
      )}
      {/* Muted and controlless: the browser draws the opening frame, which is all a tile needs. */}
      {row.kind === "video" && <video src={url} muted preload="metadata" style={FRAME} />}
      {row.kind === "audio" && (
        <div style={{ ...FRAME, display: "flex", alignItems: "center", justifyContent: "center",
                      color: "var(--ink-3)" }}>
          <SoundGlyph />
        </div>
      )}
      {/* wf-seq's own look, not the kit's Seq: that one pads to 001, and a prompt says <Picture 1>. */}
      <span className="wf-seq" style={SEQ}>{row.slot}</span>
      <button type="button" aria-label={`${row.name} referansını sil`} style={BIN}
              className="wf-stroke" onClick={() => onRemove(row.name)}>×</button>
      <Note size={11} style={{ color: "var(--ink-3)", overflow: "hidden",
                               textOverflow: "ellipsis", whiteSpace: "nowrap", ...unseen }}>
        {row.name}
      </Note>
      {row.seconds != null && (
        <Note size={11} style={{ color: "var(--ink-2)", ...unseen }}>{ran(row.seconds)}</Note>
      )}
      {/* Last, so it stands over the face, the number and the ×. */}
      {open && <div style={SLOT} />}
    </div>
  );
}

/** A row's way in, after its last reference until the row holds all it may: a press opens a picker
 * for this row's kind, one file at a time (madde 320).
 *
 * Not a label around the input: a label's words name what it holds, and every card says Ekle while
 * each picker is named for its own kind. The input stands after the card, not inside it: the click
 * the card hands the input would bubble back into the card's own handler. */
function AddCard({ kind, accept, picker, uploading, onPick }) {
  const input = useRef(null);
  return (
    <>
      {/* A locked card stops looking pressable (the design's .rv-add.is-off). */}
      <div data-add={kind} style={{ ...ADD, cursor: uploading === null ? "pointer" : "default" }}
           onClick={() => input.current.click()}>
        {uploading === kind
          ? <><span className="qe-spinner" aria-hidden="true" /> Yükleniyor…</>
          : <><PlusGlyph size={14} /> Ekle</>}
      </div>
      {/* Any file on its way holds every card: two in flight would each be weighed against a pool
          without the other. */}
      <input ref={input} type="file" accept={accept} aria-label={picker}
             disabled={uploading !== null} style={{ display: "none" }} onChange={onPick} />
    </>
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
  // The kind of the row whose file is on its way, or null.
  const [uploading, setUploading] = useState(null);
  // What is being dragged. A ref and not state: a drop has to read what the drag start wrote
  // however the browser batched the two.
  const drag = useRef(null);
  // What the drag draws, the gallery's way: the tile in flight, and the tile whose place opened
  // under the pointer. Names, because a row is keyed by them.
  const [lifted, setLifted] = useState(null);
  const [over, setOver] = useState(null);

  const load = useCallback(() => {
    listReferences(project).then(setPool).catch((err) => setError(err.message));
  }, [project]);

  useEffect(load, [load]);

  async function handlePick(kind, event) {
    const files = Array.from(event.target.files || []);
    // The same file picked twice in a row has to arrive twice: without this the input holds the
    // old value and fires nothing.
    event.target.value = "";
    if (!files.length) return;
    setError(null);
    setUploading(kind);
    try {
      setPool(await uploadReferences(project, files, kind));
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(null);
    }
  }

  function handleDragStart(kind, name) {
    drag.current = { kind, name };
    setLifted(name);
  }

  /** Only a tile of the dragged one's own row opens a place (madde 322). Anywhere else the default
   * stands, so the browser shows no drop and never fires one -- another row, and the Ekle card,
   * which listens to no drag at all. */
  function handleDragOver(kind, name, event) {
    if (drag.current?.kind !== kind) return;
    event.preventDefault();
    setOver(name);
  }

  /** Dropped or let go, the drag is over: nothing is lifted and no place is open. */
  function endDrag() {
    drag.current = null;
    setLifted(null);
    setOver(null);
  }

  /** Where the drag ends: the row is rebuilt as a sequence, and the whole of it goes down.
   *
   * The slots are not sent -- a place in the list IS the slot.
   */
  async function handleDrop(kind, index) {
    const dragged = drag.current;
    endDrag();
    if (!dragged || dragged.kind !== kind) return;
    const names = pool.references.filter((row) => row.kind === kind).map((row) => row.name);
    const from = names.indexOf(dragged.name);
    const placed = names.filter((name) => name !== dragged.name);
    placed.splice(index, 0, dragged.name);
    if (from === -1 || placed.join() === names.join()) return;
    try {
      setPool(await saveReferenceOrder(project, { [kind]: placed }));
    } catch (err) {
      setError(err.message);
    }
  }

  /** × is the whole delete. No window asks first: the user's call in madde 321, since a reference
   * is a copy they put back with one Ekle. What comes back is the pool with the ones after it
   * moved up. */
  async function handleRemove(name) {
    try {
      setPool(await removeReference(project, name));
      // The next pick or delete clears a refusal (madde 320).
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div style={PANEL}>
      {/* Above the rows: where the eye is when a pick comes back refused. */}
      {error && <StatusErrorCard text={error} />}

      {ROWS.map(({ kind, title, Glyph, accept, picker }) => {
        const rows = pool.references.filter((one) => one.kind === kind);
        return (
          <div key={kind} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--ink-3)" }}>
              <Glyph />
              <Mono size={12} style={{ color: "var(--ink-2)" }}>
                {`${title} ${rows.length}/${pool.limits[kind] ?? 0}`}
              </Mono>
            </div>
            <div style={TILES}>
              {rows.map((row, index) => (
                <Tile key={row.name} project={project} row={row} onRemove={handleRemove}
                      lifted={lifted === row.name}
                      // The tile in flight opens nothing over itself: that place is its own.
                      open={over === row.name && lifted !== row.name}
                      onDragStart={() => handleDragStart(kind, row.name)}
                      onDragOver={(event) => handleDragOver(kind, row.name, event)}
                      onDrop={() => handleDrop(kind, index)}
                      onDragEnd={endDrag} />
              ))}
              {rows.length < (pool.limits[kind] ?? 0) && (
                <AddCard kind={kind} accept={accept} picker={picker} uploading={uploading}
                         onPick={(event) => handlePick(kind, event)} />
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
