import { renderHook, act } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { usePersisted, usePersistedJson } from "./usePersisted.js";

describe("usePersisted", () => {
  it("kayıt yoksa verilen varsayılanı döndürür", () => {
    const { result } = renderHook(() => usePersisted("k", "varsayilan"));
    expect(result.current[0]).toBe("varsayilan");
  });

  it("kayıtlı değeri okur", () => {
    localStorage.setItem("k", "kayitli");
    const { result } = renderHook(() => usePersisted("k", "varsayilan"));
    expect(result.current[0]).toBe("kayitli");
  });

  it("değişince localStorage'a yazar", () => {
    const { result } = renderHook(() => usePersisted("k", ""));
    act(() => result.current[1]("yeni"));
    expect(localStorage.getItem("k")).toBe("yeni");
  });
});

describe("usePersistedJson", () => {
  it("kayıtlı JSON'u çözer", () => {
    localStorage.setItem("liste", JSON.stringify([{ id: 1 }]));
    const { result } = renderHook(() => usePersistedJson("liste", []));
    expect(result.current[0]).toEqual([{ id: 1 }]);
  });

  it("bozuk JSON'da varsayılana düşer, patlamaz", () => {
    localStorage.setItem("liste", "{yarim");
    const { result } = renderHook(() => usePersistedJson("liste", []));
    expect(result.current[0]).toEqual([]);
  });

  it("değişince JSON olarak yazar", () => {
    const { result } = renderHook(() => usePersistedJson("liste", []));
    act(() => result.current[1]([{ id: 7 }]));
    expect(JSON.parse(localStorage.getItem("liste"))).toEqual([{ id: 7 }]);
  });

  it("fonksiyon biçimli güncellemeyi kabul eder", () => {
    const { result } = renderHook(() => usePersistedJson("liste", [1]));
    act(() => result.current[1]((prev) => [...prev, 2]));
    expect(result.current[0]).toEqual([1, 2]);
  });
});
