# Görev 9 — Yan barda açık ikona basınca panel kapansın (uygulama planı)

**Spec:** [Görev 9](../specs/2026-08-13-queen-editor-v7-gorev-9-yan-bar-kapansin-design.md) ·
**Roadmap:** [v7](2026-08-13-queen-editor-v7-roadmap.md) · Blok 4

**Amaç:** Aynı ikon aç/kapa olsun; kapalıyken panel hiç çizilmesin.

## Global kısıtlar

- Kod, yorum ve test adları **İngilizce**; UI metni Türkçe.
- Ön yüz değişiyor → `npm run build` ve `dist/` **aynı commit'te**.
- Görev sonunda **tek commit**.

## Dosyalar

- **Değiştir:** `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx` (+ testi)

---

### Adım 1 — Testleri yaz

`SidePanel.test.jsx`, şerit describe'ının içine:

```jsx
  it("closes the open panel when its own icon is pressed again", () => {
    renderPanel();

    fireEvent.click(screen.getByLabelText("Fotoğraf üret"));

    expect(screen.queryByText("Fotoğraf üret", { selector: "h2 *" })).toBeNull();
    expect(screen.getByLabelText("Fotoğraf üret")).toBeTruthy();      // the rail stays
  });

  it("opens it again on the next press", () => {
    renderPanel();

    fireEvent.click(screen.getByLabelText("Fotoğraf üret"));
    fireEvent.click(screen.getByLabelText("Fotoğraf üret"));

    expect(screen.getByLabelText("Fotoğraf üret").getAttribute("aria-current")).toBe("page");
  });

  it("marks no icon as open while the panel is closed", () => {
    renderPanel();

    fireEvent.click(screen.getByLabelText("Fotoğraf üret"));

    expect(document.querySelectorAll("[aria-current='page']")).toHaveLength(0);
  });
```

(Testteki `renderPanel` bu dosyanın kendi yardımcısı; adı farklıysa mevcut olanı kullan.)

### Adım 2 — Koş, kırmızı olduğunu gör

`npm test --prefix queen-editor/frontend -- --run` → **FAIL**.

### Adım 3 — Aç/kapa yaz

`SidePanel.jsx`:

```jsx
  // Which panel is open is this column's own business: neither the project screen nor the server
  // has a reason to know it. null means none -- pressing the open panel's own icon closes it and
  // gives the width back to the gallery, the way a code editor's side bar behaves.
  const [open, setOpen] = useState("photo");
  const toggle = (id) => setOpen((shown) => (shown === id ? null : id));
  const current = PANELS.find((panel) => panel.id === open);
```

Panel sarmalayıcısı `{current && ( … )}` içine alınır; şerit `onSelect={toggle}` alır.

### Adım 4 — Koş, derle, commit

```
npm test --prefix queen-editor/frontend -- --run
npm run build --prefix queen-editor/frontend
git add queen-editor docs/superpowers
git commit -m "feat(queen-editor): the open panel's own icon closes it"
```
