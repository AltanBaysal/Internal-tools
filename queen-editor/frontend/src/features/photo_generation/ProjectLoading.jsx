import { Hand } from "../../vendor/kit.jsx";

// The project screen while settings load: the same bar (so the user knows where they are) over a
// single centered spinner. A blank white page reads as "broken"; this reads as "coming".
export default function ProjectLoading({ project }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr auto 1fr", alignItems: "center",
                    padding: "14px 32px", background: "var(--bg-2)",
                    borderBottom: "1px solid var(--border)" }}>
        <Hand size={20}><span className="wf-hl">Queen Editor</span></Hand>
        <Hand size={20}>{project}</Hand>
        <span />
      </div>
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <span className="wf-spinner" />
      </div>
    </div>
  );
}
