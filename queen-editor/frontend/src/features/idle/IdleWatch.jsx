import { Btn, Note } from "../../vendor/kit.jsx";
import { IDLE_SENTENCE, useIdleWatch } from "./useIdleWatch.js";

// "Orada mısın?" over whichever screen is open (madde 498). App draws one beside the routed screen,
// so its one held ask survives moving between screens. One button and no other way out: neither
// Escape nor a click outside closes it, since what it asks is whether anybody is there to press.
export default function IdleWatch() {
  const { asking, here } = useIdleWatch();
  if (!asking) return null;
  return (
    <div className="wf-scrim">
      <div className="wf-card wf-card--shadow" role="dialog" aria-label="Orada mısın?"
           style={{ width: 340, padding: 18, display: "flex", flexDirection: "column", gap: 10 }}>
        <Note size={14}>Orada mısın?</Note>
        <Note size={12} style={{ color: "var(--ink-2)" }}>{IDLE_SENTENCE}</Note>
        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 4 }}>
          <Btn sm hl autoFocus onClick={here}>Buradayım</Btn>
        </div>
      </div>
    </div>
  );
}
