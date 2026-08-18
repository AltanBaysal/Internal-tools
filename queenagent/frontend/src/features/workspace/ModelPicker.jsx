import { useRef, useState } from "react";

import Menu from "./Menu.jsx";
import { MODELS, modelName } from "./models.js";

// Which model this chat answers with, in the composer's foot. Open state is the button's own: it is
// gone the moment a row is pressed and nothing outside needs to know it was ever there.
//
// A model is never cleared -- there is always one answering -- so pressing the row already in use
// is not a change and asks the server for nothing. Clearing is the Skills button's rule.
export default function ModelPicker({ model, onChange }) {
  const [open, setOpen] = useState(false);
  const trigger = useRef(null);

  return (
    <>
      <button
        type="button"
        ref={trigger}
        className="picker"
        onClick={() => setOpen((was) => !was)}
      >
        <span className="picker__name">{modelName(model)}</span>
        <span className="picker__chevron">⌄</span>
      </button>
      {open ? (
        <Menu
          header="MODEL"
          anchor={trigger.current}
          onClose={() => setOpen(false)}
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
