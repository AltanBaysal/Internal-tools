// One body for both lists. `/` and `@` differ in where they are allowed and what they resolve to,
// but on screen they are the same thing: a list that appears while you type, narrows as you go, and
// writes its choice back into the draft. Filtering is the caller's job, so this file has no idea
// whether it is showing skills or files.
export default function MentionPicker({ prefix, items, onPick }) {
  if (items.length === 0) return null;

  return (
    <ul className="mention-picker">
      {items.map((item) => (
        <li key={item.name}>
          <button type="button" onClick={() => onPick(item.name)}>
            <span className="mention-name">
              {prefix}
              {item.name}
            </span>
            {item.description && <span className="mention-desc">{item.description}</span>}
          </button>
        </li>
      ))}
    </ul>
  );
}
