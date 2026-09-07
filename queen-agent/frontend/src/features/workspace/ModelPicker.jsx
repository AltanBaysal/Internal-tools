import { useRef } from "react";

import Menu from "./Menu.jsx";
import { DEFAULT_MODEL, MODELS, modelName } from "./models.js";

// Which model answers this chat's turns, at the right end of the composer's foot. It was a plain
// label between Madde 82 and 146 -- one model, so a control would have opened nothing.
//
// Two differences from the skill picker, both from what the two things are. There is no way back to
// no model, so pressing the selected row keeps it rather than clearing. And the button takes no
// warm tone: `picker--on` marks that a selection EXISTS, and one always does here.
//
// Whether the menu is open is not held here: Escape closes the pickers in a fixed order and one
// closes the other, and neither is knowable from inside a single picker.
export default function ModelPicker({ model, open, onToggle, onChange }) {
  const trigger = useRef(null);
  // The mark and the button say the same thing, which is the whole of this line. Nothing selected
  // reads as the default on the face of the button, so the default is marked; an id no row carries
  // -- one of Madde 72's five, or the model Madde 177 took out of the menu -- says itself on the
  // button, so nothing is marked. Resolved to the default it would tick a row this chat was never
  // answered by.
  const selected = model || DEFAULT_MODEL;

  return (
    <>
      <button type="button" ref={trigger} className="picker" onClick={() => onToggle?.()}>
        <span className="picker__name">{modelName(model)}</span>
        <span className="picker__chevron">⌄</span>
      </button>
      {open ? (
        <Menu
          header="MODELS"
          anchor={trigger.current}
          onClose={() => onToggle?.()}
          items={MODELS.map((candidate) => ({
            label: candidate.name,
            detail: candidate.detail,
            checked: candidate.id === selected,
            onChoose: () => onChange?.(candidate.id),
          }))}
        />
      ) : null}
    </>
  );
}
