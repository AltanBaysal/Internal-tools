import { useState } from "react";

import { Mono } from "../../vendor/kit.jsx";
import AgentPanel from "./AgentPanel.jsx";
import GeneratePanel from "./GeneratePanel.jsx";
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

// Ours, not the design's: the design gives the rail its width, its behaviour and the three panel
// names, but not the glyphs. Drawn in the kit's own language -- 14x14 box, currentColor, 1.5
// rounded stroke -- and kept here rather than in vendor/, which is a verbatim copy.
const GLYPH = {
  add: () => (
    <svg width="16" height="16" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M7 2v10M2 7h10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  ),
  queue: () => (
    <svg width="16" height="16" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M2 4h10M2 7h10M2 10h6" stroke="currentColor" strokeWidth="1.5"
            strokeLinecap="round" />
    </svg>
  ),
  agent: () => (
    <svg width="16" height="16" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M2 4.5A1.5 1.5 0 0 1 3.5 3h7A1.5 1.5 0 0 1 12 4.5v4A1.5 1.5 0 0 1 10.5 10H6l-3 2V10
               A1 1 0 0 1 2 9V4.5z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
    </svg>
  ),
};

// Adding a panel later means adding a row here -- the rail is drawn from this list, not from three
// hard-coded buttons.
const PANELS = [
  { id: "add", title: "Üretime ekle" },
  { id: "queue", title: "Kuyruğu takip et" },
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
                                    stopping, pending, failures, models, modelsError,
                                    onGenerate, onStop, onResume,
                                    onCancel, onClearError, onShowFailures }) {
  // Which panel is open is this column's own business: neither the project screen nor the server
  // has a reason to know it.
  const [open, setOpen] = useState("add");
  const current = PANELS.find((panel) => panel.id === open);

  return (
    <div style={COLUMN}>
      <div className="wf-panel" style={PANEL}>
        {/* A real heading: the open panel's name is also the only thing on screen that says which
            of the three you are looking at. */}
        <h2 style={{ margin: 0 }}><Mono size={11} style={LABEL}>{current.title}</Mono></h2>
        {open === "add" && (
          <GeneratePanel job={job} error={error} errorField={errorField}
                         busyElsewhere={busyElsewhere} settings={settings}
                         models={models} modelsError={modelsError}
                         onGenerate={onGenerate} onClearError={onClearError} />
        )}
        {open === "queue" && (
          <QueuePanel job={job} error={error} errorField={errorField}
                      busyElsewhere={busyElsewhere} project={project} stopping={stopping}
                      pending={pending} failures={failures} onStop={onStop} onResume={onResume}
                      onCancel={onCancel} onShowFailures={onShowFailures} />
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
