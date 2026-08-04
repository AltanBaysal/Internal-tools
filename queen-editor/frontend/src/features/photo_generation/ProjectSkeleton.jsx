import { Hand } from "../../vendor/kit.jsx";

const DASHED = { aspectRatio: "1/1" };

// The project screen's shape while settings load: same bar, empty dashed panel and grid.
// A blank white page reads as "broken"; this reads as "coming" (spec §2.2).
export default function ProjectSkeleton({ project }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr auto 1fr", alignItems: "center",
                    padding: "14px 32px", background: "var(--bg-2)",
                    borderBottom: "1px solid var(--border)" }}>
        <Hand size={20}><span className="wf-hl">Queen Editor</span></Hand>
        <Hand size={20}>{project}</Hand>
        <span />
      </div>
      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        <div style={{ flex: 1, padding: 16 }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 12,
                        alignItems: "start" }}>
            {Array.from({ length: 10 }, (_, i) => (
              <div key={i} className="wf-stroke wf-stroke--dashed" style={DASHED} />
            ))}
          </div>
        </div>
        <div style={{ width: 320, flexShrink: 0, borderLeft: "1px solid var(--border)",
                      padding: 16, display: "flex", flexDirection: "column", gap: 14,
                      boxSizing: "border-box" }}>
          <div className="wf-stroke wf-stroke--dashed" style={{ flex: 1 }} />
          <div className="wf-stroke wf-stroke--dashed" style={{ height: 40 }} />
          <div className="wf-stroke wf-stroke--dashed" style={{ height: 40 }} />
        </div>
      </div>
    </div>
  );
}
