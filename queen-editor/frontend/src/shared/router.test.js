import { describe, expect, it } from "vitest";

import { photoPath, projectPath, routeFromPath } from "./router.js";

describe("routeFromPath", () => {
  it("kök yolda ne proje ne fotoğraf vardır", () => {
    expect(routeFromPath("/")).toEqual({ project: null, photo: null });
  });

  it("proje yolunu çözer", () => {
    expect(routeFromPath(`/projects/${encodeURIComponent("düğün 2")}`))
      .toEqual({ project: "düğün 2", photo: null });
  });

  it("fotoğraf yolunu proje adı sanmaz", () => {
    expect(routeFromPath(`/projects/${encodeURIComponent("düğün")}/photos/0_a.png`))
      .toEqual({ project: "düğün", photo: "0_a.png" });
  });

  it("yol üreteçleri kodlar", () => {
    expect(projectPath("düğün")).toBe(`/projects/${encodeURIComponent("düğün")}`);
    expect(photoPath("düğün", "0_a.png"))
      .toBe(`/projects/${encodeURIComponent("düğün")}/photos/0_a.png`);
  });
});
