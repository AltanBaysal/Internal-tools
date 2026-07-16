import { useState } from "react";
import { Grip, Icon, ImgPH, Seq } from "../../../components/primitives";

interface Props {
  n: number;
  selected?: boolean;
  loading?: boolean;
  dim?: boolean;
  isDragging?: boolean;
  onClick?: () => void;
  // number-edit reorder
  onRenumber?: (newN: number) => void;
  // drag-drop reorder (handlers bound to this card's index by the parent)
  onDragStart?: () => void;
  onDragEnter?: () => void;
  onDrop?: () => void;
  onDragEnd?: () => void;
}

/** One scene thumbnail in the bottom strip (160px). Draggable for reorder; the
    sequence number is click-to-edit (type a new position). Ported from TimelineCard. */
export default function TimelineCard({ n, selected, loading, dim, isDragging, onClick, onRenumber, onDragStart, onDragEnter, onDrop, onDragEnd }: Props) {
  const [editing, setEditing] = useState(false);

  function commit(raw: string) {
    setEditing(false);
    const v = parseInt(raw, 10);
    if (!Number.isNaN(v) && v !== n) onRenumber?.(v);
  }

  return (
    <div
      className="wf-card"
      draggable={!editing}
      onClick={onClick}
      onDragStart={(e) => {
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/plain", String(n));
        onDragStart?.();
      }}
      onDragEnter={() => onDragEnter?.()}
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault();
        onDrop?.();
      }}
      onDragEnd={() => onDragEnd?.()}
      style={{
        width: 160,
        flexShrink: 0,
        position: "relative",
        padding: 6,
        display: "flex",
        flexDirection: "column",
        gap: 6,
        borderColor: selected || isDragging ? "var(--accent)" : "var(--border)",
        borderWidth: 1,
        boxShadow: isDragging ? "0 14px 28px rgba(0,0,0,.5), 0 0 0 1px var(--accent)" : selected ? "0 0 0 1px var(--accent)" : "none",
        background: selected || isDragging ? "var(--bg-3)" : "var(--bg-2)",
        opacity: dim ? 0.55 : 1,
        transform: isDragging ? "translateY(-10px) rotate(-3deg)" : "none",
        cursor: "grab",
        transition: "border-color .12s, background .12s",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        {editing ? (
          <input
            className="wf-input"
            type="text"
            inputMode="numeric"
            autoFocus
            defaultValue={n}
            onClick={(e) => e.stopPropagation()}
            onKeyDown={(e) => {
              if (e.key === "Enter") commit((e.target as HTMLInputElement).value);
              if (e.key === "Escape") setEditing(false);
            }}
            onBlur={(e) => commit(e.target.value)}
            style={{
              width: 46,
              padding: "1px 5px",
              fontFamily: "IBM Plex Mono, monospace",
              fontSize: 11,
              textAlign: "center",
            }}
          />
        ) : (
          // number reads as editable: dashed underline + pencil, click to renumber
          <span
            title="Sırayı değiştir — yeni numara yaz"
            onClick={(e) => {
              e.stopPropagation();
              setEditing(true);
            }}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 3,
              borderBottom: "1px dashed " + (selected ? "var(--accent)" : "var(--border-strong)"),
              paddingBottom: 1,
              cursor: "text",
            }}
          >
            <Seq n={n} hl={selected} />
            <span style={{ display: "inline-flex", color: selected ? "var(--accent)" : "var(--ink-3)" }}>
              <Icon.Pencil />
            </span>
          </span>
        )}
        <span style={{ flex: 1 }} />
        <Grip style={{ opacity: 0.9, cursor: "grab" }} />
      </div>
      <ImgPH loading={loading} style={{ aspectRatio: "16/10", width: "100%" }} label={`sc ${n}`} />
    </div>
  );
}
