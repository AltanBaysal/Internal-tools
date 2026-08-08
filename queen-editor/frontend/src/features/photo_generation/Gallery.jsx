import { useEffect, useRef, useState } from "react";

import { photoUrl } from "../../shared/api.js";
import ConfirmModal from "../../shared/ConfirmModal.jsx";
import { navigate, photoPath } from "../../shared/router.js";
import { Btn, Icon, ImgPH, Mono, Note } from "../../vendor/kit.jsx";

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
const DRAGGED = { transform: "rotate(-3deg) scale(1.04) translate(14px, -10px)",
                  filter: "drop-shadow(0 12px 24px rgba(0,0,0,.55))", zIndex: 5,
                  position: "relative" };
const SLOT = { aspectRatio: "1/1", border: "2px dashed var(--accent)", borderRadius: 4,
               background: "var(--bg-3)", boxSizing: "border-box" };
// The ✓ ring sits opposite the order badge. Its visibility is CSS's job (see app.css): it appears
// on hover while browsing, and stays on for every tile once the mode is open.
const CHECK = { position: "absolute", top: 6, left: 6, width: 18, height: 18, borderRadius: "50%",
                boxSizing: "border-box", display: "flex", alignItems: "center",
                justifyContent: "center", cursor: "pointer", zIndex: 2 };
const CHECK_ON = { background: "var(--accent)", color: "#1a1625", fontSize: 11, fontWeight: 700 };
const CHECK_OFF = { border: "2px solid var(--ink-3)", background: "rgba(0,0,0,.35)" };
const TINT = { position: "absolute", inset: 0, background: "rgba(167,139,250,.18)",
               borderRadius: 4 };
// Sticky, not absolute: the gallery scrolls, and a bar anchored to the content only shows up once
// the user has scrolled all the way down -- which is exactly when they no longer need it.
const BAR_RAIL = { position: "sticky", bottom: 20, display: "flex", justifyContent: "center",
                   pointerEvents: "none", zIndex: 10, marginTop: -64 };
const BAR = { display: "flex", alignItems: "center", gap: 14, padding: "10px 18px",
              borderColor: "var(--accent)", pointerEvents: "auto" };
// Long enough that a press-and-slide does not become a drag, short enough that a deliberate hold
// does not feel stuck. The design asks for a hold; the number is ours.
const HOLD_MS = 250;
const HINT = { position: "absolute", inset: 0, display: "flex", alignItems: "center",
               justifyContent: "center", background: "rgba(10,8,7,.8)", borderRadius: 4,
               zIndex: 3, textAlign: "center", padding: 6 };

function Tile({ name, muted, danger, badge, selected, onCheck, hint, children }) {
  const nameColor = danger ? "var(--danger)" : muted ? "var(--ink-4)" : "var(--ink-3)";
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <div style={{ position: "relative",
                    ...(selected ? { outline: "2px solid var(--accent)", borderRadius: 4 } : {}) }}>
        {children}
        {/* A frame that is not a photo yet carries the same badge from the same sequence, only in
            a fainter tone -- 20 pending becomes 20 produced. */}
        {badge != null && (
          <Mono size={10} style={muted ? { ...BADGE, opacity: 0.5 } : BADGE}>{badge}</Mono>
        )}
        {selected && <div style={TINT} />}
        {onCheck && (
          <div data-check className={selected ? "qe-check qe-check--on" : "qe-check"}
               style={{ ...CHECK, ...(selected ? CHECK_ON : CHECK_OFF) }}
               onClick={(e) => { e.preventDefault(); e.stopPropagation(); onCheck(); }}>
            {selected ? "✓" : ""}
          </div>
        )}
        {/* Held down but not liftable: the card does not rise, it explains why instead. */}
        {hint && (
          <div style={HINT}>
            <Mono size={10} style={{ color: "var(--ink-2)" }}>{hint}</Mono>
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
export default function Gallery({ project, frames, current, onReorder, onDelete, onRetry }) {
  // Drag state belongs to the grid, not to a tile: only the grid knows what "before this one"
  // means. Indexes, not file names, because the drop slot is a position.
  const [dragIndex, setDragIndex] = useState(null);
  const [overIndex, setOverIndex] = useState(null);
  // Selection is by file name, not index: a batch can land while the mode is open and shift every
  // position, but a name still means the same photo.
  const [selecting, setSelecting] = useState(false);
  const [selected, setSelected] = useState([]);
  const [confirming, setConfirming] = useState(false);
  const [deleting, setDeleting] = useState(false);
  // A tile can only be picked up after it has been held: which one is armed, and which one is
  // showing the "not yet" tip instead.
  const [armed, setArmed] = useState(null);
  const [hint, setHint] = useState(null);
  const hold = useRef(null);

  useEffect(() => () => clearTimeout(hold.current), []);

  function press(file, produced) {
    clearTimeout(hold.current);
    hold.current = setTimeout(() => (produced ? setArmed(file) : setHint(file)), HOLD_MS);
  }

  function release() {
    clearTimeout(hold.current);
    setArmed(null);
    setHint(null);
  }

  useEffect(() => {
    if (!selecting) return undefined;
    const onKey = (e) => { if (e.key === "Escape" && !confirming) closeSelection(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  function closeSelection() {
    setSelecting(false);
    setSelected([]);
  }

  function toggle(file) {
    setSelecting(true);
    setSelected((current) => (current.includes(file)
      ? current.filter((name) => name !== file)
      : [...current, file]));
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
    // "henüz fotoğraf yok" (spec §2.3).
    return (
      <div style={{ ...PAD, ...EMPTY }}>
        <span className="wf-spinner" />
      </div>
    );
  }
  if (!frames.length) {
    return (
      <div style={{ ...PAD, ...EMPTY }}>
        <Mono size={12} style={{ color: "var(--ink-3)" }}>henüz fotoğraf yok</Mono>
        <Note size={13} style={{ color: "var(--ink-3)" }}>
          Prompt'ları yaz, Üretime ekle'ye bas — fotoğraflar burada belirecek
        </Note>
      </div>
    );
  }

  // Everything but the frame the worker is holding can be selected: a disabled ring would raise
  // "why can I not select this?", and a ring that is simply not there raises nothing.
  const selectable = frames.filter((frame) => frame.file !== current);
  const byFile = new Map(frames.map((frame) => [frame.file, frame]));
  const chosenPhotos = selected.filter((file) => byFile.get(file)?.status === "done");
  const chosenQueued = selected.filter((file) => byFile.get(file)?.status !== "done");
  // Three sentences, because a pending frame is not a photo: telling someone that 5 photos will be
  // deleted when 3 of them do not exist yet would be a lie, and "cannot be undone" is only true of
  // the ones that do.
  const confirm = chosenPhotos.length && chosenQueued.length
    ? { title: `${chosenPhotos.length} fotoğraf silinsin, `
               + `${chosenQueued.length} bekleyen kare kuyruktan çıkarılsın mı?`,
        body: "Fotoğraflar kalıcı olarak silinir — bu geri alınamaz. "
              + "Bekleyen kareler üretilmeden kuyruktan çıkar.",
        label: "Sil" }
    : chosenQueued.length
      ? { title: `${chosenQueued.length} kare kuyruktan çıkarılsın mı?`,
          body: "Bu kareler üretilmeyecek. Galerideki fotoğraflara dokunulmaz.",
          label: "Çıkar" }
      : { title: `${chosenPhotos.length} fotoğraf silinsin mi?`,
          body: "Bu işlem geri alınamaz.",
          label: "Sil" };

  function handleDrop() {
    const from = dragIndex;
    const to = overIndex;
    setDragIndex(null);
    setOverIndex(null);
    if (from === null || to === null || from === to) return;
    // The whole sequence is sent, pending frames included: the order covers them too now.
    const next = frames.map((frame) => frame.file);
    const [moved] = next.splice(from, 1);
    next.splice(to, 0, moved);
    onReorder(next);
  }

  return (
    // The floating bar is positioned against this box, and the extra bottom room is what lets the
    // last row scroll clear of it (the design asks for exactly that).
    <div style={{ ...PAD, position: "relative", paddingBottom: selecting ? 84 : PAD.padding }}>
      <div style={GRID}>
        {frames.map((frame, index) => {
          // The frame being rendered is a pending one the live worker happens to be holding: it
          // has no state on disk, so the list cannot say so and the running file name does.
          const state = frame.file === current ? "running" : frame.status;
          const produced = state === "done";
          // The badge counts up from the bottom: the oldest frame is 1, the newest is N, and a new
          // frame on top never renumbers the ones below it.
          const badge = frames.length - index;
          const dragging = index === dragIndex;
          const isSlot = index === overIndex && dragIndex !== null && !dragging;
          return (
            <div
              key={frame.file}
              data-tile
              // The id is the only handle anything outside the gallery has on a single frame: the
              // queue panel's "galeride göster" link scrolls to it without knowing this grid.
              id={`tile-${frame.file}`}
              className={selecting ? "qe-tile qe-tile--selecting" : "qe-tile"}
              // Only a produced frame can be picked up: sorting is a visual decision, and there is
              // nothing to look at yet on the others. While selecting, a press is a selection, not
              // a drag -- one gesture cannot mean two things.
              draggable={armed === frame.file && !selecting}
              onMouseDown={() => !selecting && press(frame.file, produced)}
              onMouseUp={release}
              onMouseLeave={release}
              onDragStart={() => setDragIndex(index)}
              onDragOver={(e) => { e.preventDefault(); setOverIndex(index); }}
              onDrop={handleDrop}
              onDragEnd={() => { setDragIndex(null); setOverIndex(null); release(); }}
              onClick={selecting && state !== "running" ? () => toggle(frame.file) : undefined}
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
                      onCheck={state === "running" ? undefined : () => toggle(frame.file)}
                      selected={selected.includes(frame.file)}
                      hint={hint === frame.file ? "üretilince sıralanabilir" : null}>
                  {/* Every frame opens its own page, produced or not -- the detail page knows all
                      four states, and a waiting frame's prompt is only readable there. A real link
                      so middle-click still opens a tab, but a plain click stays in the app instead
                      of reloading the whole page. A drag never ends in a click, so the two gestures
                      do not collide. The link is not draggable itself -- otherwise the browser
                      drags the URL instead of the tile. */}
                  <a href={photoPath(project, frame.file)} draggable={false}
                     style={{ display: "block" }}
                     onClick={(e) => {
                       e.preventDefault();
                       if (!selecting) navigate(photoPath(project, frame.file));
                     }}>
                    {state === "done" ? (
                      <img src={photoUrl(project, frame.file)} alt={frame.file}
                           loading="lazy" decoding="async" draggable={false}
                           style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover",
                                    border: "1px solid var(--border)", borderRadius: "var(--r-sm)",
                                    display: "block" }} />
                    ) : state === "running" ? (
                      <ImgPH loading style={{ aspectRatio: "1/1" }} />
                    ) : state === "failed" ? (
                      /* A frame that blew up stays where it is with its own way back: the run went
                         on without it, and Tekrar dene produces just this one. */
                      <div className="wf-img"
                           style={{ aspectRatio: "1/1", borderColor: "var(--danger)",
                                    background: "var(--danger-bg)", backgroundImage: "none",
                                    display: "flex", flexDirection: "column", gap: 6 }}>
                        <span style={{ color: "var(--danger)" }}><Icon.Warn /></span>
                        {/* Inside the link now, so it has to keep the click to itself: pressing
                            Tekrar dene means retry, never "open this frame". */}
                        <Btn sm onClick={(e) => { e.preventDefault(); e.stopPropagation();
                                                  onRetry(frame.file); }}
                             style={{ color: "var(--danger)", borderColor: "var(--danger)",
                                      background: "transparent" }}>
                          <Icon.Regen /> Tekrar dene
                        </Btn>
                      </div>
                    ) : (
                      <div className="wf-img" style={{ aspectRatio: "1/1", borderStyle: "dashed",
                                                       opacity: 0.35 }}>
                        <Mono size={10} style={{ color: "var(--ink-3)" }}>bekliyor</Mono>
                      </div>
                    )}
                  </a>
                </Tile>
              )}
            </div>
          );
        })}
      </div>

      {/* The bar belongs to a selection, not to the mode: with nothing selected it has nothing to
          say, so it goes away rather than sitting there reading "0 seçili". */}
      {selecting && selected.length > 0 && (
        <div style={BAR_RAIL}>
          <div className="wf-card wf-card--shadow" style={BAR}>
            {/* One number, never split by kind: what is selected is frames. */}
            <Mono size={12} style={{ color: "var(--accent)" }}>{selected.length} seçili</Mono>
            <Btn sm ghost
                 onClick={() => setSelected(selected.length === selectable.length
                   ? []
                   : selectable.map((frame) => frame.file))}>
              Tümünü seç
            </Btn>
            <Btn sm onClick={() => setConfirming(true)}
                 style={{ color: "var(--danger)", borderColor: "var(--danger)",
                          background: "none" }}>
              <Icon.Trash /> {chosenPhotos.length ? "Sil" : "Çıkar"}
            </Btn>
            <Btn sm ghost onClick={closeSelection}>Vazgeç</Btn>
          </div>
        </div>
      )}

      {confirming && (
        <ConfirmModal title={confirm.title} body={confirm.body} confirmLabel={confirm.label}
                      busyLabel="Siliniyor…" danger busy={deleting}
                      onCancel={() => setConfirming(false)} onConfirm={handleDelete} />
      )}
    </div>
  );
}
