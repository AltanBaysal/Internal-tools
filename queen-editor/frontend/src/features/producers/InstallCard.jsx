import { Btn, Note } from "../../vendor/kit.jsx";

const CARD = { padding: "10px 12px", display: "flex", flexDirection: "column", gap: 8,
               borderColor: "var(--accent)" };

// Artboard: the same card in all three generation panels. It stands between the user and the queue
// button while the producer is missing, and takes itself away the moment it lands.
export default function InstallCard({ producer, onInstall }) {
  if (!producer || producer.installed) return null;

  return (
    <div className="wf-stroke" style={CARD}>
      <Note size={12} style={{ color: "var(--ink-2)" }}>{producer.name} kurulu değil.</Note>
      {/* Where the install really happens, once the user has pressed Kur. Same place the failed
          install used to speak from -- the user looks here for the answer either way. */}
      {producer.note && (
        <Note size={12} style={{ color: "var(--ink-3)" }}>{producer.note}</Note>
      )}
      {/* No confirm here, unlike the producers panel's own Kur: this button is the only thing
          between the user and what they already asked for. */}
      <Btn sm hl onClick={() => onInstall(producer.id)}
           style={{ justifyContent: "center" }}>Kur</Btn>
    </div>
  );
}
