import { useState } from "react";

// A data: URL rather than a Blob and an object URL: the browser needs no script to save this, the
// anchor does it on its own, and a test can read the content back out of the href.
function downloadHref(content) {
  return `data:text/markdown;charset=utf-8,${encodeURIComponent(content)}`;
}

export default function FileView({ file, onChange, onClose }) {
  const [label, setLabel] = useState("Kopyala");

  async function copy() {
    try {
      await navigator.clipboard.writeText(file.content);
      setLabel("Kopyalandı");
    } catch (err) {
      // Clipboard access needs a secure context. http://localhost is one, so this should not fire
      // in normal use; if it does, the browser's own reason is more useful than a guess.
      setLabel(`Kopyalanamadı: ${err.message}`);
    }
    setTimeout(() => setLabel("Kopyala"), 1500);
  }

  return (
    <aside className="file-view">
      <header>
        <span className="file-name">{file.name}</span>
        <a href={downloadHref(file.content)} download={file.name}>
          İndir
        </a>
        <button type="button" onClick={copy}>
          {label}
        </button>
        <button type="button" aria-label="Dosyayı kapat" onClick={onClose}>
          ×
        </button>
      </header>
      {/* Raw text, never rendered markdown: rendering means a markdown library, and this app has no
          dependencies to spend. You see what you wrote. */}
      <textarea value={file.content} onChange={(e) => onChange(e.target.value)} />
    </aside>
  );
}
