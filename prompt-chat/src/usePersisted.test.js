import { renderHook, act } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { usePersisted, usePersistedJson } from "./usePersisted.js";

describe("usePersisted", () => {
  it("returns the given fallback when nothing is stored", () => {
    const { result } = renderHook(() => usePersisted("k", "varsayilan"));
    expect(result.current[0]).toBe("varsayilan");
  });

  it("reads the stored value", () => {
    localStorage.setItem("k", "kayitli");
    const { result } = renderHook(() => usePersisted("k", "varsayilan"));
    expect(result.current[0]).toBe("kayitli");
  });

  it("writes to localStorage on change", () => {
    const { result } = renderHook(() => usePersisted("k", ""));
    act(() => result.current[1]("yeni"));
    expect(localStorage.getItem("k")).toBe("yeni");
  });
});

describe("usePersistedJson", () => {
  it("parses stored JSON", () => {
    localStorage.setItem("liste", JSON.stringify([{ id: 1 }]));
    const { result } = renderHook(() => usePersistedJson("liste", []));
    expect(result.current[0]).toEqual([{ id: 1 }]);
  });

  it("falls back on corrupt JSON instead of throwing", () => {
    localStorage.setItem("liste", "{yarim");
    const { result } = renderHook(() => usePersistedJson("liste", []));
    expect(result.current[0]).toEqual([]);
  });

  it("writes JSON on change", () => {
    const { result } = renderHook(() => usePersistedJson("liste", []));
    act(() => result.current[1]([{ id: 7 }]));
    expect(JSON.parse(localStorage.getItem("liste"))).toEqual([{ id: 7 }]);
  });

  it("accepts a functional update", () => {
    const { result } = renderHook(() => usePersistedJson("liste", [1]));
    act(() => result.current[1]((prev) => [...prev, 2]));
    expect(result.current[0]).toEqual([1, 2]);
  });
});
