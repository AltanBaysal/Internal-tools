import { useState } from "react";

import { Mono } from "../../vendor/kit.jsx";
import AgentPanel from "./AgentPanel.jsx";
import GeneratePanel from "./GeneratePanel.jsx";
import { AgentGlyph, PhotoGlyph, QueueGlyph } from "./glyphs.jsx";
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
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: 2,
  paddingTop: 12,
  boxSizing: "border-box",
};

const LABEL = { color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" };

// Which panel gets which icon. The drawings live in glyphs.jsx, because the photo one is also the
// icon its own submit button carries.
const GLYPH = { photo: PhotoGlyph, queue: QueueGlyph, agent: AgentGlyph };

// Adding a panel later means adding a row here -- the rail is drawn from this list, not from three
// hard-coded buttons. The id is the layer's own word, so it matches both the glyph's name and what
// the server calls that kind of job. `title` is what the rail's icon is called; `heading` is what
// the open panel is called, and the queue is the one place the design gives those two different
// words.
const PANELS = [
  { id: "photo", title: "Fotoğraf üret" },
  { id: "queue", title: "Kuyruğu takip et", heading: "Kuyruk" },
  { id: "agent", title: "AI agent" },
];

const BUTTON = {
  position: "relative",
  width: 40,
  height: 40,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "none",
  border: "none",
  padding: 0,
  cursor: "pointer",
};

function RailButton({ panel, active, onSelect }) {
  const Glyph = GLYPH[panel.id];
  return (
    <button type="button" aria-label={panel.title} aria-current={active ? "page" : undefined}
            onClick={() => onSelect(panel.id)}
            style={{ ...BUTTON, color: active ? "var(--accent)" : "var(--ink-3)" }}>
      <Glyph />
      {/* The design's mark for the open panel: the icon takes the accent colour and a short
          vertical line appears on its right, against the rail's outer edge. */}
      {active && (
        <span style={{ position: "absolute", right: -4, top: 8, bottom: 8, width: 2,
                       background: "var(--accent)" }} />
      )}
    </button>
  );
}

// v2's right column: one panel at a time, the rail on its right. Three jobs that used to share a
// single surface -- submitting work, watching the queue, and the agent that has not been designed
// yet -- now have a panel each, and the status cards that sat under the form live next door.
export default function SidePanel({ job, error, errorField, busyElsewhere, settings, project,
                                    stopping, queue, failures, models, modelsError,
                                    onGenerate, onStop, onResume,
                                    onCancel, onClearError, onRetryAll, resumed }) {
  // Which panel is open is this column's own business: neither the project screen nor the server
  // has a reason to know it.
  const [open, setOpen] = useState("photo");
  const current = PANELS.find((panel) => panel.id === open);

  return (
    <div style={COLUMN}>
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
                         onGenerate={onGenerate} onClearError={onClearError} />
        )}
        {open === "queue" && (
          <QueuePanel job={job} error={error} errorField={errorField}
                      busyElsewhere={busyElsewhere} project={project} stopping={stopping}
                      queue={queue} failures={failures} onStop={onStop} onResume={onResume}
                      onCancel={onCancel} onRetryAll={onRetryAll} resumed={resumed} />
        )}
        {open === "agent" && <AgentPanel />}
      </div>
      <div style={RAIL}>
        {PANELS.map((panel) => (
          <RailButton key={panel.id} panel={panel} active={panel.id === open}
                      onSelect={setOpen} />
        ))}
      </div>
    </div>
  );
}
