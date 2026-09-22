import { useCallback, useEffect, useState } from "react";

import { listReferences, referenceUrl, removeReference, uploadReferences } from "../../shared/api.js";
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

const PANEL = {
  width: 260,
  borderRight: "1px solid var(--border)",
  padding: 16,
  display: "flex",
  flexDirection: "column",
  gap: 14,
  overflowY: "auto",
  overflowX: "hidden",
  boxSizing: "border-box",
  flexShrink: 0,
};

const TILES = { display: "flex", flexWrap: "wrap", gap: 6 };
const TILE = { position: "relative", width: 68, display: "flex", flexDirection: "column", gap: 2 };
const FRAME = { width: 68, height: 48, objectFit: "cover", background: "var(--bg-2)",
                border: "1px solid var(--border)", display: "block" };
const BIN = { position: "absolute", top: 2, right: 2, width: 16, height: 16, lineHeight: "14px",
              padding: 0, fontSize: 11, background: "var(--bg)", border: "1px solid var(--border)",
              color: "var(--ink-2)", cursor: "pointer" };

/** How long a clip runs, in the user's own numbers. */
function ran(seconds) {
  return `${seconds.toFixed(1).replace(".", ",")} sn`;
}

function Tile({ project, row, onRemove }) {
  const url = referenceUrl(project, row.name);
  return (
    <div style={TILE}>
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
 * The project's reference pool, beside the cards (madde 299).
 *
 * It asks for its own pool rather than being handed one: nothing else on this screen has a use for
 * it, and the answer carries the limits it heads its rows with -- so the numbers are never written
 * down twice (madde 298 owns them).
 */
export default function ReferencePanel({ project, onClose }) {
  const [pool, setPool] = useState({ references: [], limits: {} });
  const [error, setError] = useState(null);
  const [asking, setAsking] = useState(null);
  const [busy, setBusy] = useState(false);

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
    <div className="wf-panel" style={PANEL}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Mono size={11} style={{ color: "var(--ink-2)", letterSpacing: "0.08em",
                                 textTransform: "uppercase" }}>
          Referanslar
        </Mono>
        <button type="button" aria-label="Referans panelini kapat" className="wf-stroke"
                onClick={onClose}
                style={{ ...BIN, position: "static", width: 18, height: 18 }}>×</button>
      </div>

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
              {rows.map((row) => (
                <Tile key={row.name} project={project} row={row} onRemove={setAsking} />
              ))}
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
