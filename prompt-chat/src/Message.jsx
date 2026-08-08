import { useState } from "react";

const ROLE_LABEL = { user: "Sen", assistant: "Grok", error: "Hata" };

export default function Message({ role, content, skill }) {
  const [label, setLabel] = useState("Kopyala");

  async function copy() {
    try {
      await navigator.clipboard.writeText(content);
      setLabel("Kopyalandı");
    } catch (err) {
      // Clipboard access needs a secure context. http://localhost is one, so this should not fire
      // in normal use; if it does, the browser's own reason is more useful than a guess.
      setLabel(`Kopyalanamadı: ${err.message}`);
    }
    setTimeout(() => setLabel("Kopyala"), 1500);
  }

  return (
    <div className={`msg ${role}`}>
      <div className="role">{ROLE_LABEL[role]}</div>
      {/* The instruction itself is folded in on the way out, so the screen shows only its name:
          three thousand words of skill text would bury the sentence the user actually wrote. */}
      {skill && <div className="skill-tag">/{skill}</div>}
      {/* A JSX child, never dangerouslySetInnerHTML: the reply is text to be copied, not markup. */}
      <div className="body">{content}</div>
      {role === "assistant" && (
        <button className="copy" onClick={copy}>
          {label}
        </button>
      )}
    </div>
  );
}
