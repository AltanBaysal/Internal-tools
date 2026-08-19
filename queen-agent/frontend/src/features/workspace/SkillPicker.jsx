import { useRef } from "react";

import Menu from "./Menu.jsx";
import { SKILLS, skillName } from "./skills.js";

// Which skill governs this chat's turns, in the composer's foot to the left of the model.
//
// Two differences from the model picker, both from what the two things are. A skill may be absent
// and that is the ordinary state, so pressing the selected row **clears** it. And a selected skill
// is worth seeing at a glance, so the button takes a warm tone -- not the accent, which marks the
// primary action and nothing else.
//
// Whether the menu is open is not held here: Escape closes the two pickers in a fixed order and one
// closes the other, and neither is knowable from inside a single picker.
export default function SkillPicker({ skill, open, onToggle, onChange }) {
  const trigger = useRef(null);

  return (
    <>
      <button
        type="button"
        ref={trigger}
        className={skill ? "picker picker--on" : "picker"}
        onClick={() => onToggle?.()}
      >
        <span className="picker__name">{skillName(skill)}</span>
        <span className="picker__chevron">⌄</span>
      </button>
      {open ? (
        <Menu
          header="SKILLS"
          anchor={trigger.current}
          onClose={() => onToggle?.()}
          items={SKILLS.map((candidate) => ({
            label: candidate.name,
            detail: candidate.detail,
            checked: candidate.id === skill,
            // The selected one clears rather than doing nothing: this is the way back to no skill.
            onChoose: () => onChange?.(candidate.id === skill ? "" : candidate.id),
          }))}
        />
      ) : null}
    </>
  );
}
