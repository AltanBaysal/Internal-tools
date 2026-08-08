import { describe, expect, it } from "vitest";

import { photoPath, projectPath, routeFromPath } from "./router.js";

describe("routeFromPath", () => {
  it("has neither a project nor a photo at the root path", () => {
    expect(routeFromPath("/")).toEqual({ project: null, photo: null });
  });

  it("resolves a project path", () => {
    expect(routeFromPath(`/projects/${encodeURIComponent("düğün 2")}`))
      .toEqual({ project: "düğün 2", photo: null });
  });

  it("does not mistake a photo path for a project name", () => {
    expect(routeFromPath(`/projects/${encodeURIComponent("düğün")}/photos/0_a.png`))
      .toEqual({ project: "düğün", photo: "0_a.png" });
  });

  it("percent-encodes what the path builders produce", () => {
    expect(projectPath("düğün")).toBe(`/projects/${encodeURIComponent("düğün")}`);
    expect(photoPath("düğün", "0_a.png"))
      .toBe(`/projects/${encodeURIComponent("düğün")}/photos/0_a.png`);
  });
});
