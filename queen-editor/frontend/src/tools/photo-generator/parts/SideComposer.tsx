import { Btn, Icon, Segment } from "../../../components/primitives";
import type { Mode } from "../types";

interface Props {
  value: string;
  onChange: (v: string) => void;
  onGenerate: () => void;
  mode: Mode;
  onModeChange: (m: Mode) => void;
  disabled?: boolean;
}

/** Right rail composer. Roomy textarea for long prompts; mode segment sits next
    to Üret so it's one glance from the action. Ported from SideComposer. */
export default function SideComposer({ value, onChange, onGenerate, mode, onModeChange, disabled }: Props) {
  return (
    <aside
      className="wf-stroke"
      style={{
        width: 360,
        flexShrink: 0,
        padding: 14,
        display: "flex",
        flexDirection: "column",
        gap: 12,
        background: "var(--bg-2)",
        minHeight: 0,
      }}
    >
      <textarea
        className="wf-input"
        style={{ flex: 1, minHeight: 180, resize: "none" }}
        placeholder={mode === "Tekil" ? "sahnede ne oluyor + kamera açısı…" : "1. ilk sahne\n2. ikinci sahne\n…"}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      />

      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <Segment options={["Tekil", "Liste"]} value={mode} hl onChange={(m) => onModeChange(m as Mode)} />
        <span style={{ flex: 1 }} />
        <Btn primary hl disabled={disabled} onClick={onGenerate}>
          <Icon.Sparkle /> Üret
        </Btn>
      </div>
    </aside>
  );
}
