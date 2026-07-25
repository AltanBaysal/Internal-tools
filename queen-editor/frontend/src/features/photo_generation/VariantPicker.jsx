import { Mono } from "../../vendor/kit.jsx";

const OPTIONS = [1, 2, 3, 4];

// The design's segmented control is a wireframe (its buttons have no onClick), so this is our own
// component wearing its CSS. Changing the offered range is a one-line change here.
export default function VariantPicker({ value, onChange }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <Mono size={11} style={{ color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" }}>
        Varyant
      </Mono>
      <div className="wf-segment">
        {OPTIONS.map((option) => (
          <button
            key={option}
            className={option === value ? "is-on" : ""}
            onClick={() => onChange(option)}
          >{option}</button>
        ))}
      </div>
    </div>
  );
}
