import { useState } from "react";

import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Mono } from "../../vendor/kit.jsx";

// Over the stage's middle and deaf to clicks: the player under it has to stay pressable.
const WAITING = { position: "absolute", inset: 0, display: "flex", alignItems: "center",
                  justifyContent: "center", pointerEvents: "none" };

/** One file on its way to the stage: the word while it comes, the card when it does not.
 *
 * Mounted under a key of the frame and the tab, so a step to another frame builds a new one --
 * the old picture, video and sound leave the DOM with it, and the state starts over as loading
 * with no code of its own to reset it (madde 232). The browser gives no reason for a file that
 * failed to load, so the card says which address did not come and nothing more.
 */
export default function Arriving({ url, children }) {
  const [state, setState] = useState("loading");

  if (state === "failed") return <StatusErrorCard text="Dosya yüklenemedi" raw={url} />;
  return (
    <>
      {children({ onReady: () => setState("ready"), onFail: () => setState("failed") })}
      {state === "loading" && (
        <div style={WAITING}>
          <Mono size={12} style={{ color: "var(--ink-3)" }}>yükleniyor…</Mono>
        </div>
      )}
    </>
  );
}
