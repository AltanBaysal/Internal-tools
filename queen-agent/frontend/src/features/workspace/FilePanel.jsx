import { relativeTime } from "../../shared/time.js";
import CopyButton from "./CopyButton.jsx";
import Markdown from "./Markdown.jsx";

// Three parts, and only the middle one moves: the name of what is being read and the line saying
// where it came from are worth as much on page four as on page one.
function isDocument(name) {
  return /\.md$/i.test(name);
}

export default function FilePanel({ name, file, missing, error, onClose, onRefresh }) {
  return (
    <div className="reader">
      {/* Madde 342: two rows. The framed buttons stand above, the name under them on a row of its
          own, so it never gives up room to the buttons. */}
      <header className="reader__head">
        <div className="reader__bar">
          {/* Come back from rather than closed: the reader is the rail widened, and the arrow is
              the way back to the list it took over. */}
          <button type="button" className="back back--inline" onClick={onClose}>
            ←
          </button>
          <div className="reader__tools">
            {/* Madde 192. The same action the list's button asks for -- it reads both -- so the
                two are one button that follows whichever surface is on screen. No busy word and
                nothing spinning: this changes the page in place, and the changed page is the
                answer. */}
            <button type="button" className="ghost reader__refresh" onClick={onRefresh}>
              Refresh
            </button>
            {/* Madde 193. build_prompts writes to a file and does not print into the chat (Madde
                130), so the only way to get a prompt out was to select it by hand inside a
                scrolling box. What is copied is the file itself, never what the panel drew from
                it: a button per prompt would put a second reader in front of the shape
                render_module writes, and the day that reader drifts from the writer the buttons
                copy the wrong text. The panel's own copy is what goes -- reading the file again
                first would lose the press the clipboard is granted to -- and Madde 192 is what
                makes that safe: what is on screen is fresh at a turn's end and at a press of
                Refresh. */}
            <CopyButton text={file?.text ?? ""} className="reader__copy" />
          </div>
        </div>
        <span className="reader__name">{file ? file.name : name}</span>
      </header>

      {missing ? <p className="reader__note">That file is gone.</p> : null}
      {error ? <p className="reader__error">{error}</p> : null}

      {/* A document is parsed -- the same parser the answers use, at the container's own scale.
          Anything else is read as it was written: Markdown eats a JSON file's indentation and turns
          a Python comment into a heading. The decision comes off the name rather than the chip,
          whose three letters say "jso" and are not an extension. */}
      {file ? (
        <div className="reader__body">
          {isDocument(file.name) ? (
            <Markdown text={file.text} />
          ) : (
            <pre className="reader__code">{file.text}</pre>
          )}
        </div>
      ) : null}
      {file ? (
        <p className="reader__meta" data-testid="file-meta">
          {/* Not what the file measures -- when it was written. Whose file it is was here too and
              left: it read the same under every file, and the screen is full with one open. */}
          {relativeTime(file.modifiedAt)}
        </p>
      ) : null}
    </div>
  );
}
