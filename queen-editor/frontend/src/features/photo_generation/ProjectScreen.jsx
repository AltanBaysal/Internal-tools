import { navigate } from "../../shared/router.js";
import { Btn, Hand } from "../../vendor/kit.jsx";
import Gallery from "./Gallery.jsx";
import GeneratePanel from "./GeneratePanel.jsx";
import { useGeneration } from "./useGeneration.js";

const HEADER = {
  display: "grid",
  gridTemplateColumns: "1fr auto 1fr",
  alignItems: "center",
  padding: "14px 32px",
  background: "var(--bg-2)",
  borderBottom: "1px solid var(--border)",
};

// Artboard 03/04: gallery on the left (the content), the 320px panel on the right (the controls).
// The panel stays put while a batch runs -- only its bottom block swaps (see GeneratePanel).
export default function ProjectScreen({ project }) {
  const { job, photos, error, generate, stop } = useGeneration(project);
  // The worker is global: a batch started from another project blocks this one (the server 409s).
  const busyElsewhere = job.status === "running" && job.project !== project;
  const running = job.status === "running" && !busyElsewhere;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={HEADER}>
        <Hand size={20}><span className="wf-hl">Queen Editor</span></Hand>
        <Hand size={20}>{project}</Hand>
        <Btn ghost style={{ color: "var(--danger)", justifySelf: "end" }}
             onClick={() => navigate("/")}>Projeden çık</Btn>
      </div>

      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        {/* The artboard can clip its gallery because it is a fixed-height frame; a real page
            has to scroll, otherwise most of a 48-photo run is unreachable. */}
        <div style={{ flex: 1, minWidth: 0, overflowY: "auto" }}>
          <Gallery project={project} photos={photos} current={running ? job.current : null} />
        </div>
        <GeneratePanel job={job} error={error} busyElsewhere={busyElsewhere}
                       onGenerate={generate} onStop={stop} />
      </div>
    </div>
  );
}
