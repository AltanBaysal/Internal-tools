import { Btn, Mono, Note } from "../../vendor/kit.jsx";

const BOX = { padding: 12, display: "flex", flexDirection: "column", gap: 8 };
const TRACK = { height: 5, background: "var(--bg-3)", borderRadius: 3, overflow: "hidden" };

// Artboard 04: the panel's bottom block while a batch runs. The form above it stays on screen,
// so this shows progress only -- it never repeats what the fields already say.
export default function ProgressPanel({ job, onStop }) {
  const { done = 0, failed = 0, total = 0, current } = job;
  const finished = done + failed;
  // total is 0 on the first poll after the 202: the server has not planned the frames yet.
  const percent = total ? Math.round((finished / total) * 100) : 0;

  return (
    <div className="wf-stroke" style={BOX}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <Mono size={13} style={{ color: "var(--accent)" }}>{finished} / {total || "…"}</Mono>
        <Btn sm onClick={onStop}>Durdur</Btn>
      </div>

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
  );
}
