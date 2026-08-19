import { useRef } from "react";

import Menu from "./Menu.jsx";
import { MODELS, modelName } from "./models.js";

// Which model this chat answers with, in the composer's foot.
//
// A model is never cleared -- there is always one answering -- so pressing the row already in use
// is not a change and asks the server for nothing. Clearing is the Skills button's rule.
//
// Whether the menu is open is not held here: Escape closes the two pickers in a fixed order and one
// closes the other, and neither is knowable from inside a single picker.
export default function ModelPicker({ model, open, onToggle, onChange }) {
  const trigger = useRef(null);

  return (
    <>
      <button type="button" ref={trigger} className="picker" onClick={() => onToggle?.()}>
        <span className="picker__name">{modelName(model)}</span>
        <span className="picker__chevron">⌄</span>
      </button>
      {open ? (
        <Menu
          header="MODEL"
          anchor={trigger.current}
          onClose={() => onToggle?.()}
          items={MODELS.map((candidate) => ({
            label: candidate.name,
            detail: candidate.detail,
            checked: candidate.id === model,
            onChoose: candidate.id === model ? undefined : () => onChange?.(candidate.id),
          }))}
        />
      ) : null}
    </>
  );
}
