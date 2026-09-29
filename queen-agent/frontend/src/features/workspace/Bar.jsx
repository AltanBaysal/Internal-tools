import { VERSION } from "../../shared/version.js";

// Across the window's top, on every screen (the design's items 150, 159, 161, 166): the name and
// the run number on the left, the open project's name in the middle, and on the right the screen's
// own way out -- Exit project in a project, Cancel on the naming screen (the design's 195). With
// nothing to show the middle and the right draw nothing; the stylesheet's grid keeps the bar where
// it was.
export default function Bar({ project, exit = project ? "Exit project" : null, onExit }) {
  return (
    <header className="bar">
      {/* Two spans with a space between, so the pair is read out as two words; the version is not
          a footnote but the name's own size and weight, as Queen Editor writes "Queen Editor 1.4.2". */}
      <span className="bar__name">
        <span className="bar__wordmark">QueenAgent</span>{" "}
        <span className="bar__version">{VERSION}</span>
      </span>
      {project ? (
        <span className="bar__project" title={project.name}>
          {project.name}
        </span>
      ) : null}
      {exit ? (
        <button type="button" className="ghost bar__exit" onClick={onExit}>
          {exit}
        </button>
      ) : null}
    </header>
  );
}
