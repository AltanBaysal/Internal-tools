// What the server actually said, in one place, because there are two roads out of the browser: the
// plain request and the stream. Never a cause of our own -- a 409 is not "the file is locked" and a
// 502 is not "the connection dropped", and reading the body is the only way to know which it is.

export async function failureFrom(response) {
  const failure = new Error(await saidBy(response));
  // The code is carried separately: "this does not exist" is a screen, not an error line.
  failure.status = response.status;
  return failure;
}

async function saidBy(response) {
  const body = await response.text();
  try {
    const written = JSON.parse(body);
    if (typeof written?.error === "string" && written.error) return written.error;
  } catch {
    // Not JSON -- an HTML error page, or nothing at all. Both are still what it said.
  }
  return body.trim() ? `HTTP ${response.status}: ${body.trim()}` : `HTTP ${response.status}`;
}
