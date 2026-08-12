import { useEffect, useState } from "react";

import {
  cancelExport,
  getExportState,
  getExportSummary,
  startExport,
} from "../../shared/api.js";
import ConfirmModal from "../../shared/ConfirmModal.jsx";
import { navigate, projectPath } from "../../shared/router.js";
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Btn, Hand, Icon, Mono, Note } from "../../vendor/kit.jsx";
import { useGeneration } from "./useGeneration.js";

// The two exports, and what the buttons say. Order is the design's: merged first.
const MODES = ["merged", "separate"];
const LABEL = { merged: "Birleşik videoyu export et", separate: "Videoları ayrı export et" };
// A write in flight, either while pieces are being cut or while they are being joined.
const RUNNING = ["running", "merging"];
const POLL_MS = 1000;

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
const BLOCKED = { border: "1px solid var(--danger)", borderRadius: "var(--r-sm)",
                  background: "var(--danger-bg)", padding: 14,
                  display: "flex", flexDirection: "column", gap: 6 };
// Full width, and the only green on the screen: the export landed.
const DONE = { border: "1px solid #4ade80", borderRadius: "var(--r-sm)",
               background: "rgba(74,222,128,.08)", padding: 14,
               display: "flex", flexDirection: "column", gap: 6 };

/** Seconds as the design writes them: "1:50". Minutes are never padded, seconds always are. */
function clock(seconds) {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

// Artboard 12: the fourth screen. It is the confirm step itself -- pressing an export button opens
// no window, and changing your mind means going back to the gallery (madde 88).
export default function ExportScreen({ project }) {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  // What each mode's export is doing, as the server last said it.
  const [runs, setRuns] = useState({});
  const [leaving, setLeaving] = useState(false);
  // What the queue is doing, from the hook the rest of the app reads it with -- the export screen
  // adds no second count of its own.
  const { job, frames, queue } = useGeneration(project);

  // Asked again whenever the gallery changes: the screen can sit open while the queue drains, and
  // a frozen count would turn its warnings into lies.
  useEffect(() => {
    let alive = true;
    getExportSummary(project)
      .then((body) => { if (alive) setSummary(body); })
      .catch((err) => { if (alive) setError(err.message); });
    return () => { alive = false; };
  }, [project, frames]);

  // No video means nothing to export: the card turns into the sentence that says what to do
  // instead, and it is not drawn as an error (madde 95).
  const empty = summary && summary.videos === 0;
  // Export is blocked while the queue flows: it copies files, and a video being written this very
  // second could be copied half-made. A paused queue has nobody writing (madde 90).
  const flowing = job.status === "running";
  const queuedVideos = (queue.find((card) => card.layer === "video") || {}).owed || 0;
  // Every condition that has one, in the design's own words; a count of zero writes no row at all
  // (madde 89). The queued line belongs here only while nothing is flowing -- otherwise the red
  // card under the card says it, with what to do about it.
  const going = MODES.some((mode) => RUNNING.includes((runs[mode] || {}).state));

  // Only while something is being written: an idle screen asks nothing.
  useEffect(() => {
    if (!going) return undefined;
    const timer = setInterval(() => {
      getExportState(project).then(setRuns).catch(() => {});
    }, POLL_MS);
    return () => clearInterval(timer);
  }, [going, project]);

  function begin(mode) {
    // Believe it started: the answer is a 202 and the first state read comes right behind it.
    setRuns((current) => ({ ...current, [mode]: { state: "running", written: 0, total: 0 } }));
    return startExport(project, mode)
      .then(() => getExportState(project).then(setRuns))
      .catch((err) => setRuns((current) => (
        { ...current, [mode]: { state: "error", error: err.message } })));
  }

  function leave() {
    if (going) return setLeaving(true);
    return navigate(projectPath(project));
  }

  function leaveAnyway() {
    return cancelExport(project)
      .catch(() => {})           // going is going: a refused cancel must not trap the user here
      .then(() => navigate(projectPath(project)));
  }

  const warnings = summary ? [
    summary.silent && `⚠ ${summary.silent} videonun sesi yok`,
    summary.withoutVideo && `⚠ ${summary.withoutVideo} videosuz kare diziye girmeyecek`,
    !flowing && queuedVideos
      && `⚠ ${queuedVideos} karenin videosu kuyrukta bekliyor — diziye girmeyecek`,
  ].filter(Boolean) : [];

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={HEADER}>
        <Hand size={20}><span className="wf-hl">Queen Editor</span></Hand>
        <Hand size={20}>{project} · Export</Hand>
        <Btn ghost style={{ justifySelf: "end" }} onClick={leave}>
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
                {warnings.map((line) => (
                  <Note key={line} size={14} style={{ color: "var(--danger)", lineHeight: 1.5 }}>
                    {line}
                  </Note>
                ))}
                <div style={RULE} />
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <Note size={14} style={{ color: "var(--ink-2)" }}>Şuraya yazılacak:</Note>
                  {/* The path is read, not typed: monospace so a long Drive path stays legible. */}
                  <Mono size={12} style={{ color: "var(--ink-3)", wordBreak: "break-all" }}>
                    {summary.folder}
                  </Mono>
                </div>
              </div>

              {flowing && (
                /* Its own red card right above the buttons, not a line in the summary: this one
                   is not a warning about the result, it is the reason the buttons are dead. */
                <div style={BLOCKED}>
                  <Note size={14} style={{ color: "var(--danger)", lineHeight: 1.5 }}>
                    ⚠ Üretim sürüyor — {queuedVideos} video kuyrukta. Kuyruğun bitmesini bekle veya
                    duraklat.
                  </Note>
                </div>
              )}

              {/* Two equal buttons, no hierarchy and no explanation line (madde 87). While one is
                  writing, its own button carries the progress and the other stays pressable. */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                {MODES.map((mode) => {
                  const run = runs[mode] || {};
                  const busy = RUNNING.includes(run.state);
                  return (
                    <Btn key={mode} hl disabled={empty || flowing || busy}
                         onClick={() => begin(mode)} style={{ justifyContent: "center" }}>
                      {busy ? (
                        <>
                          {/* A live dot, no percentage and no bar (madde 93). */}
                          <span aria-hidden="true" className="qe-dot qe-dot--alive"
                                style={{ background: "currentColor", width: 6, height: 6 }} />
                          {run.state === "merging"
                            ? "birleştiriliyor…"
                            : `${run.written} / ${run.total} yazıldı…`}
                        </>
                      ) : LABEL[mode]}
                    </Btn>
                  );
                })}
              </div>

              {MODES.filter((mode) => (runs[mode] || {}).state === "done").map((mode) => (
                <div key={mode} style={DONE}>
                  <Note size={14} style={{ color: "var(--ok, #4ade80)" }}>✓ Export tamamlandı</Note>
                  <Mono size={12} style={{ color: "var(--ink-3)", wordBreak: "break-all" }}>
                    {LABEL[mode]} → {runs[mode].target}
                  </Mono>
                </div>
              ))}

              {MODES.filter((mode) => (runs[mode] || {}).state === "error").map((mode) => (
                /* The tool's own last line, and no retry of its own: the buttons are where they
                   were and a new press opens a new folder (madde 94). */
                <div key={mode} style={BLOCKED}>
                  <Note size={14} style={{ color: "var(--danger)" }}>Export başarısız</Note>
                  <Mono size={12} style={{ color: "var(--ink-2)", wordBreak: "break-all" }}>
                    {runs[mode].error}
                  </Mono>
                </div>
              ))}
            </>
          )}
        </div>
      </div>

      {leaving && (
        /* Not a destructive action, so the confirm is the accent one: what is lost is a run, not
           anything the gallery holds (madde 96). */
        <ConfirmModal
          title="Export sürüyor — çıkılsın mı?"
          body={"Çıkarsan export iptal olur, yarım kalan klasör silinir. "
                + "Galerine ve karelerine dokunulmaz."}
          confirmLabel="Çık" width={400}
          onCancel={() => setLeaving(false)} onConfirm={leaveAnyway} />
      )}
    </div>
  );
}
