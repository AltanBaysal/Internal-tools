import { Btn, Mono, Note } from "../../vendor/kit.jsx";

const BAR = {
  height: 6,
  background: "var(--bg)",
  border: "1px solid var(--border)",
  borderRadius: 3,
  overflow: "hidden",
};

// Artboard 04: counter, progress bar, the frame being rendered, Stop.
export default function ProgressPanel({ job, onStop }) {
  const { done = 0, failed = 0, total = 0, current } = job;
  // total is 0 for the first poll after 202 (the server has not planned the frames yet).
  const percent = total ? Math.round(((done + failed) / total) * 100) : 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <Mono size={12} style={{ color: "var(--accent)" }}>
        üretiliyor — {done + failed}/{total || "…"}
      </Mono>
      <div style={BAR}>
        <div style={{ width: `${percent}%`, height: "100%", background: "var(--accent)" }} />
      </div>
      {current && (
        <Mono size={11} style={{ color: "var(--ink-3)", whiteSpace: "nowrap",
                                 overflow: "hidden", textOverflow: "ellipsis" }}>
          {current.number}_{current.letter} · {current.prompt}
        </Mono>
      )}
      {failed > 0 && (
        <Note size={12} style={{ color: "var(--danger)" }}>{failed} kare başarısız — atlandı</Note>
      )}
      <Btn onClick={onStop} style={{ justifyContent: "center", padding: "8px 12px" }}>Durdur</Btn>
      <Note size={11} style={{ color: "var(--ink-3)" }}>
        Durdurunca süren kare tamamlanır, sıradaki başlamaz.
      </Note>
    </div>
  );
}
