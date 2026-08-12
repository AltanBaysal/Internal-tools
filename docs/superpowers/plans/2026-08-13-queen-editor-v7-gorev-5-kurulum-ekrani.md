# Görev 5 — Kurulum ekranı doğruyu söylesin (uygulama planı)

**Spec:** [Görev 5](../specs/2026-08-13-queen-editor-v7-gorev-5-kurulum-ekrani-design.md) ·
**Roadmap:** [v7](2026-08-13-queen-editor-v7-roadmap.md) · Blok 2

**Amaç:** Satır yalnız koşan bir kurulumu koşuyor göstersin, biten koşu kartı bıraksın, patlayan
koşu hatasını göstersin; çubuk kalksın, yerine inen dosyanın adı gelsin; Kur'a basınca tepki anında
olsun.

**Sıra:** Önce sunucu (satırın ne dediği), sonra ön yüz (nasıl çizildiği ve iyimser durum).

## Global kısıtlar

- Kod, yorum, docstring ve test adları **İngilizce**; kullanıcıya görünen metin Türkçe.
- Kural sunucuda: satırın ne söylediğine ekran karar vermez.
- Ön yüz değişiyor → `npm run build` ve `dist/` **aynı commit'te**.
- Görev sonunda **tek commit**.

## Dosyalar

- **Değiştir:** `queen-editor/backend/features/producers/domain/usecases/list_producers.py`
- **Değiştir:** `queen-editor/backend/tests/test_producers.py`
- **Değiştir:** `queen-editor/frontend/src/features/producers/InstallCard.jsx` (+ testi)
- **Değiştir:** `queen-editor/frontend/src/features/producers/ProducersPanel.jsx` (+ testi)
- **Değiştir:** `queen-editor/frontend/src/features/producers/useProducers.js`
- **Oluştur:** `queen-editor/frontend/src/features/producers/useProducers.test.jsx`

---

### Adım 1 — Sunucunun testlerini yaz

`test_producers.py` içinde `test_the_running_install_is_reported_on_its_own_row`'u yenile ve iki
test ekle:

```python
def test_the_running_install_is_reported_on_its_own_row():
    rows = list_producers(GROUPS, FakeFiles(),
                          running={"status": "running", "kind": "video",
                                   "file": "wan.safetensors"})

    # The file being fetched, and nothing else: a percentage that restarts per file was movement
    # rather than information.
    assert rows[1]["installing"] == {"file": "wan.safetensors"}
    assert "installing" not in rows[0]


def test_a_finished_install_leaves_no_row_claiming_to_be_running():
    rows = list_producers(GROUPS, FakeFiles(),
                          running={"status": "done", "kind": "video"})

    assert all("installing" not in row for row in rows)


def test_a_failed_install_shows_its_own_words_instead_of_running_forever():
    rows = list_producers(GROUPS, FakeFiles(),
                          running={"status": "error", "kind": "video",
                                   "error": "bağlantı yok"})

    assert "installing" not in rows[1]
    assert rows[1]["error"] == "bağlantı yok"
```

### Adım 2 — Koş, kırmızı olduğunu gör

`python -m pytest queen-editor -q` → **FAIL**: satır durumdan bağımsız `installing` taşıyor.

### Adım 3 — Satırı düzelt

`list_producers.py`:

```python
def list_producers(groups, files, running=None):
    rows = []
    for kind in ORDER:
        group = groups.get(kind) or []
        installed = bool(group) and all(
            files.exists(spec["folder"], spec["name"]) for spec in group)
        row = {"id": kind, "name": NAMES[kind], "installed": installed}
        if running and running.get("kind") == kind:
            # Only a run that is actually running: the worker keeps its last state after it
            # finishes, and reporting that as progress left the card saying "kuruluyor" for good.
            if running.get("status") == "running":
                row["installing"] = {"file": running.get("file")}
            elif running.get("status") == "error":
                row["error"] = running.get("error")
        rows.append(row)
    return rows
```

Modül docstring'ine bir paragraf: satır üç şey söyleyebilir — kurulu, kuruluyor (ve ne iniyor),
ya da son denemenin hatası.

### Adım 4 — Koş, yeşil olduğunu gör

`python -m pytest queen-editor -q` → **PASS**.

### Adım 5 — Ön yüzün testlerini yaz

`InstallCard.test.jsx`:

```jsx
  it("says what is coming down while the download runs", () => {
    render(<InstallCard producer={{ ...MISSING, installing: { file: "wan.safetensors" } }}
                        onInstall={() => {}} />);

    expect(screen.getByText("kuruluyor… wan.safetensors")).toBeTruthy();
    expect(screen.queryByText("Kur")).toBeNull();
  });

  it("draws no progress bar at all", () => {
    const { container } = render(
      <InstallCard producer={{ ...MISSING, installing: { file: "wan.safetensors" } }}
                   onInstall={() => {}} />);

    expect(container.querySelector("[data-bar]")).toBeNull();
  });

  it("shows the failure of the last attempt next to a fresh Kur", () => {
    render(<InstallCard producer={{ ...MISSING, error: "bağlantı yok" }} onInstall={() => {}} />);

    expect(screen.getByText("bağlantı yok")).toBeTruthy();
    expect(screen.getByText("Kur")).toBeTruthy();
  });
```

(eski `turns into progress while the download runs` testi ilkinin yerine geçer)

`ProducersPanel.test.jsx`: `INSTALLING` fixture'ı `{ file: "wan.safetensors" }` olsun,
"shows how far the running install has got" testi inen dosyayı beklesin, ve bir test eklensin:

```jsx
  it("shows a failed install with the server's own words and a way to try again", () => {
    renderPanel({ producers: THREE.map((producer) => (producer.id === "video"
      ? { ...producer, error: "bağlantı yok" } : producer)) });

    expect(screen.getByText("bağlantı yok")).toBeTruthy();
    expect(screen.getAllByText("Kur")).toHaveLength(2);
  });
```

`useProducers.test.jsx` (yeni):

```jsx
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { installProducer, listProducers } from "../../shared/api.js";
import { useProducers } from "./useProducers.js";

vi.mock("../../shared/api.js", () => ({
  cancelInstall: vi.fn(),
  installProducer: vi.fn(),
  listProducers: vi.fn(),
}));

const THREE = [
  { id: "photo", name: "Fotoğraf üreticisi", installed: true },
  { id: "video", name: "Video üreticisi", installed: false },
];

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

beforeEach(() => {
  vi.clearAllMocks();
  listProducers.mockResolvedValue(THREE);
});

describe("useProducers", () => {
  it("says the install started before the server has answered", async () => {
    // Two round-trips separate the click from any change on screen otherwise, and the user
    // presses Kur again.
    installProducer.mockReturnValue(new Promise(() => {}));
    const { result } = renderHook(() => useProducers());
    await settle();

    act(() => { result.current.install("video"); });

    expect(result.current.producers[1].installing).toBeTruthy();
  });

  it("takes that back when the request is refused", async () => {
    installProducer.mockRejectedValue(new Error("Video üreticisi zaten kuruluyor."));
    const { result } = renderHook(() => useProducers());
    await settle();

    await act(async () => { await result.current.install("video"); });

    expect(result.current.producers[1].installing).toBeFalsy();
    expect(result.current.error).toBe("Video üreticisi zaten kuruluyor.");
  });
});
```

### Adım 6 — Koş, kırmızı olduğunu gör

`npm test --prefix queen-editor/frontend -- --run` → **FAIL**.

### Adım 7 — Ön yüzü yaz

`InstallCard.jsx`: `Bar` ve `TRACK` silinir, `export { Bar }` kalkar. Kuruluyor satırı
`kuruluyor… {producer.installing.file}` der (dosya adı yoksa yalnız `kuruluyor…`). Kur'un üstünde,
`producer.error` varsa, sunucunun cümlesi görünür.

`ProducersPanel.jsx`: `Bar` importu ve kullanımı kalkar; kuruluyor satırı aynı cümleyi kurar;
kurulu da kuruluyor da değilse ve `producer.error` varsa hata metni Kur'un üstünde görünür.

`useProducers.js`: `install` iyimser davranır ve reddedilirse geri alır.

### Adım 8 — Tam takım + derleme

```
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend -- --run
npm run build --prefix queen-editor/frontend
```

### Adım 9 — Commit

```bash
git add queen-editor docs/superpowers
git commit -m "fix(queen-editor): the install row says what is actually happening"
```
