// Markdown, exactly as much of it as the design names: headings 1-4, bold, italic, strikethrough,
// inline code, fenced code, lists, tables, quotes, rules and links. Anything outside that list stays
// the text it was typed as -- a parser that guesses reads worse than one that leaves the marks
// showing.
//
// It returns data and never HTML: the component builds React elements from these tokens, so a
// reply has no way to reach into the page.

const FENCE = "```";
const HEADING = /^(#{1,4}) +(.*)$/;
const RULE = /^ {0,3}(-{3,}|\*{3,})\s*$/;
const BULLET = /^(\s*)[-*+] +(.*)$/;
const NUMBER = /^(\s*)\d+\. +(.*)$/;
const QUOTE = /^ {0,3}> ?(.*)$/;
const LINK = /^\[([^\]]*)\]\(([^)\s]*)\)/;
// The only targets a rendered answer may carry. Anything else -- javascript: above all -- is left as
// the characters it was written with.
const HREF = /^(https?:\/\/|mailto:)/i;

const PAIRS = [
  ["**", "strong"],
  ["~~", "del"],
  ["*", "em"],
  ["_", "em"],
];

export function parseBlocks(text) {
  return blocksFrom(String(text ?? "").replace(/\r\n?/g, "\n").split("\n"));
}

function blocksFrom(lines) {
  const blocks = [];
  let at = 0;

  while (at < lines.length) {
    const line = lines[at];
    if (!line.trim()) {
      at += 1;
      continue;
    }

    if (line.trimStart().startsWith(FENCE)) {
      const lang = line.trimStart().slice(FENCE.length).trim();
      const body = [];
      at += 1;
      while (at < lines.length && !lines[at].trimStart().startsWith(FENCE)) {
        body.push(lines[at]);
        at += 1;
      }
      // One past the closing fence, or one past the end when it never came: an answer still
      // arriving must not lose its half-written block.
      at += 1;
      blocks.push({ type: "code", lang: lang || null, text: body.join("\n") });
      continue;
    }

    if (RULE.test(line)) {
      blocks.push({ type: "rule" });
      at += 1;
      continue;
    }

    const heading = HEADING.exec(line);
    if (heading) {
      blocks.push({ type: "heading", level: heading[1].length, inline: parseInline(heading[2]) });
      at += 1;
      continue;
    }

    if (QUOTE.test(line)) {
      const body = [];
      while (at < lines.length && QUOTE.test(lines[at])) {
        body.push(QUOTE.exec(lines[at])[1]);
        at += 1;
      }
      blocks.push({ type: "quote", blocks: blocksFrom(body) });
      continue;
    }

    if (opensTable(lines, at)) {
      const head = cellsOf(lines[at]);
      at += 2;
      const rows = [];
      while (at < lines.length && lines[at].trim() && lines[at].includes("|")) {
        rows.push(cellsOf(lines[at]));
        at += 1;
      }
      blocks.push({ type: "table", head, rows });
      continue;
    }

    if (BULLET.test(line) || NUMBER.test(line)) {
      const [list, next] = listFrom(lines, at);
      blocks.push(list);
      at = next;
      continue;
    }

    const body = [];
    do {
      body.push(lines[at].trim());
      at += 1;
    } while (at < lines.length && lines[at].trim() && !opensBlock(lines, at));
    blocks.push({ type: "paragraph", inline: parseInline(body.join("\n")) });
  }

  return blocks;
}

// A line that ends whatever paragraph is running. Models write the sentence and its bullets back to
// back, and swallowed into the paragraph the markers would show up as characters.
function opensBlock(lines, at) {
  const line = lines[at];
  return (
    line.trimStart().startsWith(FENCE) ||
    RULE.test(line) ||
    HEADING.test(line) ||
    QUOTE.test(line) ||
    BULLET.test(line) ||
    NUMBER.test(line) ||
    opensTable(lines, at)
  );
}

// The pipes alone prove nothing -- a sentence may hold one. It is the dashed row underneath that
// says this is a table.
function opensTable(lines, at) {
  return lines[at].includes("|") && isSeparator(lines[at + 1] ?? "");
}

function isSeparator(line) {
  if (!line.includes("|")) return false;
  const cells = splitRow(line);
  // The colons are read only far enough to recognise the row: no column in the design is aligned.
  return cells.length > 0 && cells.every((cell) => /^:?-+:?$/.test(cell.trim()));
}

function splitRow(line) {
  let text = line.trim();
  if (text.startsWith("|")) text = text.slice(1);
  if (text.endsWith("|")) text = text.slice(0, -1);
  return text.split("|");
}

function cellsOf(line) {
  return splitRow(line).map((cell) => parseInline(cell.trim()));
}

// Every item at this indent, with a deeper run of items hung under the item above it.
function listFrom(lines, start) {
  const first = BULLET.exec(lines[start]) ?? NUMBER.exec(lines[start]);
  const indent = first[1].length;
  const ordered = !BULLET.test(lines[start]);
  const items = [];
  let at = start;

  while (at < lines.length) {
    const item = BULLET.exec(lines[at]) ?? NUMBER.exec(lines[at]);
    if (!item) break;
    const depth = item[1].length;
    if (depth < indent) break;

    if (depth > indent) {
      const [nested, next] = listFrom(lines, at);
      const owner = items[items.length - 1];
      owner.blocks = [...(owner.blocks ?? []), nested];
      at = next;
      continue;
    }

    // A numbered item under bullets is a list of its own, not a stray member of this one.
    if (!BULLET.test(lines[at]) !== ordered) break;
    items.push({ inline: parseInline(item[2]) });
    at += 1;
  }

  return [{ type: "list", ordered, items }, at];
}

export function parseInline(text) {
  const source = String(text ?? "");
  const tokens = [];
  let plain = "";
  let at = 0;

  const flush = () => {
    if (plain) tokens.push({ type: "text", text: plain });
    plain = "";
  };

  while (at < source.length) {
    const rest = source.slice(at);

    if (source[at] === "\n") {
      flush();
      tokens.push({ type: "break" });
      at += 1;
      continue;
    }

    // Code first and code wins: between backticks every other marker is a character.
    if (source[at] === "`") {
      const end = source.indexOf("`", at + 1);
      if (end > at + 1) {
        flush();
        tokens.push({ type: "code", text: source.slice(at + 1, end) });
        at = end + 1;
        continue;
      }
    }

    if (source[at] === "[") {
      const link = LINK.exec(rest);
      if (link && HREF.test(link[2])) {
        flush();
        tokens.push({ type: "link", href: link[2], tokens: parseInline(link[1]) });
        at += link[0].length;
        continue;
      }
    }

    const emphasis = emphasisAt(rest, source[at - 1]);
    if (emphasis) {
      flush();
      tokens.push(emphasis.token);
      at += emphasis.length;
      continue;
    }

    plain += source[at];
    at += 1;
  }

  flush();
  return tokens;
}

function emphasisAt(rest, before) {
  for (const [marker, type] of PAIRS) {
    if (!rest.startsWith(marker)) continue;
    // `read_file` and `snake_case` are ordinary words here, so an underscore only opens emphasis
    // when it does not sit inside one.
    if (marker === "_" && /\w/.test(before ?? "")) continue;
    const body = closedBody(rest, marker);
    if (body === null) continue;
    return { token: { type, tokens: parseInline(body) }, length: body.length + marker.length * 2 };
  }
  return null;
}

// The text between a marker and its partner, or null when there is no partner. The opener must be
// followed by a non-space and the closer preceded by one, so "2 * 3 * 4" stays arithmetic.
function closedBody(rest, marker) {
  const from = marker.length;
  if (/\s/.test(rest[from] ?? " ")) return null;

  let at = rest.indexOf(marker, from + 1);
  while (at > -1) {
    if (!/\s/.test(rest[at - 1])) {
      // "**bold *and italic***" ends on a run of three: the outer pair is the last two of them, and
      // the one left over closes the emphasis inside.
      let run = 0;
      while (rest[at + run] === marker[0]) run += 1;
      const close = run > marker.length ? at + run - marker.length : at;
      return rest.slice(from, close);
    }
    at = rest.indexOf(marker, at + 1);
  }
  return null;
}
