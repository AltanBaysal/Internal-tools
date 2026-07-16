import { useState } from "react";

interface Props {
  nextN: number;
  selected?: boolean;
  onClick?: () => void;
}

/** Add-scene tile — identical shell to TimelineCard so it slots into the strip
    rhythm. The photo area becomes the "sahne ekle" call-to-action; `nextN` softly
    previews the position it will take (last + 1). Ported from AddSceneTile. */
export default function AddSceneTile({ nextN, selected, onClick }: Props) {
  const [hover, setHover] = useState(false);
  const accent = selected || hover;

  return (
    <button
      className="wf-card"
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        width: 160,
        flexShrink: 0,
        position: "relative",
        padding: 6,
        display: "flex",
        flexDirection: "column",
        gap: 6,
        borderColor: accent ? "var(--accent)" : "var(--border-strong)",
        borderWidth: 1,
        borderStyle: "dashed",
        background: selected ? "var(--bg-3)" : "transparent",
        boxShadow: selected ? "0 0 0 1px var(--accent)" : "none",
        cursor: "pointer",
        font: "inherit",
        color: accent ? "var(--accent)" : "var(--ink-2)",
        textAlign: "left",
        transition: "border-color .12s, background .12s, color .12s",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <span
          style={{
            fontFamily: "IBM Plex Mono, monospace",
            fontSize: 11,
            padding: "2px 6px",
            border: "1px dashed currentColor",
            borderRadius: 3,
            color: "currentColor",
            letterSpacing: ".05em",
            opacity: selected ? 0.85 : 0.55,
          }}
        >
          {String(nextN).padStart(3, "0")}
        </span>
        <span style={{ flex: 1 }} />
        <span style={{ width: 18 }} />
      </div>
      <div
        style={{
          aspectRatio: "16/10",
          width: "100%",
          border: "1px dashed currentColor",
          borderRadius: "var(--r-sm)",
          backgroundImage: "repeating-linear-gradient(-45deg, rgba(167,139,250,.04) 0 6px, transparent 6px 14px)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 6,
          color: "currentColor",
        }}
      >
        <span style={{ fontSize: 20, fontWeight: 400 }}>＋</span>
        <span style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 10 }}>sahne ekle</span>
      </div>
    </button>
  );
}
