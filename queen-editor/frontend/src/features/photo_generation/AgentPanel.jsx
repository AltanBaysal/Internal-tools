import { Note } from "../../vendor/kit.jsx";

// Artboard 06: the third icon opens a panel that is deliberately empty -- the design leaves its
// contents to a later version and says so on screen rather than hiding the icon.
export default function AgentPanel() {
  return (
    <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Note size={12} style={{ color: "var(--ink-3)" }}>Agent buradan çalışacak.</Note>
    </div>
  );
}
