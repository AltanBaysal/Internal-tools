import { useEffect, useState } from "react";

import { getExportSummary } from "../../shared/api.js";
import { navigate, projectPath } from "../../shared/router.js";
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Btn, Hand, Icon, Mono, Note } from "../../vendor/kit.jsx";

const HEADER = {
  display: "grid", gridTemplateColumns: "1fr auto 1fr", alignItems: "center",
  padding: "14px 32px", background: "var(--bg-2)", borderBottom: "1px solid var(--border)",
};
// The design's own width: one column, 560px, centred in whatever room the window has.
const PAGE = { width: 560, maxWidth: "100%", margin: "0 auto", padding: 32,
               display: "flex", flexDirection: "column", gap: 20, boxSizing: "border-box" };
const CARD = { border: "1px solid var(--border)", borderRadius: "var(--r-sm)", padding: 20,
               display: "flex", flexDirection: "column", gap: 14, textAlign: "left" };
const RULE = { height: 1, background: "var(--border)" };

/** Seconds as the design writes them: "1:50". Minutes are never padded, seconds always are. */
function clock(seconds) {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

// Artboard 12: the fourth screen. It is the confirm step itself -- pressing an export button opens
// no window, and changing your mind means going back to the gallery (madde 88).
export default function ExportScreen({ project }) {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let alive = true;
    getExportSummary(project)
      .then((body) => { if (alive) setSummary(body); })
      .catch((err) => { if (alive) setError(err.message); });
    return () => { alive = false; };
  }, [project]);

  // No video means nothing to export: the card turns into the sentence that says what to do
  // instead, and it is not drawn as an error (madde 95).
  const empty = summary && summary.videos === 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={HEADER}>
        <Hand size={20}><span className="wf-hl">Queen Editor</span></Hand>
        <Hand size={20}>{project} · Export</Hand>
        <Btn ghost style={{ justifySelf: "end" }} onClick={() => navigate(projectPath(project))}>
          <Icon.Left /> Galeriye dön
        </Btn>
      </div>

      <div style={{ flex: 1, overflowY: "auto" }}>
        <div style={PAGE}>
          {/* Outside the card, and the only 30pt line on the screen. */}
          <Hand size={30}>{project}</Hand>

          {error ? (
            <StatusErrorCard text="Export özeti yüklenemedi" raw={error} />
          ) : summary === null ? (
            <div style={{ ...CARD, alignItems: "center" }}><span className="wf-spinner" /></div>
          ) : (
            <>
              <div style={CARD}>
                <Note size={26}>
                  {empty
                    ? "Export edilecek video yok"
                    : `${summary.videos} video export edilecek · ${clock(summary.seconds)} dk`}
                </Note>
                {empty && (
                  <Note size={14} style={{ color: "var(--ink-2)", lineHeight: 1.5 }}>
                    Hiçbir karenin videosu yok — önce Video üret panelinden video üret.
                  </Note>
                )}
                <div style={RULE} />
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <Note size={14} style={{ color: "var(--ink-2)" }}>Şuraya yazılacak:</Note>
                  {/* The path is read, not typed: monospace so a long Drive path stays legible. */}
                  <Mono size={12} style={{ color: "var(--ink-3)", wordBreak: "break-all" }}>
                    {summary.folder}
                  </Mono>
                </div>
              </div>

              {/* Two equal buttons, no hierarchy and no explanation line (madde 87). */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <Btn hl disabled={empty} style={{ justifyContent: "center" }}>
                  Birleşik videoyu export et
                </Btn>
                <Btn hl disabled={empty} style={{ justifyContent: "center" }}>
                  Videoları ayrı export et
                </Btn>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
