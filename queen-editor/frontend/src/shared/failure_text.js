// The sentence a panel draws and the proof its copy button hands over travel as one string: line
// one is read, the rest is evidence. QueuePanel splits them at that first newline, so a failure
// that carries no proof must not gain an empty line here.
export function failureText(err) {
  return err.evidence ? `${err.message}\n${err.evidence}` : err.message;
}
