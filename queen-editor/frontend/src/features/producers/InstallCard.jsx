import { Btn, Note } from "../../vendor/kit.jsx";

const CARD = { padding: "10px 12px", display: "flex", flexDirection: "column", gap: 8,
               borderColor: "var(--accent)" };
const TRACK = { height: 4, borderRadius: 2, background: "var(--bg-3)", overflow: "hidden" };

/** How far the download has got. An unknown total draws a full faint track rather than a made-up
 *  percentage: the server did not say, and guessing would be the one thing a bar must not do. */
function Bar({ done, total }) {
  const known = typeof total === "number" && total > 0;
  return (
    <div style={TRACK}>
      <div style={{ height: "100%", background: "var(--accent)",
                    width: known ? `${Math.min(100, (done / total) * 100)}%` : "100%",
                    opacity: known ? 1 : 0.35 }} />
    </div>
  );
}

// Artboard: the same card in all three generation panels. It stands between the user and the queue
// button while the producer is missing, and takes itself away the moment it lands.
export default function InstallCard({ producer, onInstall }) {
  if (!producer || producer.installed) return null;
  const installing = producer.installing;

  return (
    <div className="wf-stroke" style={CARD}>
      {installing ? (
        <>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span aria-hidden="true" className="qe-dot qe-dot--alive"
                  style={{ background: "var(--accent)" }} />
            <Note size={12} style={{ color: "var(--ink-2)" }}>
              kuruluyor… bitince bu kart kaybolur
            </Note>
          </div>
          <Bar done={installing.done} total={installing.total} />
        </>
      ) : (
        <>
          <Note size={12} style={{ color: "var(--ink-2)" }}>{producer.name} kurulu değil.</Note>
          {/* No confirm here, unlike the producers panel's own Kur: this button is the only thing
              between the user and what they already asked for. */}
          <Btn sm hl onClick={() => onInstall(producer.id)}
               style={{ justifyContent: "center" }}>Kur</Btn>
        </>
      )}
    </div>
  );
}

export { Bar };
