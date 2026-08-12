import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Btn, Note } from "../../vendor/kit.jsx";

const ROW = { padding: "10px 12px", display: "flex", flexDirection: "column", gap: 8 };

// Artboard: one row per producer, each saying whether its model group is on this machine. No
// removing and no sizes in this version -- the design leaves both out on purpose.
export default function ProducersPanel({ producers, error }) {
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
            // Held until Görev 12 gives it something to do: a button that answers a press with
            // nothing at all would be worse than one that says it is not ready.
            <Btn hl disabled style={{ justifyContent: "center" }}>Kur</Btn>
          )}
        </div>
      ))}
    </div>
  );
}
