import { findSkill } from "./skills.js";

const TURKISH = "Kullanıcıyla Türkçe konuş.";

// The model is told what exists, never what each one says: a skill's instructions arrive only when
// the user calls it, so ten unused skills cost about ten lines instead of ten documents. Knowing
// the list is what lets it answer "bunun için /plan-yazma kullanabilirsin".
export function systemMessage(skills) {
  if (skills.length === 0) return TURKISH;
  const list = skills.map((skill) => `- /${skill.name}: ${skill.description}`).join("\n");
  return `${TURKISH}\n\nKullanıcı mesajının başına /ad yazarak şu skill'lerden birini çağırabilir:\n${list}`;
}

// The screen keeps error rows so the user can see what happened, but xAI rejects any role it does
// not know, so they are dropped on the way out. Only role and content travel: anything the screen
// adds to a message stays on the screen.
export function toRequestBody(messages, model, skills = [], files = []) {
  // One file opens once per conversation. Walking in order and remembering what has been opened
  // keeps the cost tied to how many files were used, not to how many times they were named.
  const opened = new Set();
  return {
    model,
    messages: [
      { role: "system", content: systemMessage(skills) },
      ...messages
        .filter((m) => m.role === "user" || m.role === "assistant")
        .map((m) => ({ role: m.role, content: expand(m, skills, files, opened) })),
    ],
  };
}

// Instruction first, material second, request last: that is the order a person would put them in,
// and the model reads it the same way. Neither the skill nor the file is stored with the message —
// only their names are — so both are folded in here, on the way out. Two consequences, both
// wanted: fixing a skill or a file also fixes every old chat that used it, and one that was
// deleted sends the user's own words alone rather than making the chat unsendable.
function expand(message, skills, files, opened) {
  const parts = [];

  if (message.skill) {
    const skill = findSkill(skills, message.skill);
    if (skill) parts.push(skill.body);
  }

  for (const name of message.files ?? []) {
    if (opened.has(name)) continue;
    const file = files.find((f) => f.name === name);
    if (!file) continue;
    opened.add(name);
    parts.push(`\`@${name}\` dosyasının içeriği:\n---\n${file.content}\n---`);
  }

  parts.push(message.content);
  return parts.join("\n\n");
}

// The service's own words: a 401 is equally a bad key and a bad model id, so naming one cause here
// would send the reader down the wrong path.
export function formatHttpError(status, body) {
  return `HTTP ${status} — ${body}`;
}
