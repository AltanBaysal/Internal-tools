import { Hand } from "../../../components/primitives";

/** Top bar — brand + project name. Ported from EditorTopBarE. */
export default function EditorTopBar({ title }: { title?: string }) {
  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "14px 24px",
        borderBottom: "1px solid var(--border)",
        background: "var(--bg-2)",
      }}
    >
      <Hand size={24}>
        <span className="wf-hl">Queen Editor</span>
      </Hand>
      {title && (
        <Hand size={16} style={{ color: "var(--ink-2)" }}>
          · {title}
        </Hand>
      )}
      <span style={{ flex: 1 }} />
    </header>
  );
}
