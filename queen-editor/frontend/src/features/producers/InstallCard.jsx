import { Btn, Note } from "../../vendor/kit.jsx";

const CARD = { padding: "10px 12px", display: "flex", flexDirection: "column", gap: 8,
               borderColor: "var(--accent)" };

/** What a running install is doing, in words. No bar: a group's files each restart the count and
 *  a total is often never announced, so the drawn one moved without saying anything. The file
 *  name is what the server really knows. */
export function Running({ file }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <span aria-hidden="true" className="qe-dot qe-dot--alive"
            style={{ background: "var(--accent)" }} />
      <Note size={12} style={{ color: "var(--ink-2)" }}>
        {file ? `kuruluyor… ${file}` : "kuruluyor…"}
      </Note>
    </div>
  );
}

// Artboard: the same card in all three generation panels. It stands between the user and the queue
// button while the producer is missing, and takes itself away the moment it lands.
export default function InstallCard({ producer, onInstall }) {
  if (!producer || producer.installed) return null;

  return (
    <div className="wf-stroke" style={CARD}>
      {producer.installing ? (
        <Running file={producer.installing.file} />
      ) : (
        <>
          <Note size={12} style={{ color: "var(--ink-2)" }}>{producer.name} kurulu değil.</Note>
          {/* The last attempt's own sentence, with nothing of ours wrapped around it -- an install
              that failed silently is what sent the user back to press Kur again. */}
          {producer.error && (
            <Note size={12} style={{ color: "var(--danger)" }}>{producer.error}</Note>
          )}
          {/* No confirm here, unlike the producers panel's own Kur: this button is the only thing
              between the user and what they already asked for. */}
          <Btn sm hl onClick={() => onInstall(producer.id)}
               style={{ justifyContent: "center" }}>Kur</Btn>
        </>
      )}
    </div>
  );
}
