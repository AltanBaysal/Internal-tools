// A deliberately narrow slice of YAML: `key: value` plus indented continuation lines. Skills are
// hand-written files with two fields that matter, and a real parser would be a dependency this app
// otherwise does not need.
const NAME_RULE = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const NAME_MAX = 64;
const DESCRIPTION_MAX = 1024;

export function parseSkill(raw) {
  const lines = raw.split(/\r?\n/);
  if (lines[0].trim() !== "---") {
    throw new Error("frontmatter yok — dosya --- satırıyla başlamalı");
  }
  const end = lines.findIndex((line, i) => i > 0 && line.trim() === "---");
  if (end === -1) {
    throw new Error("frontmatter kapanmamış — ikinci --- satırı yok");
  }

  const fields = {};
  let current = null;
  for (const line of lines.slice(1, end)) {
    const opened = line.match(/^([A-Za-z][\w-]*):\s*(.*)$/);
    if (opened) {
      current = opened[1];
      fields[current] = opened[2].trim();
    } else if (current && /^\s+\S/.test(line)) {
      fields[current] = `${fields[current]} ${line.trim()}`.trim();
    }
  }

  const name = fields.name ?? "";
  const description = fields.description ?? "";

  if (!NAME_RULE.test(name) || name.length > NAME_MAX) {
    throw new Error(
      `geçersiz name: "${name}" — yalnız küçük harf, rakam ve tek tire, en fazla ${NAME_MAX} karakter`
    );
  }
  if (!description || description.length > DESCRIPTION_MAX) {
    throw new Error(
      `geçersiz description — 1-${DESCRIPTION_MAX} karakter olmalı, şu an ${description.length}`
    );
  }

  return { name, description, body: lines.slice(end + 1).join("\n").trim() };
}

// The folder is the skill's identity, so a file whose `name` disagrees with it is rejected rather
// than silently renamed: the two would drift and `/ad` would stop matching what the reader sees.
export function loadSkills(files) {
  const skills = [];
  const errors = [];

  for (const path of Object.keys(files).sort()) {
    const folder = path.split("/").at(-2);
    try {
      const skill = parseSkill(files[path]);
      if (skill.name !== folder) {
        throw new Error(`name "${skill.name}", klasör adı "${folder}" ile aynı değil`);
      }
      skills.push(skill);
    } catch (err) {
      // One hand-written file must not take the whole list down with it.
      errors.push({ path, reason: err.message });
    }
  }

  skills.sort((a, b) => a.name.localeCompare(b.name));
  return { skills, errors };
}

export function findSkill(skills, name) {
  return skills.find((skill) => skill.name === name) ?? null;
}

// Contains rather than starts-with: with a handful of skills there is no ambiguity to protect
// against, and `/yazma` finding `plan-yazma` is what someone half-remembering a name would expect.
export function matchSkills(skills, query) {
  const wanted = query.toLowerCase();
  return skills.filter((skill) => skill.name.includes(wanted));
}

// Only a whole name at the very start counts as a call. A slash anywhere else is ordinary text —
// file paths and dates would otherwise be swallowed. Upper case is matched on purpose although the
// standard forbids it: the caller can then say "no such skill" instead of silently sending `/Plan`
// as prose.
const CALL = /^\/([A-Za-z0-9-]+)(?:\s+([\s\S]*))?$/;

export function splitSkillPrefix(text) {
  const called = text.match(CALL);
  if (!called) return { name: null, content: text };
  return { name: called[1], content: (called[2] ?? "").trim() };
}
