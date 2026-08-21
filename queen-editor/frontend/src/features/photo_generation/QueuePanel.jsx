import { useState } from "react";

import ConfirmModal from "../../shared/ConfirmModal.jsx";
import { RawOutput } from "../../shared/RawOutput.jsx";
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

/** The engine's own error: the rule's sentence, then the service's answer under it.
 *
 * Two things that are read differently -- one is a sentence, the other is evidence -- so they are
 * drawn differently. A one line error has no evidence to fold and gets no box.
 */
function splitReason(text) {
  const nl = text.indexOf("\n");
  return nl < 0 ? { said: text, raw: "" }
    : { said: text.slice(0, nl), raw: text.slice(nl + 1) };
}

// The dot carries the whole state at a glance: colour says what is happening, motion says whether
// the engine is still turning. Only the two states where work is in flight pulse.
const DOT = {
  running: { color: "var(--accent)", alive: true },
  // Still beating while the pause is on its way -- the engine is still turning -- but no longer in
  // the colour that means work is flowing (Fark 43).
  pausing: { color: "var(--ink-3)", alive: true },
  paused: { color: "var(--ink-3)", alive: false },
  stopped: { color: "var(--danger)", alive: false },
  waiting: { color: "var(--ink-3)", alive: false },
  done: { color: "var(--ok)", alive: false },
  empty: { color: "var(--border)", alive: false },
};

const TITLE = {
  running: "Üretiliyor",
  pausing: "Duraklatılıyor…",
  paused: "Duraklatıldı",
  stopped: "Üretim durdu",
  waiting: "Bekliyor — üretici kurulu değil",
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

// The order the engine works in, and what a card of each kind counts. A photo job opens a new
// frame, so counting frames is right there; a video or audio job produces a layer of a frame that
// already exists, which is why those count jobs instead (madde 34/35).
const KINDS = {
  photo: { title: "Foto", unit: "kare bekliyor" },
  video: { title: "Video", unit: "iş bekliyor" },
  audio: { title: "Ses", unit: "iş bekliyor" },
};
const KIND_ORDER = ["photo", "video", "audio"];

// The words the failure card breaks its total down with -- the same question asked about the other
// end of the run.
const LAYER_WORD = { photo: "foto", video: "video", audio: "ses" };

// The run card wears what it is saying. Every other state stays neutral.
const CARD_TONE = {
  done: { borderColor: "var(--ok)", background: "var(--ok-bg)" },
  stopped: { borderColor: "var(--danger)", background: "var(--danger-bg)" },
};

// One kind's share of the queue. The card the engine has in hand is the one worth looking at; the
// rest wait their turn and step back rather than compete with it -- unless they have something to
// say, and a warning written at .55 is a warning nobody reads (Fark 38).
function KindCard({ layer, owed, alive, producer, onInstall }) {
  const kind = KINDS[layer];
  const missing = Boolean(producer) && !producer.installed;
  return (
    <div data-kind={layer} className="wf-stroke"
         style={{ padding: "10px 12px", display: "flex", flexDirection: "column", gap: 8,
                  ...(alive ? { borderColor: "var(--accent)" }
                    : missing ? {} : { opacity: 0.55 }) }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span aria-hidden="true" className={alive ? "qe-dot qe-dot--alive" : "qe-dot"}
              style={{ background: alive ? "var(--accent)" : "var(--ink-3)" }} />
        <Note size={12} style={{ color: alive ? "var(--ink-2)" : "var(--ink-3)" }}>
          {/* Three states, three words (Fark 41). "sırada" says a turn is coming; a kind with no
              producer cannot have one until something lands on the machine. */}
          {kind.title} — {alive ? "üretiliyor" : missing ? "bekliyor" : "sırada"}
        </Note>
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
        {/* The accent stays on the heading row, where the dot is: three numbers in the same loud
            colour made the panel one big counter and said nothing about which one is moving
            (Fark 42). */}
        <Mono size={26} style={{ color: alive ? "var(--ink)" : "var(--ink-3)" }}>{owed}</Mono>
        <Note size={13} style={{ color: "var(--ink-2)" }}>{kind.unit}</Note>
      </div>
      {missing && (
        // The answer has been in hand since startup -- what is installed cannot change while the
        // app is up -- so there is no reason to hold it back until the engine reaches this kind.
        // The producer is not named again: the card's own heading already says which one it is.
        <>
          <Note size={12} style={{ color: "var(--ink-2)" }}>Üretici kurulu değil.</Note>
          {/* Kur installs nothing (FOUNDATION 9): it writes the one sentence the app can answer
              with onto that producer's row, and the sentence belongs where the button is. */}
          {producer.note && (
            <Note size={12} style={{ color: "var(--ink-3)" }}>{producer.note}</Note>
          )}
          <Btn sm hl onClick={() => onInstall(layer)} style={{ justifyContent: "center" }}>Kur</Btn>
        </>
      )}
    </div>
  );
}

// Artboard 05: a card per kind of work, then whatever the run itself has to say. Everything the
// run has to say lives here; the form panel next door only submits work.
export default function QueuePanel({ job, error, errorField, busyElsewhere, project, stopping,
                                     queue, failures, producers, onStop, onResume, onCancel,
                                     onRetryAll, onInstall }) {
  const [clearing, setClearing] = useState(false);

  // Another project's finished batch must not talk into this panel (state leaks across projects
  // otherwise -- the worker is global but the words on screen are this project's).
  const mine = job.project === project;
  // The engine's own order, whatever order the list arrived in.
  const cards = KIND_ORDER
    .map((layer) => (queue || []).find((card) => card.layer === layer))
    .filter(Boolean);
  const owed = cards.reduce((total, card) => total + card.owed, 0);
  const failed = (failures || []).reduce((total, kind) => total + kind.count, 0);
  // "3 kare üretilemedi — 2 foto · 1 video". With one kind the breakdown would only say the total
  // again, so it is left out.
  const breakdown = (failures || []).length > 1
    ? ` — ${failures.map((k) => `${k.count} ${LAYER_WORD[k.layer]}`).join(" · ")}`
    : "";
  // A field error belongs under its own box in the form panel, never here.
  const errorInfo = error && !errorField ? describeError(error) : null;

  const running = job.status === "running" && !busyElsewhere;
  const paused = mine && job.status === "paused";
  const halted = mine && job.status === "error";
  // What the stopped card has to say, in its two parts. Read here rather than in the card so the
  // split sits beside describeError, which answers the same question for a connection failure.
  const stopped = halted && job.error ? splitReason(job.error) : null;
  // Nothing failed: the engine for the job at the head of the queue is simply not on this machine.
  const waitingFor = mine && job.status === "waiting" ? job.waitingFor : null;
  // Nothing on this screen starts work by itself -- not a queue a dead session left owing frames,
  // and not one that stopped for a producer that has since arrived (user's decision, 2026-08-13).
  // A machine that starts rendering while nobody is looking is the one thing the user asked us to
  // stop doing. What is owed is still owed: the queue lives on disk, and the button below carries
  // it on. It is offered only once the producer is really here, because resuming without it would
  // stop at the same frame. Read from the rows the panel already has rather than taken as a
  // second-hand answer: one rule, one owner.
  const producerReady = Boolean(waitingFor)
    && (producers || []).some((row) => row.id === waitingFor && row.installed);
  // A run that died with its session leaves frames owed and nobody who remembers why.
  const abandoned = !halted && !paused && !running && !waitingFor && owed > 0;
  const finished = mine && job.status === "done" && owed === 0;

  // An abandoned queue reads as paused, not as a failure: the runtime went away, nothing broke.
  // Only a run the engine really stopped keeps the red card, so the two can be told apart. Their
  // buttons stay different -- one queue was left on purpose, the other was not.
  const state = running ? (stopping ? "pausing" : "running")
    : paused || abandoned ? "paused"
    : waitingFor ? "waiting"
    : halted ? "stopped"
    : finished ? "done"
    : "empty";

  // The queue can only be emptied when nothing is being rendered: a frame in flight has no line in
  // the log yet, so it would read as owed and get pulled out from underneath the worker. A queue
  // waiting for a producer has nothing in hand either, so the way out belongs there too (Fark 47).
  const canClear = (paused || halted || abandoned || Boolean(waitingFor)) && owed > 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10, flex: 1, minHeight: 0 }}>
      {cards.map((card) => (
        <KindCard key={card.layer} layer={card.layer} owed={card.owed}
                  producer={(producers || []).find((row) => row.id === card.layer)}
                  onInstall={onInstall}
                  // Only while the run is really flowing, and only for the kind whose job the
                  // worker has in hand. A plan written before jobs had types is a photo job.
                  alive={running && !stopping
                         && (job.current?.type || "photo") === card.layer} />
      ))}

      {/* Nothing of its own to say while work is simply flowing: what is happening is written on
          the card of the kind it is happening to. */}
      {state !== "running" && (
      <div data-run-card className="wf-stroke"
           style={{ padding: 14, display: "flex", flexDirection: "column", gap: 8,
                    ...(CARD_TONE[state] || {}) }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Dot state={state} />
          <Mono size={12} style={{ color: state === "stopped" ? "var(--danger)"
            : state === "done" ? "var(--ok)"
            : state === "pausing" ? "var(--ink-3)" : "var(--ink-2)" }}>{TITLE[state]}</Mono>
        </div>

        {state === "done" ? (
          // Good news only: what failed has a card of its own, and one sentence cannot carry both.
          // The heading is what carries the news; this line is a fact under it (Fark 44).
          <Note size={12} style={{ color: "var(--ink-3)" }}>{job.done} kare üretildi</Note>
        ) : state === "empty" ? (
          <Note size={12} style={{ color: "var(--ink-3)" }}>
            Fotoğraf üret panelinden kare gönder.
          </Note>
        ) : state === "waiting" ? (
          <>
            <Note size={12} style={{ color: "var(--ink-2)" }}>
              {(cards.find((card) => card.layer === waitingFor) || {}).owed || 0}{" "}
              {LAYER_WORD[waitingFor]}
            </Note>
            {/* Once the producer is on the machine the queue could go on, but it waits for a
                press like every other queue does. Before that, saying so would offer a button
                that stops at the same frame. */}
            {producerReady ? (
              <Btn hl onClick={onResume} style={{ justifyContent: "center" }}>
                <Icon.Regen /> Kaldığı yerden devam et
              </Btn>
            ) : (
              // The way in to the install is on the card of the kind that is missing it, not here:
              // this card speaks for the run, and what is missing belongs to one kind (Fark 38).
              <Note size={12} style={{ color: "var(--ink-3)" }}>
                Üretici kurulduktan sonra kuyruğu sen sürdürürsün.
              </Note>
            )}
          </>
        ) : null}

        {/* Only when the server knows why. A run that died with the session left no reason behind,
            and inventing one is worse than saying nothing. */}
        {stopped && (
          // The sentence stays a sentence; the service's answer is folded into its own box, which
          // is what keeps a sixty line failure from pushing the buttons under it out of the panel.
          <>
            <Mono size={10} style={{ color: "var(--ink-3)", whiteSpace: "pre-wrap" }}>
              {stopped.said}
            </Mono>
            {stopped.raw && <RawOutput text={stopped.raw} />}
          </>
        )}

        {busyElsewhere && (
          <Note size={12} style={{ color: "var(--ink-3)" }}>
            Üretim sürüyor: {job.project} — bitmesini bekle.
          </Note>
        )}
      </div>
      )}

      {/* Its own card, outside the run's -- and only once the queue is through (Fark 46): a total
          that is still growing is not a total, and every red frame is already red in the gallery
          with a Tekrar dene of its own. */}
      {failed > 0 && state === "done" && (
        <div className="wf-stroke"
             style={{ padding: 14, display: "flex", flexDirection: "column", gap: 8,
                      borderColor: "var(--danger)", background: "var(--danger-bg)" }}>
          <Note size={12} style={{ color: "var(--danger)" }}>
            {failed} kare üretilemedi{breakdown}
          </Note>
          {/* The card does something rather than sending the user somewhere: the failed frames are
              already red in the gallery, so pointing at them was never the useful half. */}
          <Btn sm onClick={onRetryAll}
               style={{ alignSelf: "flex-start", color: "var(--danger)",
                        borderColor: "var(--danger)", background: "none" }}>
            <Icon.Regen /> Tekrar dene
          </Btn>
        </div>
      )}

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

      {/* The destructive button is pushed to the foot of the panel: it and the main button are not
          two choices of the same weight, and the distance is what says so. */}
      {canClear && <div style={{ flex: 1, minHeight: 8 }} />}

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
                + "Üretilmiş kareler galeride kalır."}
          confirmLabel="Boşalt"
          width={380}
          danger
          onCancel={() => setClearing(false)}
          onConfirm={() => { setClearing(false); onCancel(); }}
        />
      )}
    </div>
  );
}
