import { useLayoutEffect, useRef, useState } from "react";
import { Btn, Grip, Icon, Mono } from "../../../components/primitives";
import type { Scene } from "../types";
import TimelineCard from "./TimelineCard";
import AddSceneTile from "./AddSceneTile";
import FauxScrollbar from "./FauxScrollbar";

interface Props {
  scenes: Scene[];
  selectedIdx: number;
  loadingAtEnd?: boolean;
  addSelected?: boolean;
  onSelect: (id: string) => void;
  onAdd: () => void;
  onPrev: () => void;
  onNext: () => void;
  onReorder: (fromIdx: number, toIdx: number) => void;
}

/** Bottom scene strip: reorder hint + nav + counter, horizontally scrolling
    thumbnails with drag-drop reorder, and the faux scrollbar synced to real
    scroll. Ported from TimelineFooter + the v2 reorder affordances. */
export default function TimelineFooter({ scenes, selectedIdx, loadingAtEnd, addSelected, onSelect, onAdd, onPrev, onNext, onReorder }: Props) {
  const stripRef = useRef<HTMLDivElement>(null);
  const [scroll, setScroll] = useState({ progress: 0, thumb: 1 });
  const [dragIdx, setDragIdx] = useState<number | null>(null);
  const [dropIdx, setDropIdx] = useState<number | null>(null);

  function syncScroll() {
    const el = stripRef.current;
    if (!el) return;
    const max = el.scrollWidth - el.clientWidth;
    setScroll({
      progress: max > 0 ? el.scrollLeft / max : 0,
      thumb: el.scrollWidth > 0 ? Math.min(1, el.clientWidth / el.scrollWidth) : 1,
    });
  }

  useLayoutEffect(syncScroll, [scenes.length, loadingAtEnd]);

  function commitDrop(target: number) {
    if (dragIdx != null) onReorder(dragIdx, target);
    setDragIdx(null);
    setDropIdx(null);
  }

  const empty = scenes.length === 0 && !loadingAtEnd;
  const total = scenes.length + (loadingAtEnd ? 1 : 0);
  const curr = empty ? 0 : addSelected || loadingAtEnd ? scenes.length + 1 : selectedIdx + 1;
  const dragging = dragIdx != null;

  return (
    <footer
      style={{
        background: "var(--bg)",
        borderTop: "1px solid var(--border)",
        padding: "10px 0 8px",
        display: "flex",
        flexDirection: "column",
        gap: 6,
        flexShrink: 0,
      }}
    >
      {/* strip header: reorder hint + nav + position counter */}
      <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "0 24px" }}>
        {!empty && (
          <Mono size={11} style={{ color: "var(--ink-3)", display: "inline-flex", alignItems: "center", gap: 6 }}>
            <Grip style={{ opacity: 0.8 }} /> sürükle ya da numaraya dokun — sıra otomatik güncellenir
          </Mono>
        )}
        <span style={{ flex: 1 }} />
        {!empty && (
          <>
            <Btn sm ghost icon title="önceki" onClick={onPrev}>
              <Icon.Left />
            </Btn>
            <Btn sm ghost icon title="sonraki" onClick={onNext}>
              <Icon.Right />
            </Btn>
          </>
        )}
        <Mono size={11} style={{ color: "var(--ink-3)", paddingLeft: 4 }}>
          {String(curr).padStart(3, "0")} / {String(total).padStart(3, "0")}
        </Mono>
      </div>

      {/* strip — real horizontal scroll, native bar hidden */}
      <div ref={stripRef} className="qe-strip" onScroll={syncScroll} style={{ display: "flex", overflowX: "auto", padding: "4px 24px" }}>
        <div style={{ display: "flex", gap: 8, paddingRight: 100, alignItems: "flex-start" }}>
          {scenes.map((s, i) => (
            <div key={s.id} style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
              {/* insertion indicator at the drop target */}
              {dragging && dropIdx === i && i !== dragIdx && (
                <div style={{ position: "relative", width: 0, flexShrink: 0, alignSelf: "stretch" }}>
                  <div
                    style={{
                      position: "absolute",
                      top: -2,
                      bottom: -2,
                      left: -4,
                      width: 3,
                      background: "var(--accent)",
                      borderRadius: 2,
                      boxShadow: "0 0 0 3px rgba(167,139,250,.18)",
                    }}
                  />
                </div>
              )}
              <TimelineCard
                n={i + 1}
                selected={i === selectedIdx && !loadingAtEnd}
                isDragging={i === dragIdx}
                dim={dragging && i !== dragIdx}
                onClick={() => onSelect(s.id)}
                onRenumber={(newN) => onReorder(i, newN - 1)}
                onDragStart={() => {
                  setDragIdx(i);
                  setDropIdx(i);
                }}
                onDragEnter={() => dragging && setDropIdx(i)}
                onDrop={() => commitDrop(i)}
                onDragEnd={() => {
                  setDragIdx(null);
                  setDropIdx(null);
                }}
              />
            </div>
          ))}
          {loadingAtEnd && <TimelineCard n={scenes.length + 1} loading selected />}
          <AddSceneTile nextN={scenes.length + (loadingAtEnd ? 2 : 1)} selected={addSelected} onClick={onAdd} />
        </div>
      </div>

      {/* faux scrollbar — only when there is something to scroll */}
      {!empty && (
        <div style={{ padding: "0 24px" }}>
          <FauxScrollbar progress={scroll.progress} thumb={scroll.thumb} marks={Math.min(scenes.length, 12)} />
        </div>
      )}
    </footer>
  );
}
