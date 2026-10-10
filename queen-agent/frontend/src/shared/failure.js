// What the server actually said, in one place. Never a cause of our own -- a 409 is not "the file
// is locked" and a 502 is not "the connection dropped", and reading the body is the only way to know
// which it is.

export async function failureFrom(response) {
  const { said, body } = await read(response);
  const failure = new Error(said);
  // The code is carried separately: "this does not exist" is a screen, not an error line.
  failure.status = response.status;
  // And whatever else the refusal said, or null: a message refused while a turn runs names that
  // turn (Madde 462), and the screen follows it.
  failure.body = body;
  return failure;
}

async function read(response) {
  const text = await response.text();
  let written = null;
  try {
    written = JSON.parse(text);
  } catch {
    // Not JSON -- an HTML error page, or nothing at all. Both are still what it said.
  }
  if (typeof written?.error === "string" && written.error) return { said: written.error, body: written };
  const said = text.trim() ? `HTTP ${response.status}: ${text.trim()}` : `HTTP ${response.status}`;
  return { said, body: written };
}
