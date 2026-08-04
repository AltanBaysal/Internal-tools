import { Btn, Mono, Note } from "../../vendor/kit.jsx";

const BOX = { padding: "8px 10px", display: "flex", flexDirection: "column", gap: 8 };
const TRACK = { height: 5, background: "var(--bg-3)", borderRadius: 3, overflow: "hidden" };

// Artboard 04: a full-width muted Durdur ABOVE the progress card -- same size as Üret, never
// accent-coloured. The card below only shows progress.
export default function ProgressPanel({ job, stopping, onStop }) {
  const { done = 0, failed = 0, total = 0, current } = job;
  const finished = done + failed;
  // total is 0 on the first poll after the 202: the server has not planned the frames yet.
  const percent = total ? Math.round((finished / total) * 100) : 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <Btn onClick={onStop} disabled={stopping}
           style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14,
                    color: "var(--ink-2)" }}>
        {stopping ? "Durduruluyor…" : "Durdur"}
      </Btn>

      <div className="wf-stroke" style={BOX}>
        <Mono size={13} style={{ color: "var(--accent)" }}>{finished} / {total || "…"}</Mono>
        <div style={TRACK}>
          <div style={{ width: `${percent}%`, height: "100%", background: "var(--accent)" }} />
        </div>
        {current && (
          <Note size={12} style={{ color: "var(--ink-2)", whiteSpace: "nowrap",
                                   overflow: "hidden", textOverflow: "ellipsis" }}>
            şimdi: "{current.prompt}"
          </Note>
        )}
        {failed > 0 && (
          <Note size={12} style={{ color: "var(--danger)" }}>
            {failed} fotoğraf üretilemedi — diğerleri devam ediyor
          </Note>
        )}
      </div>
    </div>
  );
}
