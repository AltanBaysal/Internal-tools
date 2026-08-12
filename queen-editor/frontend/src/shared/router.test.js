import { describe, expect, it } from "vitest";

import { exportPath, photoPath, projectPath, routeFromPath } from "./router.js";

describe("routeFromPath", () => {
  it("has neither a project nor a frame at the root path", () => {
    expect(routeFromPath("/")).toEqual({ project: null, photo: null, exporting: false });
  });

  it("resolves a project path", () => {
    expect(routeFromPath(`/projects/${encodeURIComponent("düğün 2")}`))
      .toEqual({ project: "düğün 2", photo: null, exporting: false });
  });

  it("does not mistake a frame path for a project name", () => {
    expect(routeFromPath(`/projects/${encodeURIComponent("düğün")}/photos/P0_1`))
      .toEqual({ project: "düğün", photo: "P0_1", exporting: false });
  });

  it("reads the export screen's own path", () => {
    expect(routeFromPath(`/projects/${encodeURIComponent("düğün")}/export`))
      .toEqual({ project: "düğün", photo: null, exporting: true });
  });

  it("percent-encodes what the path builders produce", () => {
    expect(projectPath("düğün")).toBe(`/projects/${encodeURIComponent("düğün")}`);
    expect(photoPath("düğün", "P0_1"))
      .toBe(`/projects/${encodeURIComponent("düğün")}/photos/P0_1`);
    expect(exportPath("düğün")).toBe(`/projects/${encodeURIComponent("düğün")}/export`);
  });
});
