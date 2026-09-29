// One of a thing is one, not one of them -- the design writes the sentence out that way, in the
// delete question and on the All projects row alike.
export function countOf(many, word) {
  return `${many} ${word}${many === 1 ? "" : "s"}`;
}
