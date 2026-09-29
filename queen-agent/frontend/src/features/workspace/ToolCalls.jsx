import { useState } from "react";

// Madde 78's shape: the step's mark, the tool, and its subject in brackets. The brackets carry the
// file rather than a separator element -- a call about no file in particular really has none, and a
// mark standing where a name would have been announces something that is not there. Written as one
// string so the text reads as a whole rather than as neighbouring fragments.
function headOf(call) {
  return `⏺ ${call.tool}${call.target ? `(${call.target})` : ""}`;
}

// What the turn did before it spoke, behind one door. Above the answer, because that is the order it
// happened in.
//
// Shut, the door says which step is happening while the turn runs and how many there were once it is
// over: waiting, a reader wants to know what is going on; afterwards, what it did. Open, the handle
// stops repeating the last call -- that call is on a card right below it.
//
// A card you can press does something; a card you cannot is a record. The handle opens the list, so
// it is a button; a step that already happened opens nothing, so it is not. That is Madde 78's rule,
// and the only part of it this drops is the unspoken half -- that a record has to be faint.
export default function ToolCalls({ calls, running }) {
  // Per message and per box: the loop draws one of these for each, so a new answer is born shut and
  // a reload shuts them all. A way of looking rather than a fact about the chat, which is why it
  // reaches neither disk nor browser storage.
  const [open, setOpen] = useState(false);
  if (!calls?.length) return null;
  const summary = `⏺ ${calls.length} step${calls.length === 1 ? "" : "s"}`;
  return (
    <div className="tool-calls">
      <button
        type="button"
        className="tool-calls__handle"
        aria-expanded={open}
        onClick={() => setOpen((shown) => !shown)}
      >
        <span className="tool-calls__summary">
          {running && !open ? headOf(calls[calls.length - 1]) : summary}
        </span>
        <span className="tool-calls__chevron">{open ? "⌃" : "⌄"}</span>
      </button>
      {open
        ? calls.map((call, index) => (
            <div className="tool-call" key={`${call.tool}-${call.target}-${index}`}>
              <span className="tool-call__head">{headOf(call)}</span>
              {/* Absent on anything recorded before outcomes existed, and an empty half would
                  claim a result nobody wrote down. */}
              {call.outcome ? <span className="tool-call__outcome">{call.outcome}</span> : null}
            </div>
          ))
        : null}
    </div>
  );
}
