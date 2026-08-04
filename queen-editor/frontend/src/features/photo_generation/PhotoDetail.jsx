import { useEffect, useState } from "react";

import { photoUrl } from "../../shared/api.js";
import { navigate, photoPath, projectPath } from "../../shared/router.js";
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Btn, Hand, Icon, Mono, Note } from "../../vendor/kit.jsx";
import PhotoDeleteModal from "./PhotoDeleteModal.jsx";
import { usePhotos } from "./usePhotos.js";

const HEADER = {
  display: "grid", gridTemplateColumns: "1fr auto 1fr", alignItems: "center",
  padding: "14px 32px", background: "var(--bg-2)", borderBottom: "1px solid var(--border)",
};
const STAGE = {
  flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: 24,
  position: "relative", background: "var(--bg)", minHeight: 0,
};
// The design's arrows: plain glyphs at the two ends of the photo area, glowing enough to stay
// legible over any photo.
const ARROW = {
  position: "absolute", top: "50%", transform: "translateY(-50%)", color: "#fff", fontSize: 44,
  lineHeight: 1, fontWeight: 300, textShadow: "0 0 4px rgba(0,0,0,.9), 0 2px 8px rgba(0,0,0,.7)",
  userSelect: "none",
};
const SIDE = {
  width: 300, flexShrink: 0, borderLeft: "1px solid var(--border)", padding: 16,
  display: "flex", flexDirection: "column", gap: 14, boxSizing: "border-box", minHeight: 0,
};
const LABEL = { color: "var(--ink-3)", letterSpacing: ".08em", textTransform: "uppercase" };

function Arrow({ glyph, side, onClick }) {
  // No handler means there is nowhere to go: the design says the ends do not wrap around, so the
  // arrow is dimmed rather than hidden -- the two ends stay where the eye expects them.
  const enabled = Boolean(onClick);
  return (
    <div role="button" onClick={onClick}
         style={{ ...ARROW, [side]: 20, cursor: enabled ? "pointer" : "default",
                  opacity: enabled ? 1 : 0.25 }}>
      {glyph}
    </div>
  );
}

// Artboard 10: the photo as large as it fits at its own aspect ratio, between two arrows; the
// 300px column on the right says where it sits, what it is called and what made it.
export default function PhotoDetail({ project, file }) {
  const { photos, error, remove } = usePhotos(project);
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);

  const index = photos ? photos.findIndex((photo) => photo.file === file) : -1;
  const current = index >= 0 ? photos[index] : null;
  const previous = index > 0 ? photos[index - 1] : null;
  const next = photos && index >= 0 && index < photos.length - 1 ? photos[index + 1] : null;

  useEffect(() => {
    const onKey = (e) => {
      if (confirming) return;                    // the modal owns the keyboard while it is open
      if (e.key === "Escape") navigate(projectPath(project));
      if (e.key === "ArrowLeft" && previous) navigate(photoPath(project, previous.file));
      if (e.key === "ArrowRight" && next) navigate(photoPath(project, next.file));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [project, previous, next, confirming]);

  function handleDelete() {
    setBusy(true);
    // Where to go afterwards is decided before the list changes: the next photo, the one before it
    // when this was the last, or the gallery when nothing is left.
    const after = next || previous;
    remove(file).then(() => {
      setBusy(false);
      setConfirming(false);
      navigate(after ? photoPath(project, after.file) : projectPath(project));
    });
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={HEADER}>
        <Hand size={20}><span className="wf-hl">Queen Editor</span></Hand>
        <Hand size={20}>{project}</Hand>
        <Btn ghost style={{ justifySelf: "end" }} onClick={() => navigate(projectPath(project))}>
          <Icon.Left /> Galeriye dön
        </Btn>
      </div>

      {photos === null ? (
        <div style={STAGE}><span className="wf-spinner" /></div>
      ) : !current ? (
        <div style={{ ...STAGE, flexDirection: "column", gap: 12 }}>
          <StatusErrorCard text="Fotoğraf bulunamadı" raw={error || file} />
        </div>
      ) : (
        <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
          <div style={STAGE}>
            <Arrow glyph="‹" side="left"
                   onClick={previous
                     ? () => navigate(photoPath(project, previous.file))
                     : undefined} />
            <Arrow glyph="›" side="right"
                   onClick={next ? () => navigate(photoPath(project, next.file)) : undefined} />
            {/* contain, not a fixed ratio: the server does not know the photo's shape, and the
                design's rule is that it is never cropped. 120px is the design's own arrow gutter. */}
            <img src={photoUrl(project, current.file)} alt={current.file}
                 style={{ maxWidth: "calc(100% - 120px)", maxHeight: "100%", width: "auto",
                          height: "auto", objectFit: "contain", display: "block" }} />
          </div>

          <div style={SIDE}>
            <div style={{ display: "flex", gap: 24 }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                <Mono size={10} style={LABEL}>Sıra</Mono>
                <Mono size={13} style={{ color: "var(--ink)" }}>{index + 1} / {photos.length}</Mono>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                <Mono size={10} style={LABEL}>Dosya adı</Mono>
                <Mono size={13} style={{ color: "var(--ink)" }}>{current.file}</Mono>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1, minHeight: 0 }}>
              <Mono size={10} style={LABEL}>Prompt</Mono>
              <div className="wf-stroke"
                   style={{ flex: 1, minHeight: 0, overflowY: "auto", padding: 10 }}>
                <Note size={12} style={{ color: "var(--ink-2)", display: "block",
                                         lineHeight: 1.6 }}>
                  {current.prompt}
                </Note>
              </div>
            </div>

            {error && <StatusErrorCard text="Fotoğraf silinemedi" raw={error} />}

            <Btn sm onClick={() => setConfirming(true)}
                 style={{ color: "var(--danger)", borderColor: "var(--danger)",
                          justifyContent: "center" }}>
              <Icon.Trash /> Sil
            </Btn>
          </div>
        </div>
      )}

      {confirming && (
        <PhotoDeleteModal busy={busy} onCancel={() => setConfirming(false)}
                          onConfirm={handleDelete} />
      )}
    </div>
  );
}
