import { useState } from "react";

import ConfirmModal from "../../shared/ConfirmModal.jsx";
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Btn, Icon, Mono, Note } from "../../vendor/kit.jsx";

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

// The dot carries the whole state at a glance: colour says what is happening, motion says whether
// the engine is still turning. Only the two states where work is in flight pulse.
const DOT = {
  running: { color: "var(--accent)", alive: true },
  pausing: { color: "var(--accent)", alive: true },
  paused: { color: "var(--ink-3)", alive: false },
  stopped: { color: "var(--danger)", alive: false },
  done: { color: "var(--ok)", alive: false },
  empty: { color: "var(--border)", alive: false },
};

const TITLE = {
  running: "Üretiliyor",
  pausing: "Duraklatılıyor…",
  paused: "Duraklatıldı",
  stopped: "Üretim durdu",
  done: "Kuyruk tamamlandı",
  empty: "Kuyruk boş",
};

function Dot({ state }) {
  const { color, alive } = DOT[state];
  return (
    <span aria-hidden="true"
          className={alive ? "qe-dot qe-dot--alive" : "qe-dot"}
          style={{ background: color }} />
  );
}

// Artboard 05: one card, one number, one button. Everything the run has to say lives here; the
// form panel next door only submits work.
export default function QueuePanel({ job, error, errorField, busyElsewhere, project, stopping,
                                     pending, failures, onStop, onResume, onCancel,
                                     onShowFailures }) {
  const [clearing, setClearing] = useState(false);

  // Another project's finished batch must not talk into this panel (state leaks across projects
  // otherwise -- the worker is global but the words on screen are this project's).
  const mine = job.project === project;
  const owed = pending?.length || 0;
  const failed = failures?.length || 0;
  // A field error belongs under its own box in the form panel, never here.
  const errorInfo = error && !errorField ? describeError(error) : null;

  const running = job.status === "running" && !busyElsewhere;
  const paused = mine && job.status === "paused";
  const halted = mine && job.status === "error";
  // A run that died with its session leaves frames owed and nobody who remembers why.
  const abandoned = !halted && !paused && !running && owed > 0;
  const finished = mine && job.status === "done" && owed === 0;

  const state = running ? (stopping ? "pausing" : "running")
    : paused ? "paused"
    : halted || abandoned ? "stopped"
    : finished ? "done"
    : "empty";

  // The queue can only be emptied when nothing is being rendered: a frame in flight has no line in
  // the log yet, so it would read as owed and get pulled out from underneath the worker.
  const canClear = (paused || halted || abandoned) && owed > 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <div className="wf-stroke" style={{ padding: "10px 12px", display: "flex",
                                          flexDirection: "column", gap: 8 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Dot state={state} />
          <Note size={12} style={{ color: state === "stopped" ? "var(--danger)"
            : state === "done" ? "var(--ok)" : "var(--ink-2)" }}>{TITLE[state]}</Note>
        </div>

        {state === "done" ? (
          <Note size={12} style={{ color: "var(--ok)" }}>
            {job.done} kare üretildi
            {failed > 0 && <span style={{ color: "var(--danger)" }}>, {failed} hatalı</span>}
          </Note>
        ) : state === "empty" ? (
          <Note size={12} style={{ color: "var(--ink-3)" }}>
            Üretime ekle panelinden kare gönder.
          </Note>
        ) : (
          <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
            <Mono size={26} style={{ color: state === "stopped" ? "var(--danger)" : "var(--ink)" }}>
              {owed}
            </Mono>
            <Note size={13} style={{ color: "var(--ink-2)" }}>kare bekliyor</Note>
          </div>
        )}

        {/* Only when the server knows why. A run that died with the session left no reason behind,
            and inventing one is worse than saying nothing. */}
        {halted && job.error && (
          <Mono size={10} style={{ color: "var(--ink-3)" }}>{job.error}</Mono>
        )}

        {failed > 0 && (
          <button type="button" onClick={onShowFailures}
                  style={{ background: "none", border: "none", padding: 0, textAlign: "left",
                           cursor: "pointer", color: "var(--danger)", font: "inherit",
                           fontSize: 12, textDecoration: "underline" }}>
            {failed} kare üretilemedi — galeride göster
          </button>
        )}

        {busyElsewhere && (
          <Note size={12} style={{ color: "var(--ink-3)" }}>
            Üretim sürüyor: {job.project} — bitmesini bekle.
          </Note>
        )}
      </div>

      {running && (
        <Btn onClick={onStop} disabled={stopping}
             style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14,
                      color: "var(--ink-2)" }}>
          {stopping ? "Duraklatılıyor…" : "Duraklat"}
        </Btn>
      )}
      {paused && (
        <Btn hl onClick={onResume}
             style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
          <Icon.Regen /> Devam et
        </Btn>
      )}
      {(halted || abandoned) && (
        <Btn hl onClick={onResume}
             style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
          <Icon.Regen /> Kaldığı yerden devam et
        </Btn>
      )}

      {canClear && (
        // The destructive standard: no filled red anywhere -- outline, red text, trash icon.
        // Applied app-wide in Madde 6; this button is drawn in it from the start because it is new.
        <Btn onClick={() => setClearing(true)}
             style={{ justifyContent: "center", borderColor: "var(--danger)",
                      color: "var(--danger)", background: "none" }}>
          <Icon.Trash /> Kuyruğu boşalt
        </Btn>
      )}

      {errorInfo && (
        <StatusErrorCard
          text={running || paused
            ? `${errorInfo.headline} — son bilinen: ${owed} kare bekliyor`
            : errorInfo.headline}
          raw={errorInfo.raw}
        />
      )}

      {clearing && (
        <ConfirmModal
          title="Kuyruk boşaltılsın mı?"
          // No "geri alınamaz": nothing is deleted, the same prompts can be queued again.
          body={`Bekleyen ${owed} kare üretilmeden kuyruktan çıkar. `
                + "Üretilmiş fotoğraflar galeride kalır."}
          confirmLabel="Boşalt"
          danger
          onCancel={() => setClearing(false)}
          onConfirm={() => { setClearing(false); onCancel(); }}
        />
      )}
    </div>
  );
}
