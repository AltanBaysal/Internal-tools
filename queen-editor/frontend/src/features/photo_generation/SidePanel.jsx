import { useState } from "react";

import { Mono } from "../../vendor/kit.jsx";
import AgentPanel from "./AgentPanel.jsx";
import GeneratePanel from "./GeneratePanel.jsx";
import ProducersPanel from "../producers/ProducersPanel.jsx";
import {
  AgentGlyph,
  PhotoGlyph,
  ProducersGlyph,
  QueueGlyph,
  SoundGlyph,
  VideoGlyph,
} from "./glyphs.jsx";
import LayerPanel from "./LayerPanel.jsx";
import QueuePanel from "./QueuePanel.jsx";

const COLUMN = { display: "flex", flexShrink: 0 };

const PANEL = {
  width: 320,
  borderLeft: "1px solid var(--border)",
  padding: 16,
  display: "flex",
  flexDirection: "column",
  gap: 14,
  overflow: "hidden",
  boxSizing: "border-box",
};

const RAIL = {
  width: 48,
  flexShrink: 0,
  borderLeft: "1px solid var(--border)",
  // The rail has a ground of its own now, and its cells span its full width.
  background: "var(--bg-2)",
  display: "flex",
  flexDirection: "column",
  alignItems: "stretch",
  paddingTop: 12,
  boxSizing: "border-box",
};

const LABEL = { color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" };

// Which panel gets which icon. The drawings live in glyphs.jsx, because the photo one is also the
// icon its own submit button carries.
const GLYPH = { photo: PhotoGlyph, video: VideoGlyph, audio: SoundGlyph, queue: QueueGlyph,
                agent: AgentGlyph, producers: ProducersGlyph };

// Adding a panel later means adding a row here -- the rail is drawn from this list, not from three
// hard-coded buttons. The id is the layer's own word, so it matches both the glyph's name and what
// the server calls that kind of job. `title` is what the rail's icon is called; `heading` is what
// the open panel is called, and the queue is the one place the design gives those two different
// words.
const PANELS = [
  { id: "photo", title: "Fotoğraf üret" },
  { id: "video", title: "Video üret" },
  { id: "audio", title: "Ses üret" },
  { id: "queue", title: "Kuyruğu takip et", heading: "Kuyruk" },
  { id: "agent", title: "AI agent" },
  { id: "producers", title: "Üreticiler", apart: true },
];

const BUTTON = {
  position: "relative",
  width: "100%",
  height: 46,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "none",
  border: "none",
  padding: 0,
  cursor: "pointer",
  // The open panel's mark is a full-height edge; the others carry the same width in nothing at
  // all, so the icons do not shift when the selection moves. Written long-hand because the colour
  // is the only part that changes, and mixing it with the shorthand confuses React's style diff.
  borderRightWidth: 2,
  borderRightStyle: "solid",
  borderRightColor: "transparent",
};

function RailButton({ panel, active, busy, onSelect }) {
  const Glyph = GLYPH[panel.id];
  return (
    <button type="button" aria-label={panel.title} aria-current={active ? "page" : undefined}
            onClick={() => onSelect(panel.id)}
            style={{ ...BUTTON, color: active ? "var(--accent)" : "var(--ink-3)",
                     ...(active ? { borderRightColor: "var(--accent)" } : {}),
                     // Set apart at the foot: it is about the machine, not this project's work.
                     ...(panel.apart ? { marginTop: "auto", marginBottom: 12 } : {}) }}>
      <Glyph />
      {/* Something is landing behind a closed panel: the rail is the only place that can say so. */}
      {busy && (
        <span aria-hidden="true" className="qe-dot qe-dot--alive"
              style={{ position: "absolute", top: 8, right: 8, background: "var(--accent)" }} />
      )}
    </button>
  );
}

// v2's right column: one panel at a time, the rail on its right. Three jobs that used to share a
// single surface -- submitting work, watching the queue, and the agent that has not been designed
// yet -- now have a panel each, and the status cards that sat under the form live next door.
export default function SidePanel({ job, error, errorField, busyElsewhere, settings, project,
                                    stopping, queue, failures, models, modelsError, producers,
                                    frames, selected, onQueueLayer,
                                    onGenerate, onStop, onResume,
                                    onCancel, onClearError, onRetryAll, resumed }) {
  // Which panel is open is this column's own business: neither the project screen nor the server
  // has a reason to know it. null means none of them -- pressing the open panel's own icon closes
  // it and gives the width back to the gallery, the way a code editor's side bar behaves.
  const [open, setOpen] = useState("photo");
  const toggle = (id) => setOpen((shown) => (shown === id ? null : id));
  const current = PANELS.find((panel) => panel.id === open);
  const installing = (producers?.producers || []).some((producer) => producer.installing);

  return (
    <div style={COLUMN}>
      {/* Closed is not an empty panel but no panel: the column is not drawn at all, so its width
          goes back to the gallery. */}
      {current && (
      <div className="wf-panel" style={PANEL}>
        {/* A real heading: the open panel's name is also the only thing on screen that says which
            of the three you are looking at. */}
        <h2 style={{ margin: 0 }}>
          <Mono size={11} style={LABEL}>{current.heading || current.title}</Mono>
        </h2>
        {open === "photo" && (
          <GeneratePanel job={job} error={error} errorField={errorField}
                         busyElsewhere={busyElsewhere} settings={settings}
                         models={models} modelsError={modelsError}
                         producer={(producers?.producers || []).find((p) => p.id === "photo")}
                         onGenerate={onGenerate} onClearError={onClearError}
                         onInstall={producers?.install} />
        )}
        {/* One panel, two layers: the design asks for the same screen twice, so only the words and
            the scope rule differ (see LayerPanel). */}
        {(open === "video" || open === "audio") && (
          <LayerPanel layer={open} frames={frames} selected={selected}
                      producer={(producers?.producers || []).find((p) => p.id === open)}
                      onQueue={(files, variants) => onQueueLayer(open, files, variants)}
                      onInstall={producers?.install} />
        )}
        {open === "queue" && (
          <QueuePanel job={job} error={error} errorField={errorField}
                      busyElsewhere={busyElsewhere} project={project} stopping={stopping}
                      queue={queue} failures={failures} onStop={onStop} onResume={onResume}
                      onCancel={onCancel} onRetryAll={onRetryAll} resumed={resumed}
                      onInstall={producers?.install} />
        )}
        {open === "agent" && <AgentPanel />}
        {open === "producers" && (
          <ProducersPanel producers={producers?.producers || null}
                          error={producers?.error || null}
                          onInstall={producers?.install} onCancel={producers?.cancel} />
        )}
      </div>
      )}
      <div style={RAIL}>
        {PANELS.map((panel) => (
          <RailButton key={panel.id} panel={panel} active={panel.id === open}
                      busy={panel.id === "producers" && installing} onSelect={toggle} />
        ))}
      </div>
    </div>
  );
}
