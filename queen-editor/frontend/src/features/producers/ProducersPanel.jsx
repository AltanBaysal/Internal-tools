import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Btn, Note } from "../../vendor/kit.jsx";

const ROW = { padding: "10px 12px", display: "flex", flexDirection: "column", gap: 8 };

// Artboard: one row per producer, each saying whether its model group is on this machine. No
// removing and no sizes in this version -- the design leaves both out on purpose. Nothing is
// installed from here either: Kur answers with where the install happens (FOUNDATION 9).
export default function ProducersPanel({ producers, error, onInstall }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <Note size={12} style={{ color: "var(--ink-3)" }}>
        Her üretici kendi model grubunu kurar. Kullanmadığın kurulmaz.
      </Note>

      {/* Three rows or none: two right answers and one wrong one is worse than saying nothing. */}
      {error ? (
        <StatusErrorCard text="Üretici durumu okunamadı" raw={error} />
      ) : (producers || []).map((producer) => (
        <div key={producer.id} className="wf-stroke" style={ROW}>
          <Note size={12} style={{ color: "var(--ink-2)" }}>{producer.name}</Note>
          {producer.installed ? (
            <Note size={12} style={{ color: "var(--ok)" }}>✓ kurulu</Note>
          ) : (
            <>
              {producer.note && (
                <Note size={12} style={{ color: "var(--ink-3)" }}>{producer.note}</Note>
              )}
              {/* Nothing to confirm any more: the button carries the answer rather than starting
                  a download, so a modal in front of it would only stand between the two. */}
              <Btn hl onClick={() => onInstall(producer.id)}
                   style={{ justifyContent: "center" }}>Kur</Btn>
            </>
          )}
        </div>
      ))}
    </div>
  );
}
