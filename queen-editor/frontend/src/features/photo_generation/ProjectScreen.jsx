import { useState } from "react";

import { exportUrl } from "../../shared/api.js";
import ConfirmModal from "../../shared/ConfirmModal.jsx";
import { navigate } from "../../shared/router.js";
import { Btn, Hand } from "../../vendor/kit.jsx";
import Gallery from "./Gallery.jsx";
import SidePanel from "./SidePanel.jsx";
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
export default function ProjectScreen({ project, settings, onSaveSettings }) {
  const { job, photos, error, errorField, stopping, queue, pending, failures,
          generate, stop, resume, cancel, retry, clearError,
          reorder, removePhotos } = useGeneration(project);
  const [saveError, setSaveError] = useState(null);
  const [leaving, setLeaving] = useState(false);
  // The worker is global: a batch started from another project blocks this one (the server 409s).
  const busyElsewhere = job.status === "running" && job.project !== project;
  const running = job.status === "running" && !busyElsewhere;
  // Whose run the status describes: another project's queue must not draw tiles into this gallery.
  const mine = job.project === project;

  // Pressing Üretime ekle persists the panel first, whether or not the frames are accepted -- text
  // the server rejects is still what the user typed. Both writes land in the same folder, so
  // settings that cannot be written mean the photos could not be either: say so and do not send.
  // Answers with the server's body so the panel can quote how many frames the queue took.
  async function handleGenerate(form) {
    setSaveError(null);
    try {
      await onSaveSettings({
        prompts: form.prompts, negative: form.negative, variants: form.variants,
      });
    } catch (err) {
      setSaveError(err.message);
      return null;
    }
    return generate(form);
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={HEADER}>
        <Hand size={20}><span className="wf-hl">Queen Editor</span></Hand>
        <Hand size={20}>{project}</Hand>
        <div style={{ display: "flex", gap: 8, justifySelf: "end" }}>
          {/* A link, not a Btn: its whole job is downloading a file, which the browser does by
              itself -- no JavaScript, and "save link as" keeps working. The look is the design's
              ghost button; app.css drops the anchor's underline. */}
          <a className="wf-btn wf-btn--ghost" href={exportUrl(project)} download>Export</a>
          <Btn ghost onClick={() => setLeaving(true)}>Projeden çık</Btn>
        </div>
      </div>

      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        {/* The artboard can clip its gallery because it is a fixed-height frame; a real page
            has to scroll, otherwise most of a 48-photo run is unreachable. */}
        <div style={{ flex: 1, minWidth: 0, overflowY: "auto" }}>
          <Gallery project={project} photos={photos} current={running ? job.current : null}
                   pending={pending} failures={failures}
                   onReorder={reorder} onDelete={removePhotos} onRetry={retry} />
        </div>
        <SidePanel job={job} error={saveError || error} errorField={errorField}
                   busyElsewhere={busyElsewhere} settings={settings} project={project}
                   stopping={stopping} queue={queue} onGenerate={handleGenerate} onStop={stop}
                   onResume={resume} onCancel={cancel} onClearError={clearError} />
      </div>

      {leaving && (
        <ConfirmModal title="Projeden çıkılsın mı?" confirmLabel="Çık"
                      onCancel={() => setLeaving(false)} onConfirm={() => navigate("/")} />
      )}
    </div>
  );
}
