// Shared wireframe primitives for Queen Editor wireframes
// All components are presentational — no real state mutation.

const Hand = ({ children, size = 24, style, ...rest }) => (
  <span className="wf-hand" style={{ fontSize: size, lineHeight: 1.1, ...style }} {...rest}>{children}</span>
);

const Note = ({ children, size = 16, style, ...rest }) => (
  <span className="wf-note" style={{ fontSize: size, lineHeight: 1.3, ...style }} {...rest}>{children}</span>
);

const Mono = ({ children, size = 12, style, ...rest }) => (
  <span className="wf-mono" style={{ fontSize: size, ...style }} {...rest}>{children}</span>
);

const HL = ({ children }) => <span className="wf-hl">{children}</span>;

const Btn = ({ children, primary, hl, sm, ghost, style, icon, ...rest }) => (
  <button
    className={[
      "wf-btn",
      primary && "wf-btn--primary",
      hl && "wf-btn--hl",
      sm && "wf-btn--sm",
      ghost && "wf-btn--ghost",
      icon && "wf-btn--icon",
    ].filter(Boolean).join(" ")}
    style={style}
    {...rest}
  >{children}</button>
);

const Seq = ({ n, hl, big, xl, style }) => (
  <span
    className={[
      "wf-seq",
      hl && "wf-seq--hl",
      big && "wf-seq--big",
      xl && "wf-seq--xl",
    ].filter(Boolean).join(" ")}
    style={style}
  >{String(n).padStart(3, "0")}</span>
);

const Grip = ({ style }) => (
  <span className="wf-grip" style={style}>
    <i /><i /><i /><i /><i /><i />
  </span>
);

const Segment = ({ options, value, hl }) => (
  <div className={"wf-segment" + (hl ? " wf-segment--hl" : "")}>
    {options.map((o) => (
      <button key={o} className={o === value ? "is-on" : ""}>{o}</button>
    ))}
  </div>
);

// Diagonal-striped image placeholder
const ImgPH = ({ label = "photo", loading, style, children }) => (
  <div
    className={"wf-img" + (loading ? " wf-img--loading" : "")}
    style={style}
  >
    {!loading && <span className="wf-img-x" aria-hidden />}
    {loading
      ? (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10, position: "relative", zIndex: 1 }}>
          <span className="wf-spinner" />
          <Mono size={12} style={{ color: "var(--ink-2)" }}>Çalışıyor</Mono>
        </div>
      )
      : (children || <span className="wf-img-label">{label}</span>)
    }
  </div>
);

const Status = ({ children, hl, err, dot, style }) => (
  <span
    className={"wf-status" + (hl ? " wf-status--hl" : "") + (err ? " wf-status--err" : "")}
    style={style}
  >
    {dot && <span className="dot" />}
    {children}
  </span>
);

const Pill = ({ children, hl, err, style }) => (
  <span
    className={"wf-pill" + (hl ? " wf-pill--hl" : "") + (err ? " wf-pill--err" : "")}
    style={style}
  >{children}</span>
);

// Tiny icon glyphs — drawn with text/SVG, intentionally simple
const Icon = {
  Regen: () => <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M2 7a5 5 0 0 1 8.5-3.5L12 5M12 7a5 5 0 0 1-8.5 3.5L2 9" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/><path d="M9 5h3V2M5 9H2v3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  Pencil: () => <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M2 12l1-3 6.5-6.5a1.5 1.5 0 0 1 2 2L5 11l-3 1z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/></svg>,
  Trash: () => <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M3 4h8M5 4V2.5h4V4M4.5 4l.5 7.5a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1L9.5 4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  Up: () => <svg width="12" height="12" viewBox="0 0 14 14" fill="none"><path d="M3 9l4-4 4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  Down: () => <svg width="12" height="12" viewBox="0 0 14 14" fill="none"><path d="M3 5l4 4 4-4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  Left: () => <svg width="12" height="12" viewBox="0 0 14 14" fill="none"><path d="M9 3L5 7l4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  Right: () => <svg width="12" height="12" viewBox="0 0 14 14" fill="none"><path d="M5 3l4 4-4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  Plus: () => <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M7 2v10M2 7h10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/></svg>,
  Sparkle: () => <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M7 1.5l1.2 3.3L11.5 6 8.2 7.2 7 10.5 5.8 7.2 2.5 6l3.3-1.2L7 1.5z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/></svg>,
  Warn: () => <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M7 2l5.5 9.5h-11L7 2z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/><path d="M7 6v2.5M7 10.2v.1" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/></svg>,
};

// Annotation arrow (uses inline SVG)
const Arrow = ({ from, to, color = "var(--ink)", curve = 0.3 }) => {
  const [x1, y1] = from, [x2, y2] = to;
  const dx = x2 - x1, dy = y2 - y1;
  const cx = (x1 + x2) / 2 + dy * curve;
  const cy = (y1 + y2) / 2 - dx * curve;
  return (
    <svg style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none", overflow: "visible" }}>
      <path d={`M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`} stroke={color} strokeWidth="1.5" fill="none" strokeDasharray="4 3" />
      {/* arrowhead */}
      <path d={`M ${x2} ${y2} l -8 -3 m 8 3 l -6 5`} stroke={color} strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

// Adapted for ESM -- the ONLY change from the design copy; component bodies are verbatim.
export { Hand, Note, Mono, HL, Btn, Seq, Grip, Segment, ImgPH, Status, Pill, Icon, Arrow };
