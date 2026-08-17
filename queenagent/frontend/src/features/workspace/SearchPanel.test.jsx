import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import SearchPanel from "./SearchPanel.jsx";

const HITS = [
  { kind: "project", label: "Thesis", projectId: "p1", projectName: "", chatId: "", fileName: "" },
  {
    kind: "file",
    label: "outline.md",
    projectId: "p1",
    projectName: "Thesis",
    chatId: "",
    fileName: "outline.md",
  },
];

test("the input takes the keyboard the moment the panel opens", () => {
  render(<SearchPanel query="" />);
  expect(document.activeElement).toBe(screen.getByPlaceholderText(/Search projects/));
});

test("every row says what kind of thing it is", () => {
  render(<SearchPanel query="th" hits={HITS} searched />);
  expect(screen.getByText("project")).toBeTruthy();
  expect(screen.getByText("file")).toBeTruthy();
  expect(screen.getByText("outline.md")).toBeTruthy();
});

test("a row that lives in a project says which one", () => {
  render(<SearchPanel query="th" hits={HITS} searched />);
  // Eight results can come from eight projects, so the row answers that before the click.
  expect(screen.getByText("Thesis", { selector: ".hit__where" })).toBeTruthy();
});

test("picking a row hands the whole hit back", () => {
  const onPick = vi.fn();
  render(<SearchPanel query="th" hits={HITS} searched onPick={onPick} />);
  fireEvent.click(screen.getByText("outline.md"));
  expect(onPick).toHaveBeenCalledWith(HITS[1]);
});

test("a search that found nothing says so", () => {
  render(<SearchPanel query="zzz" hits={[]} searched />);
  expect(screen.getByText("No results.")).toBeTruthy();
});

test("an empty box says nothing at all", () => {
  // Nothing has been searched for yet, so there is no result to report.
  render(<SearchPanel query="" hits={[]} />);
  expect(screen.queryByText("No results.")).toBeNull();
});

test("typing is passed straight up", () => {
  const onQuery = vi.fn();
  render(<SearchPanel query="" onQuery={onQuery} />);
  fireEvent.change(screen.getByPlaceholderText(/Search projects/), { target: { value: "q" } });
  expect(onQuery).toHaveBeenCalledWith("q");
});

test("a click outside closes, a click inside does not", () => {
  const onClose = vi.fn();
  render(<SearchPanel query="th" hits={HITS} searched onClose={onClose} />);
  fireEvent.click(screen.getByPlaceholderText(/Search projects/));
  expect(onClose).not.toHaveBeenCalled();
  fireEvent.click(screen.getByTestId("search"));
  expect(onClose).toHaveBeenCalled();
});
