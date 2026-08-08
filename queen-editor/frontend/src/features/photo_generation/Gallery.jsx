import { useEffect, useState } from "react";

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
const BAR = { position: "absolute", left: "50%", bottom: 20, transform: "translateX(-50%)",
              display: "flex", alignItems: "center", gap: 14, padding: "10px 18px",
              borderColor: "var(--accent)", zIndex: 10 };

function Tile({ name, muted, danger, badge, selected, onCheck, children }) {
  const nameColor = danger ? "var(--danger)" : muted ? "var(--ink-4)" : "var(--ink-3)";
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <div style={{ position: "relative",
                    ...(selected ? { outline: "2px solid var(--accent)", borderRadius: 4 } : {}) }}>
        {children}
        {badge != null && <Mono size={10} style={BADGE}>{badge}</Mono>}
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

// Artboard 03/04/05: five columns, in the order the user dragged them into. The frame being
// rendered sits at the front as a spinner tile, so the grid shows what is happening, not just what
// landed -- it carries no badge because it has no place in the record yet.
export default function Gallery({ project, photos, current, pending, failures, onReorder, onDelete,
                                  onRetry }) {
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

  if (photos === null) {
    // First fetch still flying: "empty" is not known yet, so spin instead of a false
    // "henüz fotoğraf yok" (spec §2.3).
    return (
      <div style={{ ...PAD, ...EMPTY }}>
        <span className="wf-spinner" />
      </div>
    );
  }
  const queued = pending || [];
  const broken = failures || [];
  if (!photos.length && !current && !queued.length && !broken.length) {
    return (
      <div style={{ ...PAD, ...EMPTY }}>
        <Mono size={12} style={{ color: "var(--ink-3)" }}>henüz fotoğraf yok</Mono>
        <Note size={13} style={{ color: "var(--ink-3)" }}>
          Prompt'ları yaz, Üretime ekle'ye bas — fotoğraflar burada belirecek
        </Note>
      </div>
    );
  }

  function handleDrop() {
    const from = dragIndex;
    const to = overIndex;
    setDragIndex(null);
    setOverIndex(null);
    if (from === null || to === null || from === to) return;
    const next = photos.map((photo) => photo.file);
    const [moved] = next.splice(from, 1);
    next.splice(to, 0, moved);
    onReorder(next);
  }

  return (
    // The floating bar is positioned against this box, and the extra bottom room is what lets the
    // last row scroll clear of it (the design asks for exactly that).
    <div style={{ ...PAD, position: "relative", paddingBottom: selecting ? 84 : PAD.padding }}>
      <div style={GRID}>
        {current && (
          <Tile name={`${current.number}_${current.letter}.png`} muted>
            <ImgPH loading style={{ aspectRatio: "1/1" }} />
          </Tile>
        )}
        {/* A frame that blew up stays on screen with its own way back: the run went on without it,
            and Tekrar dene produces just this one, from the plan it was planned with. */}
        {broken.map((file) => (
          <Tile key={file} name={file} danger>
            <div className="wf-img"
                 style={{ aspectRatio: "1/1", borderColor: "var(--danger)",
                          background: "var(--danger-bg)", backgroundImage: "none",
                          display: "flex", flexDirection: "column", gap: 6 }}>
              <span style={{ color: "var(--danger)" }}><Icon.Warn /></span>
              <Btn sm onClick={() => onRetry(file)}
                   style={{ color: "var(--danger)", borderColor: "var(--danger)",
                            background: "transparent" }}>
                <Icon.Regen /> Tekrar dene
              </Btn>
            </div>
          </Tile>
        ))}
        {/* The queue, drawn before it exists: the run's remaining frames as faded dashed tiles, so
            the gallery shows what is coming and not only what has landed. They carry no order
            badge and cannot be dragged or selected -- there is no photo behind them yet. */}
        {queued.map((file) => (
          <Tile key={file} name={file} muted>
            <div className="wf-img" style={{ aspectRatio: "1/1", borderStyle: "dashed",
                                             opacity: 0.35 }}>
              <Mono size={10} style={{ color: "var(--ink-3)" }}>bekliyor</Mono>
            </div>
          </Tile>
        ))}
        {photos.map((photo, index) => {
          const dragging = index === dragIndex;
          const isSlot = index === overIndex && dragIndex !== null && !dragging;
          return (
            <div
              key={photo.file}
              data-tile
              className={selecting ? "qe-tile qe-tile--selecting" : "qe-tile"}
              // While selecting, a press is a selection, not a drag: one gesture cannot mean two
              // things.
              draggable={!selecting}
              onDragStart={() => setDragIndex(index)}
              onDragOver={(e) => { e.preventDefault(); setOverIndex(index); }}
              onDrop={handleDrop}
              onDragEnd={() => { setDragIndex(null); setOverIndex(null); }}
              onClick={selecting ? () => toggle(photo.file) : undefined}
              style={dragging ? DRAGGED : undefined}
            >
              {isSlot ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <div style={SLOT} />
                  {/* Keeps the row's height while the caption is hidden, so the grid does not jump. */}
                  <Mono size={10} style={{ visibility: "hidden" }}>{photo.file}</Mono>
                </div>
              ) : (
                <Tile name={photo.file} badge={index + 1} onCheck={() => toggle(photo.file)}
                      selected={selected.includes(photo.file)}>
                  {/* A real link so middle-click still opens a tab, but a plain click stays in the
                      app instead of reloading the whole page. A drag never ends in a click, so the
                      two gestures do not collide. The link and image are not draggable themselves
                      -- otherwise the browser drags the URL instead of letting the tile reorder. */}
                  <a href={photoPath(project, photo.file)} draggable={false}
                     onClick={(e) => {
                       e.preventDefault();
                       if (!selecting) navigate(photoPath(project, photo.file));
                     }}>
                    <img src={photoUrl(project, photo.file)} alt={photo.file}
                         loading="lazy" decoding="async" draggable={false}
                         style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover",
                                  border: "1px solid var(--border)", borderRadius: "var(--r-sm)",
                                  display: "block" }} />
                  </a>
                </Tile>
              )}
            </div>
          );
        })}
      </div>

      {selecting && (
        <div className="wf-card wf-card--shadow" style={BAR}>
          <Mono size={12} style={{ color: "var(--accent)" }}>{selected.length} seçili</Mono>
          <Btn sm ghost
               onClick={() => setSelected(selected.length === photos.length
                 ? []
                 : photos.map((photo) => photo.file))}>
            Tümünü seç
          </Btn>
          <Btn sm disabled={!selected.length} onClick={() => setConfirming(true)}
               style={{ color: "var(--danger)", borderColor: "var(--danger)" }}>
            <Icon.Trash /> Sil
          </Btn>
          <Btn sm ghost onClick={closeSelection}>Vazgeç</Btn>
        </div>
      )}

      {confirming && (
        <ConfirmModal title={`${selected.length} fotoğraf silinsin mi?`}
                      body="Bu işlem geri alınamaz." confirmLabel="Sil" busyLabel="Siliniyor…"
                      danger busy={deleting} onCancel={() => setConfirming(false)}
                      onConfirm={handleDelete} />
      )}
    </div>
  );
}
