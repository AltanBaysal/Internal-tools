// Every request goes through here: a component never calls fetch itself and no caller checks
// resp.ok on its own, so "the server said no" has exactly one meaning across the app.
async function request(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    throw new Error(`${options?.method ?? "GET"} ${path} failed with ${response.status}`);
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
