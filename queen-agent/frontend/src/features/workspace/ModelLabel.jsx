// Which model answers, and that is all: since Madde 82 there is one, so there is nothing to
// choose. config.py holds its id; this holds the name a person reads, and the two move together --
// Python and JS cannot read each other, so nothing but this sentence keeps them in step.
//
// A span rather than a button: a control that opens nothing would be a promise the app cannot
// keep.
export default function ModelLabel() {
  return <span className="model-label">Grok Build</span>;
}
