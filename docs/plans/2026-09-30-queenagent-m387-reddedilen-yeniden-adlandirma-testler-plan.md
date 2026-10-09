# Madde 387 — Reddedilen yeniden adlandırma · test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Amaç:** Reddedilen yeniden adlandırmada satırın yazılan adı tutmasını isteyen testleri yazmak ve
kırmızı görmek. Yalnız test; kaynak koda dokunulmaz.

**Mimari:** `ProjectRow.test.jsx` satırı sahte bir `onRename`'le sınar (söz: kabulde truthy, redde
`null`); `App.test.jsx` gerçek `useProjects`'i ilk yazmayı reddeden sahte sunucuyla
(`refusingFirstWrite`) sınar.

**Teknoloji:** vitest + jsdom + Testing Library.

**Spec:** `docs/specs/2026-09-30-queenagent-m387-reddedilen-yeniden-adlandirma-testler-design.md`

## Genel kısıtlar

- Test adları ve yorumlar İngilizce; `skip`/`todo` yok.
- Suite yalnız CLAUDE.md'nin dört satırıyla, olduğu gibi, paralel koşar.

---

### Görev 1: `ProjectRow.test.jsx`

**Dosya:** `queen-agent/frontend/src/features/workspace/ProjectRow.test.jsx`

- [ ] **Adım 1:** İçe aktarmaya `act` eklenir: `import { act, fireEvent, render, screen } from "@testing-library/react";`
- [ ] **Adım 2:** "Enter saves what was typed, once, and closes the field" şöyle olur — `onRename`
  kabulle çözülür, iki Enter tek çağrı, alan cevaptan sonra kapanır:

```jsx
test("Enter saves what was typed, once, and closes the field once it has landed", async () => {
  const onRename = vi.fn().mockResolvedValue(PROJECT);
  const field = renaming({ onRename });
  fireEvent.change(field, { target: { value: "  Harbour  " } });
  await act(async () => {
    fireEvent.keyDown(field, { key: "Enter" });
    // A second press while the first is on its way is not a second rename.
    fireEvent.keyDown(field, { key: "Enter" });
  });
  expect(onRename).toHaveBeenCalledTimes(1);
  expect(onRename).toHaveBeenCalledWith("p2", "Harbour");
  expect(screen.queryByRole("textbox", { name: "Project name" })).toBeNull();
  expect(document.querySelector(".all-projects__row-open")).toBeTruthy();
});
```

- [ ] **Adım 3:** Blur testi kabulle çözülen `onRename`'le, `await act(async () => fireEvent.blur(field))`.
- [ ] **Adım 4:** Yeni testler:

```jsx
test("the field holds the name while it is on its way", () => {
  const field = renaming({ onRename: vi.fn(() => new Promise(() => {})) });
  fireEvent.change(field, { target: { value: "Harbour" } });
  fireEvent.keyDown(field, { key: "Enter" });
  expect(screen.getByRole("textbox", { name: "Project name" }).value).toBe("Harbour");
});

test("a refused name stays in the field, ready to send again", async () => {
  const onRename = vi.fn().mockResolvedValueOnce(null).mockResolvedValueOnce(PROJECT);
  const field = renaming({ onRename });
  fireEvent.change(field, { target: { value: "Harbour" } });
  await act(async () => {
    fireEvent.keyDown(field, { key: "Enter" });
  });
  const kept = screen.getByRole("textbox", { name: "Project name" });
  expect(kept.value).toBe("Harbour");
  expect(document.activeElement).toBe(kept);
  await act(async () => {
    fireEvent.keyDown(kept, { key: "Enter" });
  });
  expect(onRename).toHaveBeenCalledTimes(2);
  expect(onRename).toHaveBeenLastCalledWith("p2", "Harbour");
  expect(screen.queryByRole("textbox", { name: "Project name" })).toBeNull();
});

test("Escape after a refusal gives the name up", async () => {
  const onRename = vi.fn().mockResolvedValue(null);
  const field = renaming({ onRename });
  fireEvent.change(field, { target: { value: "Harbour" } });
  await act(async () => {
    fireEvent.keyDown(field, { key: "Enter" });
  });
  fireEvent.keyDown(screen.getByRole("textbox", { name: "Project name" }), { key: "Escape" });
  expect(onRename).toHaveBeenCalledTimes(1);
  expect(screen.queryByRole("textbox", { name: "Project name" })).toBeNull();
  expect(screen.getByText("Night market")).toBeTruthy();
});
```

### Görev 2: `App.test.jsx`

**Dosya:** `queen-agent/frontend/src/App.test.jsx`, Madde 364 bölümü.

- [ ] **Adım 1:** "a rename the server refuses leaves All projects standing…" şöyle olur:

```jsx
test("a rename the server refuses keeps the typed name in the row, with the server's words", async () => {
  refusingFirstWrite(ROWS);
  const { container } = render(<App />);
  await onAllProjects();
  renameTo("Thesis", "Dissertation");
  expect((await screen.findByText("the store is unreachable")).className).toBe("list-error");
  expect(screen.getByRole("textbox", { name: "Project name" }).value).toBe("Dissertation");
  // Thesis's row holds the field, so only Notes reads as a name; the list is still standing.
  expect(sections(container)).toEqual({ Recent: ["Notes"] });
  expect(screen.queryByText("Couldn't load projects.")).toBeNull();
});
```

- [ ] **Adım 2:** Yeni test:

```jsx
test("Enter again sends the kept name, and once it lands the row and the line follow", async () => {
  const fetch = refusingFirstWrite(ROWS);
  render(<App />);
  await onAllProjects();
  renameTo("Thesis", "Dissertation");
  await screen.findByText("the store is unreachable");
  fireEvent.keyDown(screen.getByRole("textbox", { name: "Project name" }), { key: "Enter" });
  expect(
    await screen.findByText("Dissertation", { selector: ".all-projects__row-name" }),
  ).toBeTruthy();
  expect(screen.queryByText("the store is unreachable")).toBeNull();
  expect(patches(fetch).map(([path, options]) => [path, JSON.parse(options.body)])).toEqual([
    ["/api/projects/p1", { name: "Dissertation" }],
    ["/api/projects/p1", { name: "Dissertation" }],
  ]);
});
```

- [ ] **Adım 3:** "the next write that lands takes the refusal's line away" testinde, reddden sonra
  Pin'den önce vazgeçilir:
  `fireEvent.keyDown(screen.getByRole("textbox", { name: "Project name" }), { key: "Escape" });`

### Görev 3: Kırmızı

- [ ] Dört satır paralel koşar. Beklenen: ProjectRow'da "holds the name while it is on its way",
  "a refused name stays…", "Escape after a refusal…"; App'te "keeps the typed name…", "Enter again…",
  "the next write…" kırmızı; geri kalan her şey yeşil.
- [ ] Commit: `test(queen-agent): Madde 387 red -- a refused rename keeps the typed name`
