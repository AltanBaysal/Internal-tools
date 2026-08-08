import { Btn, Icon, Mono, Note } from "../../vendor/kit.jsx";
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import ProgressPanel from "./ProgressPanel.jsx";

/** api.js prefixes an unreachable-server message with "Sunucuya ulaşılamadı" (see shared/api.js);
 * anything else is a request the server itself rejected. The headline names which one happened so
 * a dead tunnel doesn't read as a bad request, and the raw line drops the now-redundant Turkish
 * prefix so it shows the underlying browser detail instead of repeating the headline.
 */
function describeError(text) {
  if (text.startsWith("Sunucuya ulaşılamadı")) {
    const nl = text.indexOf("\n");
    return { headline: "Sunucuya ulaşılamıyor", raw: nl >= 0 ? text.slice(nl + 1) : text };
  }
  return { headline: "İstek reddedildi", raw: text };
}

// Artboard 05: everything the run has to say. The form panel next door only submits work; whether
// it is flowing, paused, stopped or finished is answered here and nowhere else.
export default function QueuePanel({ job, error, errorField, busyElsewhere, project, stopping,
                                     queue, onStop, onResume, onCancel }) {
  const running = job.status === "running" && !busyElsewhere;
  // Another project's finished batch must not talk into this panel (state leaks across projects
  // otherwise -- the worker is global but the words on screen are this project's).
  const mine = job.project === project;
  // A field error belongs under its own box in the form panel, never here.
  const errorInfo = error && !errorField ? describeError(error) : null;
  const paused = mine && job.status === "paused";
  const owed = queue?.pending?.length || 0;
  // Two ways a run can be left unfinished: it died in front of us (the server still knows why), or
  // it died with the session (Drive remembers the queue, nobody remembers the reason).
  const halted = mine && job.status === "error";
  const abandoned = !halted && !paused && job.status !== "running" && owed > 0;
  const unfinished = halted || abandoned;

  if (unfinished) {
    // Artboard 13: the same shape as the finished card -- big button, status card under it.
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Btn hl onClick={onResume}
             style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
          <Icon.Regen /> Kaldığı yerden devam et
        </Btn>
        <div className="wf-stroke"
             style={{ padding: "8px 10px", display: "flex", flexDirection: "column", gap: 6,
                      borderColor: "var(--danger)", background: "var(--danger-bg)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--danger)" }}>
            <Icon.Warn />
            <Note size={12} style={{ color: "var(--danger)", fontWeight: 500 }}>
              {halted
                ? `Üretim durdu — ${job.done}/${job.total} tamamlandı`
                : `Üretim yarım kaldı — ${queue.total - owed}/${queue.total} tamamlandı`}
            </Note>
          </div>
          {/* Only when the reason is known. A run that died with the session left no reason
              behind, and inventing one is worse than saying nothing. */}
          {halted && job.error && (
            <Mono size={10} style={{ color: "var(--ink-3)" }}>{job.error}</Mono>
          )}
        </div>
      </div>
    );
  }

  if (paused) {
    // Artboard 12: the way back on top, what happened under it, and the way out at the bottom.
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Btn hl onClick={onResume}
             style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
          <Icon.Regen /> Devam et
        </Btn>
        <div className="wf-stroke" style={{ padding: "8px 10px" }}>
          <Note size={12} style={{ color: "var(--ink-2)", display: "block" }}>
            Üretim duraklatıldı — {job.done}/{job.total} tamamlandı
          </Note>
        </div>
        <Btn ghost onClick={onCancel}
             style={{ justifyContent: "center", color: "var(--ink-3)" }}>İptal et</Btn>
        {errorInfo && <StatusErrorCard text={errorInfo.headline} raw={errorInfo.raw} />}
      </div>
    );
  }

  if (running) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {/* While polls fail, the bar shows the LAST KNOWN state, not the present — dim it so a
            frozen counter cannot read as live progress, and let the card carry the last-known
            numbers ("the screen never claims what it does not know"). */}
        <div style={errorInfo ? { opacity: 0.45 } : undefined}>
          <ProgressPanel job={job} stopping={stopping} onStop={onStop} />
        </div>
        {errorInfo && (
          <StatusErrorCard
            text={`${errorInfo.headline} — son bilinen: ${job.done ?? 0}/${job.total || "?"}`}
            raw={errorInfo.raw}
          />
        )}
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      {errorInfo ? (
        <StatusErrorCard text={errorInfo.headline} raw={errorInfo.raw} />
      ) : mine && job.status === "done" ? (
        <div className="wf-stroke"
             style={{ padding: "8px 10px", display: "flex", alignItems: "center", gap: 8,
                      borderColor: "var(--ok)", background: "var(--ok-bg)" }}>
          <Mono size={13} style={{ color: "var(--ok)" }}>✓</Mono>
          <Note size={12} style={{ color: "var(--ok)" }}>
            {job.done} / {job.total} üretildi — tamamlandı
          </Note>
        </div>
      ) : busyElsewhere ? (
        <Note size={12} style={{ color: "var(--ink-3)" }}>
          Üretim sürüyor: {job.project} — bitmesini bekle.
        </Note>
      ) : null}
    </div>
  );
}
