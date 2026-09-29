const CHIP_LENGTH = 3;

// A message remembers names, not rows, so the chip's letters are read off the name here -- the same
// three the server puts on a listed file.
function extensionOf(name) {
  const dot = name.lastIndexOf(".");
  return name.slice(dot + 1, dot + 1 + CHIP_LENGTH).toLowerCase();
}

// The skeleton of the card about to be born: an empty badge slot where the chip will go, and no
// name -- the model's wish is not the name until it has been cleaned and a clash resolved.
export function CreatingFile() {
  return (
    <div className="creating">
      <span className="creating__chip" />
      <span>creating file…</span>
    </div>
  );
}

// The primary way into a file: the card is a door rather than a receipt. Which one is open is the
// caller's answer, and telling someone to open what is already open would be the wrong sentence --
// so the hint drops to "open" and the arrow, having nowhere to point, drops with it.
export default function FileCard({ name, selected, onOpen }) {
  return (
    <button
      type="button"
      className={selected ? "file-card file-card--selected" : "file-card"}
      onClick={() => onOpen?.(name)}
    >
      <span className="file-chip">{extensionOf(name)}</span>
      <span className="file-card__name">{name}</span>
      <span className="file-card__saved">✓ saved to project</span>
      <span className="file-card__hint">{selected ? "open" : "Open ›"}</span>
    </button>
  );
}
