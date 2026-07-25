import { useEffect, useState } from "react";
import { getHealth } from "./shared/api.js";

// Part 2 is a connection proof: on load, call the server and show the result.
const LABEL = {
  checking: "kontrol ediliyor…",
  ok: "sunucuya bağlı ✓",
  error: "sunucuya bağlanılamadı ✗",
};

export default function App() {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    getHealth()
      .then(() => setStatus("ok"))
      .catch(() => setStatus("error"));
  }, []);

  const cls =
    "wf-status" +
    (status === "ok" ? " wf-status--hl" : status === "error" ? " wf-status--err" : "");

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 16,
      }}
    >
      <span className="wf-hand" style={{ fontSize: 28 }}>
        <span className="wf-hl">Queen Editor</span>
      </span>
      <span className={cls}>
        {status === "checking" && <span className="dot" />}
        {LABEL[status]}
      </span>
    </div>
  );
}
