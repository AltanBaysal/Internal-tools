import { useState } from "react";

import ConfirmModal from "../../shared/ConfirmModal.jsx";
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Btn, Note } from "../../vendor/kit.jsx";
import { Bar } from "./InstallCard.jsx";

const ROW = { padding: "10px 12px", display: "flex", flexDirection: "column", gap: 8 };

// Artboard: one row per producer, each saying whether its model group is on this machine. No
// removing and no sizes in this version -- the design leaves both out on purpose.
export default function ProducersPanel({ producers, error, onInstall, onCancel }) {
  // Which producer the user is being asked about, and what they were asked.
  const [asking, setAsking] = useState(null);

  function confirm() {
    const { producer, kind } = asking;
    setAsking(null);
    if (kind === "install") onInstall(producer.id);
    else onCancel(producer.id);
  }

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
          {producer.installing ? (
            <>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span aria-hidden="true" className="qe-dot qe-dot--alive"
                      style={{ background: "var(--accent)" }} />
                <Note size={12} style={{ color: "var(--ink-2)" }}>
                  kuruluyor… bitince bu kart kaybolur
                </Note>
              </div>
              <Bar done={producer.installing.done} total={producer.installing.total} />
              <Btn sm ghost onClick={() => setAsking({ producer, kind: "cancel" })}
                   style={{ alignSelf: "flex-start", color: "var(--danger)" }}>İptal</Btn>
            </>
          ) : producer.installed ? (
            <Note size={12} style={{ color: "var(--ok)" }}>✓ kurulu</Note>
          ) : (
            // Unlike the card inside a generation panel, this one asks first: the user came here to
            // do maintenance, and how long it may take is worth saying before it starts.
            <Btn hl onClick={() => setAsking({ producer, kind: "install" })}
                 style={{ justifyContent: "center" }}>Kur</Btn>
          )}
        </div>
      ))}

      {asking && (asking.kind === "install" ? (
        <ConfirmModal
          title={`${asking.producer.name} kurulsun mu?`}
          body="Kurulum uzun sürebilir. Üretimi engellemez, arkada sürer."
          confirmLabel="Kur"
          width={360}
          onCancel={() => setAsking(null)}
          onConfirm={confirm}
        />
      ) : (
        <ConfirmModal
          title="Kurulum iptal edilsin mi?"
          body={"İnen kısım atılır, sonra baştan kurmak gerekir. Kuyruktaki video işleri atılmaz — "
                + "kurulum yapılana kadar beklemede kalır."}
          confirmLabel="İptal et"
          width={360}
          danger
          onCancel={() => setAsking(null)}
          onConfirm={confirm}
        />
      ))}
    </div>
  );
}
