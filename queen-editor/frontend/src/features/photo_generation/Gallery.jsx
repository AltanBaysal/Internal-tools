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

function Tile({ name, muted, children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      {children}
      <Mono size={10} style={{ color: muted ? "var(--ink-4)" : "var(--ink-3)" }}>{name}</Mono>
    </div>
  );
}

// Artboard 03/04: five columns, newest first (the record's own order). The frame being rendered
// sits at the front as a spinner tile, so the grid shows what is happening, not just what landed.
export default function Gallery({ project, photos, current }) {
  if (photos === null) {
    // First fetch still flying: "empty" is not known yet, so show shape instead of a false
    // "henüz fotoğraf yok" (spec §2.3).
    return (
      <div style={PAD}>
        <div style={GRID}>
          {Array.from({ length: 10 }, (_, i) => (
            <div key={i} className="wf-stroke wf-stroke--dashed" style={{ aspectRatio: "1/1" }} />
          ))}
        </div>
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

  return (
    <div style={PAD}>
      <div style={GRID}>
        {current && (
          <Tile name={`${current.number}_${current.letter}.png`} muted>
            <ImgPH loading style={{ aspectRatio: "1/1" }} />
          </Tile>
        )}
        {photos.map((photo) => (
          <Tile key={photo.file} name={photo.file}>
            {/* Placeholder until the detail page (Part 10): open the raw file in a new tab. */}
            <a href={photoUrl(project, photo.file)} target="_blank" rel="noreferrer">
              <img src={photoUrl(project, photo.file)} alt={photo.file}
                   loading="lazy" decoding="async"
                   style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover",
                            border: "1px solid var(--border)", borderRadius: "var(--r-sm)",
                            display: "block" }} />
            </a>
          </Tile>
        ))}
      </div>
    </div>
  );
}
