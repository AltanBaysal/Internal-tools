import { useRef } from "react";

import Menu from "./Menu.jsx";
import { MODES, modeName } from "./modes.js";

// What the model may do at all, in the composer's foot to the left of the skill -- that question
// comes before which job it is doing, and the row reads outermost first.
//
// The skill picker's twin, with one difference that comes from what the two things are: a chat may
// have no skill and usually does not, so pressing the selected row there clears it. There is no
// such thing as no mode, so pressing it here picks it again. The button takes no --on tone for the
// same reason: that tone means something is selected, and here something always is.
//
// Whether the menu is open is not held here: one value in App owns which of the two pickers is
// open, and Escape closes whichever that is.
export default function ModePicker({ mode, open, onToggle, onChange }) {
  const trigger = useRef(null);

  return (
    <>
      <button type="button" ref={trigger} className="picker" onClick={() => onToggle?.()}>
        <span className="picker__name">{modeName(mode)}</span>
        <span className="picker__chevron">⌄</span>
      </button>
      {open ? (
        <Menu
          header="MODE"
          anchor={trigger.current}
          onClose={() => onToggle?.()}
          items={MODES.map((candidate) => ({
            label: candidate.name,
            detail: candidate.detail,
            checked: candidate.id === mode,
            onChoose: () => onChange?.(candidate.id),
          }))}
        />
      ) : null}
    </>
  );
}
