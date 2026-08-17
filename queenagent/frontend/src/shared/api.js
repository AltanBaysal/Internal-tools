// Every request goes through here: a component never calls fetch itself and no caller checks
// resp.ok on its own, so "the server said no" has exactly one meaning across the app.
async function request(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const failure = new Error(await saidBy(response));
    // The code is carried separately: "this does not exist" is a screen, not an error line.
    failure.status = response.status;
    throw failure;
  }
  return response.json();
}

// What the server actually said, and never a cause of our own. A 409 is not "the file is locked" and
// a 502 is not "the connection dropped" -- reading the body is the only way to know.
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

function sendJson(method, path, body) {
  const options = { method };
  if (body !== undefined) {
    options.headers = { "Content-Type": "application/json" };
    options.body = JSON.stringify(body);
  }
  return request(path, options);
}

export function getJson(path) {
  return request(path);
}

export function postJson(path, body) {
  return sendJson("POST", path, body);
}

export function patchJson(path, body) {
  return sendJson("PATCH", path, body);
}

// Deleting answers with a body like everything else -- 204 would need an exception here, and this
// is the one place that decides what a response means.
export function deleteJson(path) {
  return sendJson("DELETE", path);
}
