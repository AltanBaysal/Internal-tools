// Shared wireframe primitives — ported from the design handoff (wireframe-kit.jsx),
// typed for TS. Visuals are 1:1 with the prototype; Segment gains an onChange so the
// real app can toggle it (the prototype rendered it read-only).
import type { CSSProperties, ReactNode, ButtonHTMLAttributes } from "react";

type WithStyle = { style?: CSSProperties };

export const Hand = ({ children, size = 24, style, ...rest }: { children: ReactNode; size?: number } & WithStyle) => (
  <span className="wf-hand" style={{ fontSize: size, lineHeight: 1.1, ...style }} {...rest}>
    {children}
  </span>
);

export const Note = ({ children, size = 16, style, ...rest }: { children: ReactNode; size?: number } & WithStyle) => (
  <span className="wf-note" style={{ fontSize: size, lineHeight: 1.3, ...style }} {...rest}>
    {children}
  </span>
);

export const Mono = ({ children, size = 12, style, ...rest }: { children: ReactNode; size?: number } & WithStyle) => (
  <span className="wf-mono" style={{ fontSize: size, ...style }} {...rest}>
    {children}
  </span>
);

interface BtnProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  primary?: boolean;
  hl?: boolean;
  sm?: boolean;
  ghost?: boolean;
  icon?: boolean;
}
export const Btn = ({ children, primary, hl, sm, ghost, icon, className, ...rest }: BtnProps) => (
  <button
    className={[
      "wf-btn",
      primary && "wf-btn--primary",
      hl && "wf-btn--hl",
      sm && "wf-btn--sm",
      ghost && "wf-btn--ghost",
      icon && "wf-btn--icon",
      className,
    ]
      .filter(Boolean)
      .join(" ")}
    {...rest}
  >
    {children}
  </button>
);

export const Seq = ({ n, hl, big, xl, style }: { n: number; hl?: boolean; big?: boolean; xl?: boolean } & WithStyle) => (
  <span
    className={["wf-seq", hl && "wf-seq--hl", big && "wf-seq--big", xl && "wf-seq--xl"].filter(Boolean).join(" ")}
    style={style}
  >
    {String(n).padStart(3, "0")}
  </span>
);

export const Grip = ({ style }: WithStyle) => (
  <span className="wf-grip" style={style}>
    <i />
    <i />
    <i />
    <i />
    <i />
    <i />
  </span>
);

export const Segment = ({
  options,
  value,
  hl,
  onChange,
}: {
  options: string[];
  value: string;
  hl?: boolean;
  onChange?: (option: string) => void;
}) => (
  <div className={"wf-segment" + (hl ? " wf-segment--hl" : "")}>
    {options.map((o) => (
      <button key={o} className={o === value ? "is-on" : ""} onClick={() => onChange?.(o)} type="button">
        {o}
      </button>
    ))}
  </div>
);

// Diagonal-striped image placeholder; `loading` swaps in the circular spinner.
export const ImgPH = ({
  label = "photo",
  loading,
  style,
  children,
}: {
  label?: string;
  loading?: boolean;
  children?: ReactNode;
} & WithStyle) => (
  <div className={"wf-img" + (loading ? " wf-img--loading" : "")} style={style}>
    {!loading && <span className="wf-img-x" aria-hidden />}
    {loading ? (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 10,
          position: "relative",
          zIndex: 1,
        }}
      >
        <span className="wf-spinner" />
        <Mono size={12} style={{ color: "var(--ink-2)" }}>
          Çalışıyor
        </Mono>
      </div>
    ) : (
      children || <span className="wf-img-label">{label}</span>
    )}
  </div>
);

export const Status = ({ children, hl, err, dot, style }: { children: ReactNode; hl?: boolean; err?: boolean; dot?: boolean } & WithStyle) => (
  <span className={"wf-status" + (hl ? " wf-status--hl" : "") + (err ? " wf-status--err" : "")} style={style}>
    {dot && <span className="dot" />}
    {children}
  </span>
);

// Tiny icon glyphs — drawn with SVG, intentionally simple. 1:1 with the handoff.
export const Icon = {
  Trash: () => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <path d="M3 4h8M5 4V2.5h4V4M4.5 4l.5 7.5a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1L9.5 4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  Left: () => (
    <svg width="12" height="12" viewBox="0 0 14 14" fill="none">
      <path d="M9 3L5 7l4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  Right: () => (
    <svg width="12" height="12" viewBox="0 0 14 14" fill="none">
      <path d="M5 3l4 4-4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  Sparkle: () => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <path d="M7 1.5l1.2 3.3L11.5 6 8.2 7.2 7 10.5 5.8 7.2 2.5 6l3.3-1.2L7 1.5z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
    </svg>
  ),
  Pencil: () => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <path d="M2 12l1-3 6.5-6.5a1.5 1.5 0 0 1 2 2L5 11l-3 1z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
    </svg>
  ),
};
