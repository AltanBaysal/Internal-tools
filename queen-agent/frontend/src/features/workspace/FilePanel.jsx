import { useEffect, useRef, useState } from "react";

import { relativeTime } from "../../shared/time.js";
import Markdown from "./Markdown.jsx";

// Long enough to be read without looking away, short enough that the button is a button again
// before it is next needed.
const SAID_MS = 2500;

// Madde 193. build_prompts writes to a file and does not print into the chat (Madde 130), so the
// only way to get a prompt out was to select it by hand inside a scrolling box. What is copied is
// the file itself, never what the panel drew from it: a button per prompt would put a second reader
// in front of the shape render_module writes, and the day that reader drifts from the writer the
// buttons copy the wrong text.
//
// Its own component because it has its own state -- what it last said, and the timer that takes
// that back. Download's waiting is a different waiting and shares nothing with it.
//
// The precedent is queen-editor's RawOutput and PhotoDetail; the two tools share no code, so what
// travels is the reasoning.
function CopyButton({ text }) {
  const [said, setSaid] = useState(null);
  const fade = useRef(null);

  useEffect(() => () => clearTimeout(fade.current), []);

  const copy = () => {
    clearTimeout(fade.current);
    // Written straight from the press rather than a microtask after it: the clipboard is granted to
    // a user gesture, and a browser may refuse a write that arrives even a tick late. This is why
    // the panel's own copy is what goes -- Download can read again, and this cannot. Madde 192 is
    // what makes that safe: what is on screen is fresh at a turn's end and at a press of Refresh.
    //
    // The try is for the other half: with no clipboard object at all the call throws where it
    // stands, while a refused permission rejects instead, and the user needs the same answer either
    // way.
    let landing;
    try {
      landing = navigator.clipboard.writeText(text);
    } catch (absent) {
      landing = Promise.reject(absent);
    }
    Promise.resolve(landing)
      .then(() => setSaid("Copied"))
      .catch(() => setSaid("Could not copy"))
      .finally(() => {
        fade.current = setTimeout(() => setSaid(null), SAID_MS);
      });
  };

  return (
    // The answer is the icon's own name and colour: a word appearing beside the heading would push
    // the body under it down, which is the page moving while it is being read. Dimmed rather than
    // gone while there is nothing to copy -- an icon that came and went as the file loaded would
    // make the header twitch, and a button that copies nothing and says it did is the other half
    // of the same lie.
    <button
      type="button"
      className="reader__copy"
      disabled={!text}
      aria-label={said ?? "Copy"}
      title={said ?? "Copy"}
      data-said={said === "Copied" ? "yes" : said ? "no" : undefined}
      onClick={copy}
    >
      ⧉
    </button>
  );
}

// Three parts, and only the middle one moves: the name of what is being read and the line saying
// where it came from are worth as much on page four as on page one.
//
// `back` is what the two callers differ by. The rail's panel is the rail widened, so it is come back
// from; the project screen's panel is a surface standing beside the grid, so it closes. One
// component either way -- splitting it would copy the header, the Download and its waiting state.
function isDocument(name) {
  return /\.md$/i.test(name);
}

export default function FilePanel({
  name,
  file,
  missing,
  error,
  back,
  onClose,
  onDownload,
  onRefresh,
}) {
  const [preparing, setPreparing] = useState(false);
  const [failed, setFailed] = useState(null);

  const download = async () => {
    setPreparing(true);
    setFailed(null);
    try {
      await onDownload?.();
    } catch (failure) {
      setFailed(failure.message);
    } finally {
      setPreparing(false);
    }
  };

  return (
    <div className="reader">
      <header className="reader__head">
        {back ? (
          <button type="button" className="back back--inline" onClick={onClose}>
            ←
          </button>
        ) : null}
        <span className="reader__name">{file ? file.name : name}</span>
        {/* Madde 192. The same action the list's button asks for -- it reads both -- so the two are
            one button that follows whichever surface is on screen. No busy word and nothing
            spinning: Download says "preparing…" because what it makes lands outside the screen,
            and this changes the page in place. The changed page is the answer. */}
        <button
          type="button"
          className="reader__refresh"
          title="Refresh"
          aria-label="Refresh"
          onClick={onRefresh}
        >
          ↻
        </button>
        {/* Refresh, copy, download: the same file, lightest first. */}
        <CopyButton text={file?.text ?? ""} />
        {/* The width is fixed so the label can change inside it without moving the button. */}
        <button
          type="button"
          className="ghost reader__download"
          onClick={download}
          disabled={preparing}
        >
          {preparing ? "preparing…" : "Download"}
        </button>
        {back ? null : (
          <button type="button" className="reader__close" title="Close" onClick={onClose}>
            ×
          </button>
        )}
      </header>

      {missing ? <p className="reader__note">That file is gone.</p> : null}
      {error ? <p className="reader__error">{error}</p> : null}
      {failed ? <p className="reader__error">{failed}</p> : null}

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
