import { Btn, Icon, Mono, Note } from "../vendor/kit.jsx";

// Spec §4's "state error" card: danger border AND danger background, one plain sentence, the
// server's raw text as a bare mono line -- no nested box. Optional retry for screen-level
// failures; the panel's cards simply omit it.
export function StatusErrorCard({ text, raw, onRetry }) {
  return (
    <div className="wf-stroke"
         style={{ padding: "8px 10px", display: "flex", flexDirection: "column", gap: 6,
                  maxWidth: 640, borderColor: "var(--danger)", background: "var(--danger-bg)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--danger)" }}>
        <Icon.Warn />
        <Note size={12} style={{ color: "var(--danger)", fontWeight: 500 }}>{text}</Note>
      </div>
      {raw && (
        <Mono size={10} style={{ color: "var(--ink-3)", whiteSpace: "pre-wrap",
                                 wordBreak: "break-word" }}>{raw}</Mono>
      )}
      {onRetry && (
        <Btn sm onClick={onRetry} style={{ alignSelf: "flex-start" }}>
          <Icon.Regen /> Tekrar dene
        </Btn>
      )}
    </div>
  );
}
