import { parseBlocks } from "../../shared/markdown.js";

// Tokens become React elements here and nowhere else. The wrapper carries no size of its own: the
// container it sits in picks the scale, so one parser serves both the bubble and the file panel.

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

function block(node, key) {
  switch (node.type) {
    case "heading": {
      const Heading = `h${node.level}`;
      return <Heading key={key}>{inline(node.inline)}</Heading>;
    }
    case "code":
      return (
        <pre key={key}>
          <code>{node.text}</code>
        </pre>
      );
    case "rule":
      return <hr key={key} />;
    case "quote":
      return <blockquote key={key}>{node.blocks.map(block)}</blockquote>;
    case "list": {
      const List = node.ordered ? "ol" : "ul";
      return (
        <List key={key}>
          {node.items.map((item, index) => (
            <li key={index}>
              {inline(item.inline)}
              {item.blocks?.map(block)}
            </li>
          ))}
        </List>
      );
    }
    case "table":
      // Its own scroller: the page never scrolls sideways, so a wide table scrolls inside itself.
      return (
        <div className="md__table-scroll" key={key}>
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
      );
    default:
      return <p key={key}>{inline(node.inline)}</p>;
  }
}

export default function Markdown({ text }) {
  return <div className="md">{parseBlocks(text).map(block)}</div>;
}
