// The design's one waiting ring (items 173 and 181). It is only the ring: each place that waits
// wraps it in a box of its own, so where it stands and how much room it gets is that place's.
// It says nothing -- the heading and the buttons left standing around it say what is loading.
export default function Spinner() {
  return <span className="spinner" aria-hidden="true" data-testid="spinner" />;
}
