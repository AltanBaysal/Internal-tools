// The design's formula. The hue is stored with the project, so adding or removing a neighbour never
// recolours an existing card.
export default function ProjectDot({ hue, size = 9 }) {
  return (
    <span
      className="dot"
      style={{
        width: size,
        height: size,
        borderRadius: size / 3,
        background: `oklch(0.72 0.09 ${hue})`,
      }}
    />
  );
}
