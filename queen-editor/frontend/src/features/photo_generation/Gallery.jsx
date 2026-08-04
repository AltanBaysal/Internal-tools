import { useState } from "react";

import { photoUrl } from "../../shared/api.js";
import { ImgPH, Mono, Note } from "../../vendor/kit.jsx";

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

function Tile({ name, muted, badge, children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <div style={{ position: "relative" }}>
        {children}
        {badge != null && <Mono size={10} style={BADGE}>{badge}</Mono>}
      </div>
      <Mono size={10} style={{ color: muted ? "var(--ink-4)" : "var(--ink-3)" }}>{name}</Mono>
    </div>
  );
}

// Artboard 03/04/05: five columns, in the order the user dragged them into. The frame being
// rendered sits at the front as a spinner tile, so the grid shows what is happening, not just what
// landed -- it carries no badge because it has no place in the record yet.
export default function Gallery({ project, photos, current, onReorder }) {
  // Drag state belongs to the grid, not to a tile: only the grid knows what "before this one"
  // means. Indexes, not file names, because the drop slot is a position.
  const [dragIndex, setDragIndex] = useState(null);
  const [overIndex, setOverIndex] = useState(null);

  if (photos === null) {
    // First fetch still flying: "empty" is not known yet, so spin instead of a false
    // "henüz fotoğraf yok" (spec §2.3).
    return (
      <div style={{ ...PAD, ...EMPTY }}>
        <span className="wf-spinner" />
      </div>
    );
  }
  if (!photos.length && !current) {
    return (
      <div style={{ ...PAD, ...EMPTY }}>
        <Mono size={12} style={{ color: "var(--ink-3)" }}>henüz fotoğraf yok</Mono>
        <Note size={13} style={{ color: "var(--ink-3)" }}>
          Prompt'ları yaz, Üret'e bas — fotoğraflar burada belirecek
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
    <div style={PAD}>
      <div style={GRID}>
        {current && (
          <Tile name={`${current.number}_${current.letter}.png`} muted>
            <ImgPH loading style={{ aspectRatio: "1/1" }} />
          </Tile>
        )}
        {photos.map((photo, index) => {
          const dragging = index === dragIndex;
          const isSlot = index === overIndex && dragIndex !== null && !dragging;
          return (
            <div
              key={photo.file}
              draggable
              onDragStart={() => setDragIndex(index)}
              onDragOver={(e) => { e.preventDefault(); setOverIndex(index); }}
              onDrop={handleDrop}
              onDragEnd={() => { setDragIndex(null); setOverIndex(null); }}
              style={dragging ? DRAGGED : undefined}
            >
              {isSlot ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <div style={SLOT} />
                  {/* Keeps the row's height while the caption is hidden, so the grid does not jump. */}
                  <Mono size={10} style={{ visibility: "hidden" }}>{photo.file}</Mono>
                </div>
              ) : (
                <Tile name={photo.file} badge={index + 1}>
                  {/* Placeholder until the detail page (Part 11): open the raw file in a new tab.
                      The link and image are not draggable themselves -- otherwise the browser drags
                      the URL instead of letting the tile reorder. */}
                  <a href={photoUrl(project, photo.file)} target="_blank" rel="noreferrer"
                     draggable={false}>
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
    </div>
  );
}
