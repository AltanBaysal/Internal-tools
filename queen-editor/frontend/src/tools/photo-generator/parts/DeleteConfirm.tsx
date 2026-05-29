import { Btn, Hand, Icon, Mono, Note } from "../../../components/primitives";

/** Compact danger dialog over a blurred editor. Shows only the scene number
    (prompts can be long). Ported from ArtboardE_DeleteConfirm's modal. */
export default function DeleteConfirm({ n, onCancel, onConfirm }: { n: number; onCancel: () => void; onConfirm: () => void }) {
  const seq = String(n).padStart(3, "0");
  return (
    <div className="wf-scrim">
      <div
        className="wf-card"
        style={{
          width: 460,
          padding: 20,
          display: "flex",
          flexDirection: "column",
          gap: 14,
          background: "var(--bg-2)",
          borderColor: "var(--danger)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span
            style={{
              padding: "2px 6px",
              border: "1px solid var(--danger)",
              borderRadius: 3,
              color: "var(--danger)",
              fontFamily: "IBM Plex Mono, monospace",
              fontSize: 11,
              fontWeight: 500,
              letterSpacing: ".05em",
            }}
          >
            {seq}
          </span>
          <Hand size={20}>Sahneyi sil?</Hand>
        </div>

        <Note size={13} style={{ color: "var(--ink-2)" }}>
          <Mono size={12} style={{ color: "var(--ink)" }}>
            {seq}
          </Mono>{" "}
          numaralı sahne silinecek. Emin misin?
        </Note>

        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <Btn onClick={onCancel}>Vazgeç</Btn>
          <span style={{ flex: 1 }} />
          <Btn style={{ background: "var(--danger)", color: "var(--bg)", borderColor: "var(--danger)" }} onClick={onConfirm}>
            <Icon.Trash /> Sil
          </Btn>
        </div>
      </div>
    </div>
  );
}
