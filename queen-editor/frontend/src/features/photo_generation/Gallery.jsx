import { useEffect, useState } from "react";

import ConfirmModal from "../../shared/ConfirmModal.jsx";
import { navigate, photoPath } from "../../shared/router.js";
import { Btn, Icon, Mono, Note } from "../../vendor/kit.jsx";
import { Rendering, StatusPill } from "./frame_status.jsx";
import { PlayGlyph, SoundGlyph } from "./glyphs.jsx";
import { lostLayers, owned } from "./layer_words.js";
import { TileImage } from "./TileImage.jsx";

const PAD = { padding: 16 };
const GRID = { display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 12,
               alignItems: "start" };
const EMPTY = {
  minHeight: "60vh",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: 8,
};
// Artboard 05: the badge sits on the photo itself, always visible, never on the caption line.
const BADGE = { position: "absolute", top: 6, right: 6, background: "rgba(10,8,7,.75)",
                color: "var(--ink-2)", padding: "2px 6px", borderRadius: 3, zIndex: 1 };
// Madde 57's third plane: the order badge top right, the state pill top left, and what the frame
// owns bottom right. It says the layer is finished -- an unfinished one is the pill's to tell.
const OWNS = { position: "absolute", bottom: 6, right: 6, display: "flex", alignItems: "center",
               gap: 6, background: "rgba(10,8,7,.75)", color: "var(--ink-2)", padding: "2px 5px",
               borderRadius: 3, zIndex: 1, pointerEvents: "none" };
// The badge's own drawing of each layer. The layers themselves and their words live next door, in
// the module the delete confirms count with -- the tile and the window say the same thing.
const GLYPH = { video: PlayGlyph, audio: SoundGlyph };
const DRAGGED = { transform: "rotate(-3deg) scale(1.04) translate(14px, -10px)",
                  filter: "drop-shadow(0 12px 24px rgba(0,0,0,.55))", zIndex: 5,
                  position: "relative" };
const SLOT = { aspectRatio: "1/1", border: "2px dashed var(--accent)", borderRadius: 4,
               background: "var(--bg-3)", boxSizing: "border-box" };
// The ✓ ring sits where the order badge is, and the badge steps aside for it (see app.css): while
// frames are being picked, what is looked at is the pictures, not the numbering. Its visibility is
// CSS's job -- it appears on hover while browsing, and stays on for every tile once the mode is
// open.
const CHECK = { position: "absolute", top: 6, right: 6, width: 18, height: 18, borderRadius: "50%",
                boxSizing: "border-box", display: "flex", alignItems: "center",
                justifyContent: "center", cursor: "pointer", zIndex: 2 };
const CHECK_ON = { background: "var(--accent)", color: "#1a1625", fontSize: 11, fontWeight: 700 };
const CHECK_OFF = { border: "2px solid var(--ink-3)", background: "rgba(0,0,0,.35)" };
const TINT = { position: "absolute", inset: 0, background: "rgba(167,139,250,.18)",
               borderRadius: 4 };
// Sticky, not absolute: the gallery scrolls, and a bar anchored to the content only shows up once
// the user has scrolled all the way down -- which is exactly when they no longer need it.
// 28, not 20: with the card's shadow under it, a smaller gap reads as stuck to the floor rather
// than floating over the gallery (madde 108).
const BAR_RAIL = { position: "sticky", bottom: 28, display: "flex", justifyContent: "center",
                   pointerEvents: "none", zIndex: 10, marginTop: -64 };
const BAR = { display: "flex", alignItems: "center", gap: 14, padding: "10px 18px",
              borderColor: "var(--accent)", pointerEvents: "auto" };

// A layer that blew up on a frame that still has its picture: the way back rides an overlay CSS
// only brings down under the pointer, so the photo is never hidden for good (madde 67).
const VEIL = { position: "absolute", inset: 0, display: "flex", alignItems: "center",
               justifyContent: "center", background: "rgba(0,0,0,.55)",
               borderRadius: "var(--r-sm)", zIndex: 3 };

/** The way back from a failed render.
 *
 * Pressed once: the queue has taken it and the card only changes on the next poll, so the button
 * says so itself rather than sitting there ready for a second press (madde 69).
 */
function RetryButton({ frame, sent, onRetry }) {
  return (
    <Btn sm disabled={sent}
         onClick={(e) => { e.preventDefault(); e.stopPropagation(); if (!sent) onRetry(frame); }}
         style={{ color: "var(--danger)", borderColor: "var(--danger)", background: "transparent" }}>
      {sent ? "Kuyruğa eklendi" : <><Icon.Regen /> Tekrar dene</>}
    </Btn>
  );
}

/** The one thing worth saying about a frame's state, or nothing at all.
 *
 * Running first, then what blew up, then what is still owed: a frame can be several of these at
 * once -- its photo failed while its video waits -- and two pills in one corner make the card
 * unreadable. The rest is the detail page's to show.
 *
 * `flowing` is the queue's own state, not this frame's: an owed layer reads as queued while the
 * worker is moving through the list and as waiting once it has stopped. The debt is the same
 * either way; only the promise differs.
 */
function statusOf(frame, rendering, flowing) {
  if (rendering) return { layer: rendering, state: "running" };
  const failed = (frame.failed || [])[0];
  if (failed) return { layer: failed, state: "failed" };
  const owed = (frame.owed || [])[0];
  if (owed) return { layer: owed, state: flowing ? "pending" : "waiting" };
  return null;
}

function Tile({ name, muted, danger, badge, pill, owns, veil, selected, onCheck, children }) {
  const nameColor = danger ? "var(--danger)" : muted ? "var(--ink-4)" : "var(--ink-3)";
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <div style={{ position: "relative",
                    ...(selected ? { outline: "2px solid var(--accent)", borderRadius: 4 } : {}) }}>
        {children}
        {veil}
        {/* A frame that is not a photo yet carries the same badge from the same sequence, only in
            a fainter tone -- 20 pending becomes 20 produced. */}
        {/* wf-mono is repeated on purpose: the kit's Mono writes its own className before
            spreading the rest, so a className passed in replaces it rather than joining it -- and
            vendor/ is not ours to edit. The dim tone for a frame with no photo yet is a class
            rather than an inline style, because an inline opacity would beat the rule in app.css
            that takes the number away when the ring arrives. */}
        {badge != null && (
          <Mono size={10} style={BADGE}
                className={muted ? "wf-mono qe-badge qe-badge--muted" : "wf-mono qe-badge"}>
            {badge}
          </Mono>
        )}
        {pill}
        {owns.length > 0 && (
          <span style={OWNS}>
            {owns.map(({ layer, word }) => {
              const Glyph = GLYPH[layer];
              return (
                <span key={layer} style={{ display: "flex", alignItems: "center", gap: 3 }}>
                  <Glyph size={9} />
                  <Mono size={9}>{word}</Mono>
                </span>
              );
            })}
          </span>
        )}
        {selected && <div style={TINT} />}
        {onCheck && (
          <div data-check className={selected ? "qe-check qe-check--on" : "qe-check"}
               style={{ ...CHECK, ...(selected ? CHECK_ON : CHECK_OFF) }}
               onClick={(e) => { e.preventDefault(); e.stopPropagation(); onCheck(); }}>
            {selected ? "✓" : ""}
          </div>
        )}
      </div>
      <Mono size={10} style={{ color: nameColor }}>{name}</Mono>
    </div>
  );
}

// Artboard 03/04/05: five columns, one sequence. Every frame stands in its own place whatever
// became of it -- waiting, rendering, failed or produced -- and a frame turns into a photo without
// moving. Its state changes how it looks, never where it is.
export default function Gallery({ project, frames, current, currentLayer, running, onReorder,
                                  onDelete, onRetry, onSelectionChange }) {
  // Drag state belongs to the grid, not to a tile: only the grid knows what "before this one"
  // means. Indexes, not file names, because the drop slot is a position.
  const [dragIndex, setDragIndex] = useState(null);
  const [overIndex, setOverIndex] = useState(null);
  // Selection is by identity, not index: a batch can land while the mode is open and shift every
  // position, but an identity still means the same frame -- and two frames can be showing one
  // picture, so a file name would not tell them apart.
  const [selected, setSelected] = useState([]);
  // The mode IS the selection: rings on the cards while there is one, none while there is not.
  // Derived rather than a flag of its own, because the two drifting apart is exactly what left a
  // gallery covered in rings after its bar had already gone.
  const selecting = selected.length > 0;
  const [confirming, setConfirming] = useState(false);
  const [deleting, setDeleting] = useState(false);
  // Which frames have just been sent back. The screen's own memory: the server keeps no "asked for"
  // flag, and the next poll brings the frame back as a waiting one anyway.
  const [retried, setRetried] = useState([]);

  // The gallery owns the selection; the video panel only needs to read it, so it hears about it
  // rather than keeping a second copy that could drift.
  useEffect(() => {
    if (onSelectionChange) onSelectionChange(selected);
  }, [selected, onSelectionChange]);

  useEffect(() => {
    if (!selecting) return undefined;
    const onKey = (e) => { if (e.key === "Escape" && !confirming) closeSelection(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  function closeSelection() {
    setSelected([]);
  }

  function sendBack(fid) {
    setRetried((frames) => [...frames, fid]);
    onRetry(fid);
  }

  function toggle(fid) {
    setSelected((current) => (current.includes(fid)
      ? current.filter((chosen) => chosen !== fid)
      : [...current, fid]));
  }

  function handleDelete() {
    setDeleting(true);
    onDelete(selected).then(() => {
      setDeleting(false);
      setConfirming(false);
      closeSelection();
    });
  }

  if (frames === null) {
    // First fetch still flying: "empty" is not known yet, so spin instead of a false
    // "henüz kare yok" (spec §2.3).
    return (
      <div style={{ ...PAD, ...EMPTY }}>
        <span className="wf-spinner" />
      </div>
    );
  }
  if (!frames.length) {
    return (
      <div style={{ ...PAD, ...EMPTY }}>
        <Mono size={12} style={{ color: "var(--ink-3)" }}>henüz kare yok</Mono>
        <Note size={13} style={{ color: "var(--ink-3)" }}>
          Prompt'ları yaz, Kuyruğa ekle'ye bas — kareler burada belirecek
        </Note>
      </div>
    );
  }

  // Everything but the frame the worker is holding can be selected: a disabled ring would raise
  // "why can I not select this?", and a ring that is simply not there raises nothing.
  const selectable = frames.filter((frame) => frame.id !== current);
  const byId = new Map(frames.map((frame) => [frame.id, frame]));
  const chosenPhotos = selected.filter((fid) => byId.get(fid)?.status === "done");
  const chosenQueued = selected.filter((fid) => byId.get(fid)?.status !== "done");
  // Three windows, because a pending frame is not a produced one: telling someone that 5 frames
  // will be deleted when 3 of them do not exist yet would be a lie, and "cannot be undone" is only
  // true of the ones that do. The mixed one is the title alone -- with both halves named there, a
  // line under it could only repeat itself (karar 64).
  // Each carries its own width beside its own words (madde 105): the longer the sentence, the wider
  // the window it opens in.
  const confirm = chosenPhotos.length && chosenQueued.length
    ? { title: `${chosenPhotos.length} kare silinsin, `
               + `${chosenQueued.length} bekleyen kare kuyruktan çıkarılsın mı?`,
        label: "Sil", width: 420 }
    : chosenQueued.length
      ? { title: `${chosenQueued.length} kare kuyruktan çıkarılsın mı?`,
          body: "Bu kareler üretilmeyecek. Üretilmiş karelere ve dosyalarına dokunulmaz.",
          label: "Çıkar", width: 400 }
      : { title: `${chosenPhotos.length} kare silinsin mi?`,
          // What goes with the frames is named before the warning: a frame is its layers too.
          body: lostLayers(chosenPhotos.map((fid) => byId.get(fid)))
                + "Bu işlem geri alınamaz.",
          label: "Sil", width: 320 };

  function handleDrop() {
    const from = dragIndex;
    const to = overIndex;
    setDragIndex(null);
    setOverIndex(null);
    if (from === null || to === null || from === to) return;
    // The whole sequence is sent, pending frames included: the order covers them too now.
    const next = frames.map((frame) => frame.id);
    const [moved] = next.splice(from, 1);
    next.splice(to, 0, moved);
    onReorder(next);
  }

  return (
    // The floating bar is positioned against this box, and the extra bottom room is what lets the
    // last row scroll clear of it (the design asks for exactly that).
    <div style={{ ...PAD, position: "relative", paddingBottom: selecting ? 92 : PAD.padding }}>
      <div style={GRID}>
        {frames.map((frame, index) => {
          // The frame being rendered is one the live worker happens to be holding: it has no state
          // on disk, so the list cannot say so and the running job does. Only a PHOTO render
          // empties the card -- a frame whose video is being made still has its picture, and
          // taking it away would say the photo went somewhere.
          // Which layer of this frame the worker is holding, if any -- not to be confused with
          // `running`, the prop above, which says whether the queue is moving at all.
          const rendering = frame.id === current ? (currentLayer || "photo") : null;
          const state = rendering === "photo" ? "running" : frame.status;
          const produced = state === "done";
          const owns = owned(frame);
          // A layer failed on a frame that still has its picture: the card stays as it is and the
          // way back comes down over it under the pointer.
          const brokenLayer = produced && (frame.failed || []).length > 0;
          // The badge counts up from the bottom: the oldest frame is 1, the newest is N, and a new
          // frame on top never renumbers the ones below it.
          const badge = frames.length - index;
          const dragging = index === dragIndex;
          const isSlot = index === overIndex && dragIndex !== null && !dragging;
          return (
            <div
              key={frame.id}
              data-tile
              // The id is the only handle anything outside the gallery has on a single frame: the
              // queue panel's "galeride göster" link scrolls to it without knowing this grid.
              id={`tile-${frame.id}`}
              className={selecting ? "qe-tile qe-tile--selecting" : "qe-tile"}
              // Draggable from the start, not after a hold: the browser decides at mousedown
              // whether a press may become a drag, so a tile armed 250 ms later was never a drag
              // source at all -- the gallery simply could not be reordered. Every card can be
              // picked up whatever became of it, because the sequence a drag makes is the sequence
              // the queue produces in. While selecting, a press is a selection instead -- one
              // gesture cannot mean two things.
              draggable={!selecting}
              onDragStart={() => setDragIndex(index)}
              onDragOver={(e) => { e.preventDefault(); setOverIndex(index); }}
              onDrop={handleDrop}
              onDragEnd={() => { setDragIndex(null); setOverIndex(null); }}
              onClick={selecting && state !== "running" ? () => toggle(frame.id) : undefined}
              style={dragging ? DRAGGED : undefined}
            >
              {isSlot ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <div style={SLOT} />
                  {/* Keeps the row's height while the caption is hidden, so the grid does not jump. */}
                  <Mono size={10} style={{ visibility: "hidden" }}>{frame.file}</Mono>
                </div>
              ) : (
                <Tile name={frame.file} badge={badge} muted={!produced}
                      danger={state === "failed"}
                      pill={<StatusPill {...(statusOf(frame, rendering, running) || {})} />}
                      owns={owns}
                      veil={brokenLayer && (
                        <div data-veil className="qe-veil" style={VEIL}>
                          <RetryButton frame={frame.id} sent={retried.includes(frame.id)}
                                       onRetry={sendBack} />
                        </div>
                      )}
                      onCheck={state === "running" ? undefined : () => toggle(frame.id)}
                      selected={selected.includes(frame.id)}>
                  {/* Every frame opens its own page, produced or not -- the detail page knows all
                      four states, and a waiting frame's prompt is only readable there. A real link
                      so middle-click still opens a tab, but a plain click stays in the app instead
                      of reloading the whole page. A drag never ends in a click, so the two gestures
                      do not collide. The link is not draggable itself -- otherwise the browser
                      drags the URL instead of the tile. */}
                  <a href={photoPath(project, frame.id)} draggable={false}
                     style={{ display: "block" }}
                     onClick={(e) => {
                       e.preventDefault();
                       if (!selecting) navigate(photoPath(project, frame.id));
                     }}>
                    {state === "done" ? (
                      /* The picture asks a queue before it downloads: every tile is a request
                         through the same tunnel, and unlimited tiles starved the poll until it
                         timed out. loading=lazy is gone with it -- the queue is the gate now, and
                         the tile only asks once it is near. */
                      <TileImage project={project} file={frame.file}
                                 decoding="async" draggable={false}
                                 style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover",
                                          border: "1px solid var(--border)",
                                          borderRadius: "var(--r-sm)", display: "block" }} />
                    ) : state === "running" ? (
                      <Rendering style={{ aspectRatio: "1/1" }} />
                    ) : state === "failed" ? (
                      /* A frame that blew up stays where it is with its own way back: the run went
                         on without it, and Tekrar dene produces just this one. */
                      <div className="wf-img"
                           style={{ aspectRatio: "1/1", borderColor: "var(--danger)",
                                    background: "var(--danger-bg)", backgroundImage: "none",
                                    display: "flex", flexDirection: "column", gap: 6 }}>
                        <span style={{ color: "var(--danger)" }}><Icon.Warn /></span>
                        {/* Inside the link, so it has to keep the click to itself: pressing
                            Tekrar dene means retry, never "open this frame". */}
                        <RetryButton frame={frame.id} sent={retried.includes(frame.id)}
                                     onRetry={sendBack} />
                      </div>
                    ) : (
                      /* Nothing in the middle: the dashed border already says there are no pixels,
                         and the corner's pill says what the frame is waiting for. */
                      <div className="wf-img" style={{ aspectRatio: "1/1", borderStyle: "dashed",
                                                       opacity: 0.35 }} />
                    )}
                  </a>
                </Tile>
              )}
            </div>
          );
        })}
      </div>

      {/* The bar belongs to a selection, not to a mode alongside it: there is only the selection
          now, so having one is the whole condition. */}
      {selecting && (
        <div style={BAR_RAIL}>
          <div className="wf-card wf-card--shadow" style={BAR}>
            {/* One number, never split by kind: what is selected is frames. */}
            <Mono size={12} style={{ color: "var(--accent)" }}>{selected.length} seçili</Mono>
            <Btn sm ghost
                 onClick={() => setSelected(selected.length === selectable.length
                   ? []
                   : selectable.map((frame) => frame.id))}>
              Tümünü seç
            </Btn>
            <Btn sm onClick={() => setConfirming(true)}
                 style={{ color: "var(--danger)", borderColor: "var(--danger)",
                          background: "none" }}>
              {/* One word in all three cases (madde 65): what really happens is the opening
                  window's to say, and it says it differently every time. */}
              <Icon.Trash /> Sil
            </Btn>
            <Btn sm ghost onClick={closeSelection}>Vazgeç</Btn>
          </div>
        </div>
      )}

      {confirming && (
        <ConfirmModal title={confirm.title} body={confirm.body} confirmLabel={confirm.label}
                      width={confirm.width}
                      busyLabel="Siliniyor…" danger busy={deleting}
                      onCancel={() => setConfirming(false)} onConfirm={handleDelete} />
      )}
    </div>
  );
}
