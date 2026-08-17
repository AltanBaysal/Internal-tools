// Every request goes through here: a component never calls fetch itself and no caller checks
// resp.ok on its own, so "the server said no" has exactly one meaning across the app.
async function request(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const failure = new Error(`${options?.method ?? "GET"} ${path} failed with ${response.status}`);
    // The code is carried separately: "this does not exist" is a screen, not an error line.
    failure.status = response.status;
    throw failure;
  }
  return response.json();
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
