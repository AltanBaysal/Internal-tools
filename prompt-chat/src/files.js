const DEFAULT_EXTENSION = ".md";

// Everything this app writes is markdown, so typing the extension is friction with no payoff. A
// name that already has a dot is left alone: the user meant something by it.
export function normaliseName(raw) {
  const trimmed = raw.trim();
  return trimmed.includes(".") ? trimmed : trimmed + DEFAULT_EXTENSION;
}

export function filesOf(files, projectId) {
  return files.filter((file) => file.projectId === projectId);
}

// Ids are unique across the whole store, not per project: a file is looked up by id everywhere
// except in `@ad`, and per-project numbering would make two files share one.
export function createFile(files, projectId, rawName) {
  if (!rawName.trim()) throw new Error("dosya adı boş olamaz");
  const name = normaliseName(rawName);
  if (filesOf(files, projectId).some((file) => file.name === name)) {
    throw new Error(`"${name}" adında bir dosya zaten var`);
  }
  const id = files.reduce((max, file) => Math.max(max, file.id), 0) + 1;
  return { files: [...files, { id, projectId, name, content: "" }], id };
}

export function writeFile(files, id, content) {
  return files.map((file) => (file.id === id ? { ...file, content } : file));
}

export function deleteFile(files, id) {
  return files.filter((file) => file.id !== id);
}

// Name lookup is scoped to a project because `@ad` is written inside one: the same name may exist
// elsewhere and must not be reachable from here.
export function findFile(files, projectId, name) {
  return filesOf(files, projectId).find((file) => file.name === name) ?? null;
}

// An @ followed by a whole file name is a call; an @ followed by anything else is ordinary text.
// The name must exist in the project, because @ turns up in prose and addresses all the time and
// treating every one as a call would raise false alarms on `@herkes` and `ali@example.com`.
export function mentionedFiles(text, projectFiles) {
  const names = new Set(projectFiles.map((file) => file.name));
  const found = [];
  for (const [, candidate] of text.matchAll(/@([^\s@]+)/g)) {
    if (names.has(candidate) && !found.includes(candidate)) found.push(candidate);
  }
  return found;
}

// The list belongs to the moment a name is being typed. Splitting on whitespace and looking at the
// last piece is enough for that, and it works mid-sentence because what you are typing is always
// the last piece. Moving the caret back into finished text does not reopen it — tracking the caret
// is more machinery than the gain is worth.
export function activeMention(draft) {
  const last = draft.split(/\s/).at(-1);
  return last && last.startsWith("@") ? last.slice(1) : null;
}

export function replaceActiveMention(draft, name) {
  return `${draft.slice(0, draft.lastIndexOf("@"))}@${name} `;
}

export function matchFiles(projectFiles, query) {
  const wanted = query.toLowerCase();
  return projectFiles.filter((file) => file.name.toLowerCase().includes(wanted));
}
