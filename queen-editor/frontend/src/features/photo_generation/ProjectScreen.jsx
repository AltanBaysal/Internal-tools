import { navigate } from "../../shared/router.js";
import { Btn, Hand } from "../../vendor/kit.jsx";
import Gallery from "./Gallery.jsx";
import GeneratePanel from "./GeneratePanel.jsx";
import ProgressPanel from "./ProgressPanel.jsx";
import { useGeneration } from "./useGeneration.js";

const HEADER = {
  display: "grid",
  gridTemplateColumns: "1fr auto 1fr",
  alignItems: "center",
  padding: "14px 32px",
  background: "var(--bg-2)",
  borderBottom: "1px solid var(--border)",
};

// Artboard 03/04: gallery on the LEFT (the content), panel on the RIGHT (the controls).
export default function ProjectScreen({ project }) {
  const { job, photos, error, generate, stop } = useGeneration(project);
  const running = job.status === "running";
  // The worker is global: a batch started from another project blocks this one (the server 409s).
  const busyElsewhere = running && job.project !== project;

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <div style={HEADER}>
        <Btn ghost onClick={() => navigate("/")}>← Projeler</Btn>
        <Hand size={20}>{project}</Hand>
        <span />
      </div>

      <div style={{ flex: 1, display: "flex", gap: 32, padding: "24px 32px", alignItems: "flex-start" }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <Gallery project={project} photos={photos} />
        </div>
        <div style={{ width: 380, flexShrink: 0 }}>
          {running && !busyElsewhere
            ? <ProgressPanel job={job} onStop={stop} />
            : <GeneratePanel job={job} error={error} busyElsewhere={busyElsewhere}
                             onGenerate={generate} />}
        </div>
      </div>
    </div>
  );
}
