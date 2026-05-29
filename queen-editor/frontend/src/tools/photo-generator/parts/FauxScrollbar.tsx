/** Custom scrollbar under the strip. Driven by real scroll metrics from
    TimelineFooter (the prototype faked the values). Ported from FauxScrollbar. */
export default function FauxScrollbar({ progress, thumb, marks }: { progress: number; thumb: number; marks: number }) {
  return (
    <div style={{ position: "relative", height: 14, padding: "0 4px" }}>
      <div style={{ position: "absolute", left: 4, right: 4, top: 6, height: 2, background: "var(--border)", borderRadius: 2 }} />
      {marks > 1 &&
        Array.from({ length: marks }).map((_, i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `calc(${4 + (i / (marks - 1)) * 100}% - ${(i / (marks - 1)) * 8 + 4}px)`,
              top: 3,
              width: 1,
              height: 8,
              background: "var(--ink-4)",
            }}
          />
        ))}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: `calc(${progress * (1 - thumb) * 100}% + 4px)`,
          width: `${thumb * 100}%`,
          height: 14,
          background: "var(--ink-2)",
          borderRadius: 7,
          maxWidth: "calc(100% - 8px)",
        }}
      />
    </div>
  );
}
