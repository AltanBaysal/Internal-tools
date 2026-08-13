# v10 · Görev 1 — Üretim kendi kendine başlamasın (uygulama planı)

**Spec:** [2026-08-13-queen-editor-v10-gorev-1-uretim-kendi-baslamasin-design.md](../specs/2026-08-13-queen-editor-v10-gorev-1-uretim-kendi-baslamasin-design.md)
**Amaç:** Proje açılınca hiçbir üretim başlamasın; yarıda kalan iş Kuyruk panelinde nötr bir
"Duraklatıldı" kartıyla beklesin ve kullanıcının basmasını beklesin.

**Komutlar:** `npm test --prefix queen-editor/frontend -- --run` ·
`npm run build --prefix queen-editor/frontend` · `python -m pytest queen-editor -q`

## Global kısıtlar

- Ön yüz değişiyor → `dist/` aynı commit'te.
- Kullanıcıya görünen metin **Türkçe**, kod ve test adları **İngilizce**.
- Sunucu tarafına dokunulmuyor: bu, ekranın ne zaman istek attığıyla ilgili bir karar, kuralla
  değil. Kuyruğun kendisi ve diskteki hâli aynı kalıyor.
- Görev tek commit; commit mesajında çift tırnak yok.

## Adım 1 — ProjectScreen: iki otomatik başlatma da kalksın

**Dosyalar:** `features/photo_generation/ProjectScreen.test.jsx`, `ProjectScreen.jsx`

- [ ] **1.1 Testleri yaz (kırmızı)** — `ProjectScreen — an open project carries its queue on`
      bloğunu şununla değiştir:

```jsx
describe("ProjectScreen — an open project waits for the user", () => {
  const OWED = [{ id: "0_a", file: "0_a.png", status: "pending", owed: ["photo"], failed: [] }];

  beforeEach(() => {
    vi.useFakeTimers();
    resumeBatch.mockResolvedValue({});
  });
  afterEach(() => vi.useRealTimers());

  async function settle(ms = 0) {
    await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
  }

  it("starts nothing on its own, however many frames are owed", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "idle" });

    renderScreen();
    await settle();
    await settle(10_000);

    expect(resumeBatch).not.toHaveBeenCalled();
  });

  it("leaves a waiting queue where it is even once its producer has landed", async () => {
    listFrames.mockResolvedValue(OWED);
    getStatus.mockResolvedValue({ status: "waiting", project: "düğün", waitingFor: "video" });
    listProducers.mockResolvedValue([
      { id: "video", name: "Video üreticisi", installed: true }]);

    renderScreen();
    await settle();

    expect(resumeBatch).not.toHaveBeenCalled();
  });
});
```

Aynı blokta duran `asks once, not on every poll` ve `waits for the server before it carries any
queue on` testleri silinir: ikisi de sürdürmenin **ne zaman** olacağını sınıyordu, artık hiç
olmuyor.

- [ ] **1.2 Koş, kırmızıyı gör** — `npm test --prefix queen-editor/frontend -- --run`

- [ ] **1.3 `ProjectScreen.jsx`'i sadeleştir** — şunlar gider: `asked` ref'i ve onu kullanan
      `useEffect`, `resumed` state'i ve onu sıfırlayan effect, `readyAgain`'i `resume()`'a bağlayan
      `useEffect`. `known` artık yalnız galeriyi çizmek için duruyorsa `useGeneration`'dan
      alınmaya devam eder; kullanılmıyorsa sökülür.

      `readyAgain` **hesap olarak kalır**, adı `producerReady` olur ve `SidePanel`'e geçer: bekleyen
      kartın devam düğmesi yalnız o doğruyken görünecek.

- [ ] **1.4 Koş, yeşil**

## Adım 2 — QueuePanel: yarıda kalmış iş nötr görünsün

**Dosyalar:** `QueuePanel.test.jsx`, `QueuePanel.jsx`

- [ ] **2.1 Testleri yaz (kırmızı)**:

```jsx
  it("draws an abandoned queue as paused, not as a failure", () => {
    const { container } = renderPanel({ job: { status: "idle", project: "düğün" },
                                        queue: [{ layer: "photo", owed: 2 }] });

    expect(screen.getByText("Duraklatıldı")).toBeTruthy();
    expect(screen.getByText("Kaldığı yerden devam et")).toBeTruthy();
    expect(container.querySelector("[data-run-card]").style.borderColor).not.toBe("var(--danger)");
  });

  it("still draws a run the engine stopped in red", () => {
    const { container } = renderPanel({ job: { status: "error", project: "düğün" },
                                        queue: [{ layer: "photo", owed: 2 }] });

    expect(screen.getByText("Üretim durdu")).toBeTruthy();
    expect(container.querySelector("[data-run-card]").style.borderColor).toBe("var(--danger)");
  });
```

`QueuePanel — a queue that picked itself up` bloğu tamamen silinir: kendi kendine sürdürme kalmadı,
`resumed` prop'u da.

- [ ] **2.2 Koş, kırmızıyı gör**

- [ ] **2.3 `QueuePanel.jsx`** — `state` hesabında `halted || abandoned ? "stopped"` ayrılır:
      `halted ? "stopped" : abandoned ? "paused"`. Düğmeler bugünkü gibi kalır (`paused` →
      "Devam et", `halted || abandoned` → "Kaldığı yerden devam et"), çünkü onlar `state`'e değil
      kendi doğrularına bakıyor. `resumed` prop'u ve onu basan `Note` silinir.

- [ ] **2.4 Koş, yeşil**

## Adım 3 — Bekleyen kart çıkışsız kalmasın

**Dosyalar:** `QueuePanel.test.jsx`, `QueuePanel.jsx`

- [ ] **3.1 Testleri yaz (kırmızı)** — `a queue with nobody to do the work` bloğunda, eski
      "Kurulum bitince kuyruk kendiliğinden sürer." iddiası şunlarla değişir:

```jsx
  it("does not promise to carry itself on any more", () => {
    renderPanel({ job: WAITING, queue: [{ layer: "video", owed: 5 }] });

    expect(screen.queryByText("Kurulum bitince kuyruk kendiliğinden sürer.")).toBeNull();
    expect(screen.queryByText("Kaldığı yerden devam et")).toBeNull();
  });

  it("offers the way on only once the producer is really here", () => {
    const onResume = vi.fn();
    renderPanel({ job: WAITING, queue: [{ layer: "video", owed: 5 }],
                  producerReady: true, onResume });

    fireEvent.click(screen.getByText("Kaldığı yerden devam et"));

    expect(onResume).toHaveBeenCalled();
  });
```

- [ ] **3.2 Koş, kırmızıyı gör**

- [ ] **3.3 `QueuePanel.jsx`** — `producerReady` prop'u eklenir. Bekleyen kartta:
      *"Kurulum bitince kuyruk kendiliğinden sürer."* yerine
      *"Üretici kurulduktan sonra kuyruğu sen sürdürürsün."*; `producerReady` doğruyken
      "Kaldığı yerden devam et" düğmesi, değilken bugünkü "… kur" düğmesi.

- [ ] **3.4 `SidePanel.jsx`** — `resumed` prop'u sökülür, `producerReady` `QueuePanel`'e geçirilir;
      `SidePanel.test.jsx`'te `resumed` kullanan fixture varsa temizlenir.

- [ ] **3.5 Koş, yeşil**

## Adım 4 — Kapanış

- [ ] **4.1** `npm test … --run` ve `python -m pytest queen-editor -q` yeşil.
- [ ] **4.2** `npm run build --prefix queen-editor/frontend`
- [ ] **4.3** `EKSIKLER.md`'den kapanan madde çıkarılır.
- [ ] **4.4 Commit** — kod + testler + `dist/` + spec + plan + EKSIKLER.

## Kendi kontrolüm

- Yarıda kalan iş **kaybolmuyor**: kuyruk diskte duruyor, yalnız kendiliğinden sürmüyor
  ([FOUNDATION 1](../../../queen-editor/FOUNDATION.md)). ✓
- Bekleyen kartın düğmesi tasarıma tek eklenen şey; kullanıcı bunu bilerek onayladı, çünkü
  alternatifi çıkışsız bir kuyruktu. ✓
- `abandoned` kartının rengi değişiyor ama düğmesi değişmiyor: kullanıcı hangi kuyruğu
  duraklattığını, hangisinin yarıda kaldığını düğmenin sözünden ayırt etmeye devam ediyor. ✓
- Sunucuya hiç dokunulmuyor; `resume` ucu ve kuyruk kuralları aynı. ✓
