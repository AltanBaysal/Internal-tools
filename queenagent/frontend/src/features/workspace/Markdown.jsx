import { Fragment } from "react";

import { parseBlocks } from "../../shared/markdown.js";

// Tokens become React elements here and nowhere else. The wrapper carries no size of its own: the
// container it sits in picks the scale, so one parser serves both the bubble and the file panel.
//
// While an answer is still arriving a caret marks where it has got to. That is the end of the text,
// which in a tree of blocks is a rule rather than a position: it descends to the last block, and
// into it wherever the block has a text end to sit at.

function Caret() {
  return <span className="caret" />;
}

function inline(tokens) {
  return tokens.map((token, key) => {
    switch (token.type) {
      case "break":
        return <br key={key} />;
      case "code":
        return <code key={key}>{token.text}</code>;
      case "link":
        // A local page opening a document's link: a new tab, and no referrer to carry.
        return (
          <a key={key} href={token.href} target="_blank" rel="noreferrer">
            {inline(token.tokens)}
          </a>
        );
      case "strong":
        return <strong key={key}>{inline(token.tokens)}</strong>;
      case "em":
        return <em key={key}>{inline(token.tokens)}</em>;
      case "del":
        return <del key={key}>{inline(token.tokens)}</del>;
      default:
        return token.text;
    }
  });
}

// The caret belongs to the last block of a run -- and to the run itself when there is no block yet,
// which is the first frame of every answer.
function blockList(nodes, caret) {
  if (!nodes.length) return caret ? <Caret /> : null;
  return nodes.map((node, key) => block(node, key, caret && key === nodes.length - 1));
}

function block(node, key, caret) {
  switch (node.type) {
    case "heading": {
      const Heading = `h${node.level}`;
      return (
        <Heading key={key}>
          {inline(node.inline)}
          {caret ? <Caret /> : null}
        </Heading>
      );
    }
    case "code":
      return (
        <pre key={key}>
          <code>
            {node.text}
            {caret ? <Caret /> : null}
          </code>
        </pre>
      );
    case "rule":
      // Nothing to sit at the end of, so the caret takes a line of its own.
      return (
        <Fragment key={key}>
          <hr />
          {caret ? <Caret /> : null}
        </Fragment>
      );
    case "quote":
      return <blockquote key={key}>{blockList(node.blocks, caret)}</blockquote>;
    case "list": {
      const List = node.ordered ? "ol" : "ul";
      return (
        <List key={key}>
          {node.items.map((item, index) => {
            const last = caret && index === node.items.length - 1;
            return (
              <li key={index}>
                {inline(item.inline)}
                {item.blocks ? blockList(item.blocks, last) : null}
                {last && !item.blocks ? <Caret /> : null}
              </li>
            );
          })}
        </List>
      );
    }
    case "table":
      // Its own scroller: the page never scrolls sideways, so a wide table scrolls inside itself.
      return (
        <Fragment key={key}>
          <div className="md__table-scroll">
            <table>
              <thead>
                <tr>
                  {node.head.map((cell, index) => (
                    <th key={index}>{inline(cell)}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {node.rows.map((row, index) => (
                  <tr key={index}>
                    {row.map((cell, column) => (
                      <td key={column}>{inline(cell)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {caret ? <Caret /> : null}
        </Fragment>
      );
    default:
      return (
        <p key={key}>
          {inline(node.inline)}
          {caret ? <Caret /> : null}
        </p>
      );
  }
}

export default function Markdown({ text, caret = false }) {
  return <div className="md">{blockList(parseBlocks(text), caret)}</div>;
}
