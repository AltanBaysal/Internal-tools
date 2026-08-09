// Blocks where the content will be. They carry no text: a skeleton stands in for something that has
// not arrived, and words would be inventing what it says.
export default function Skeleton({ rows = 1, variant = "row" }) {
  return (
    <div className={`skeleton skeleton--${variant}`} data-testid="skeleton">
      {Array.from({ length: rows }, (_, index) => (
        <span key={index} className="skeleton__block" />
      ))}
    </div>
  );
}
