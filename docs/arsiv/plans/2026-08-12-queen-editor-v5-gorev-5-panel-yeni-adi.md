# Görev 5 — Panel yeni adını alır · Uygulama Planı

> **Çalıştıran ajan için:** GEREKLİ ALT BECERİ: bu planı görev görev uygulamak için
> superpowers:executing-plans. Adımlar `- [ ]` kutucuklarıyla izlenir.

**Amaç:** Fotoğraf paneli yaptığı işi değil ürettiği şeyi söyler — başlık "Fotoğraf üret", buton
"Kuyruğa ekle", şerit ikonu fotoğraf çerçevesi — ve adı tırnak içinde anan iki metin de yeni adı
söyler.

**Mimari:** Yalnız ön yüz. Şeridin ikonları tek dosyaya (`glyphs.jsx`) taşınır çünkü fotoğraf ikonu
artık iki yerde çiziliyor; geri kalan değişiklik dize değişimidir.

**Yığın:** React 18 + Vite · vitest + jsdom.

**Spec:** [Görev 5 tasarımı](../specs/2026-08-12-queen-editor-v5-gorev-5-panel-yeni-adi-design.md)

## Global kısıtlar

- **Full TDD:** hiçbir üretim satırı, önce kırmızı bir test yokken yazılmaz. Var olan bir testin
  beklentisini yeni metne çevirmek de kırmızı testtir — önce çevir, koş, kırmızıyı gör.
- **Dil ayrımı:** yorum, test adı, commit mesajı **İngilizce**; kullanıcının gördüğü metin
  **Türkçe**.
- **Yorum sürüklenmez:** yorum kodun bugününü anlatır; eski adı anan yorum kodla birlikte düzelir.
- **`vendor/` elle düzenlenmez.**
- Test komutları (dizin değiştirmeden, tam takım):
  - ön yüz: `npm test --prefix queen-editor/frontend -- --run`
  - arka uç: `python -m pytest queen-editor -q`
- Ön yüze dokunuldu: `npm run build --prefix queen-editor/frontend` koşulur ve `dist/` **aynı
  commit'te** gider.
- **Tek commit:** görevin tamamı bitince, Adım 5'te.

---

### Görev 1: Panelin adı

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx:60-64`,
  `:105`, `:114`
- Test: `queen-editor/frontend/src/features/photo_generation/SidePanel.test.jsx:35`, `:68`

**Arayüzler:**
- Üretir: şerit paneli kimliği `"photo"` (eski `"add"`), adı `"Fotoğraf üret"` — Görev 4 bu kimlikle
  ikon seçer.

- [ ] **Adım 1: Var olan iki beklentiyi yeni ada çevir (kırmızı test)**

`SidePanel.test.jsx` içinde:

```jsx
  it("opens on the form panel", () => {
    renderColumn();

    expect(screen.getByPlaceholderText(PROMPT_BOX)).toBeTruthy();
    expect(screen.getByLabelText("Fotoğraf üret").getAttribute("aria-current")).toBe("page");
    expect(screen.getByLabelText("Kuyruğu takip et").getAttribute("aria-current")).toBeNull();
  });
```

ve

```jsx
  it("names the open panel above it", () => {
    renderColumn();

    expect(screen.getByRole("heading", { name: "Fotoğraf üret" })).toBeTruthy();

    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    expect(screen.getByRole("heading", { name: "Kuyruğu takip et" })).toBeTruthy();
  });
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: `SidePanel.test.jsx` iki testte FAIL — "Fotoğraf üret" adlı bir öğe yok.

- [ ] **Adım 3: Paneli yeniden adlandır**

`SidePanel.jsx`:

```jsx
// Adding a panel later means adding a row here -- the rail is drawn from this list, not from three
// hard-coded buttons. The id is the layer's own word, so it matches both the glyph's name and what
// the server calls that kind of job.
const PANELS = [
  { id: "photo", title: "Fotoğraf üret" },
  { id: "queue", title: "Kuyruğu takip et" },
  { id: "agent", title: "AI agent" },
];
```

`GLYPH` haritasının anahtarını da aynı sözcüğe çevir (`add:` → `photo:`), açılış durumunu ve panel
seçimini de:

```jsx
  const [open, setOpen] = useState("photo");
```

```jsx
        {open === "photo" && (
```

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: `SidePanel.test.jsx` PASS.

---

### Görev 2: Butonun adı

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx:173`
- Test: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.test.jsx` — "Üretime
  ekle" geçen dokuz satır

- [ ] **Adım 1: Testlerdeki adı çevir (kırmızı test)**

`GeneratePanel.test.jsx` içindeki her `"Üretime ekle"` dizesini `"Kuyruğa ekle"` yap (dokuz yer;
`getByText("Üretime ekle")` ve `getByText("Üretime ekle").closest("button")` kalıplarının ikisi de).
Metin dışında hiçbir şey değişmez — testler aynı davranışı yeni adla sorar.

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: `GeneratePanel.test.jsx` çok sayıda FAIL — "Kuyruğa ekle" metni yok.

- [ ] **Adım 3: Butonun metnini değiştir**

`GeneratePanel.jsx`:

```jsx
          {submitting
            ? <><span className="qe-spinner" aria-hidden="true" /> Ekleniyor…</>
            : <><Icon.Plus /> Kuyruğa ekle</>}
```

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: `GeneratePanel.test.jsx` PASS. (`Icon.Plus` bu adımda duruyor; Görev 4'te fotoğraf
ikonuyla değişecek.)

---

### Görev 3: Adı tırnak içinde anan iki metin

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx:156`
- Değiştir: `queen-editor/frontend/src/features/photo_generation/QueuePanel.jsx:98`
- Test: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx` (yeni test),
  `queen-editor/frontend/src/features/photo_generation/QueuePanel.test.jsx:152`

- [ ] **Adım 1: Boş galeri için testi yaz (kırmızı test)**

`Gallery.test.jsx` içinde `describe("Gallery ordering", …)` bloğundan önce yeni bir blok:

```jsx
describe("Gallery — the empty project", () => {
  it("points at the button by the name the button actually carries", () => {
    renderGallery({ frames: [] });

    expect(screen.getByText("henüz fotoğraf yok")).toBeTruthy();
    expect(screen.getByText(
      "Prompt'ları yaz, Kuyruğa ekle'ye bas — fotoğraflar burada belirecek",
    )).toBeTruthy();
  });
});
```

- [ ] **Adım 2: Boş kuyruk kartının beklentisini çevir (kırmızı test)**

`QueuePanel.test.jsx:152`:

```jsx
    expect(screen.getByText("Fotoğraf üret panelinden kare gönder.")).toBeTruthy();
```

- [ ] **Adım 3: Koş, iki kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: `Gallery.test.jsx` ve `QueuePanel.test.jsx` birer FAIL — ikisi de eski adı buluyor.

- [ ] **Adım 4: İki metni değiştir**

`Gallery.jsx`:

```jsx
        <Note size={13} style={{ color: "var(--ink-3)" }}>
          Prompt'ları yaz, Kuyruğa ekle'ye bas — fotoğraflar burada belirecek
        </Note>
```

`QueuePanel.jsx`:

```jsx
          <Note size={12} style={{ color: "var(--ink-3)" }}>
            Fotoğraf üret panelinden kare gönder.
          </Note>
```

- [ ] **Adım 5: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: 14 dosya PASS.

---

### Görev 4: Fotoğraf ikonu

**Dosyalar:**
- Oluştur: `queen-editor/frontend/src/features/photo_generation/glyphs.jsx`
- Değiştir: `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx:35-56` (yerel
  `GLYPH` tanımı kalkar), `:3-6` (import), `:80`
- Değiştir: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx:4`, `:173`
- Test: `SidePanel.test.jsx`, `GeneratePanel.test.jsx`

**Arayüzler:**
- Üretir: `glyphs.jsx` → `PhotoGlyph`, `QueueGlyph`, `AgentGlyph`; her biri `{ size }` alır
  (varsayılan 16) ve `<svg data-glyph="photo|queue|agent">` çizer.

- [ ] **Adım 1: İki testi yaz (kırmızı test)**

`SidePanel.test.jsx` — "SidePanel — the icon rail" bloğunun sonuna:

```jsx
  it("marks the photo panel with its own layer's glyph, not a plus", () => {
    renderColumn();

    expect(screen.getByLabelText("Fotoğraf üret").querySelector("[data-glyph='photo']"))
      .toBeTruthy();
  });
```

`GeneratePanel.test.jsx` — ilk `describe` bloğunun sonuna:

```jsx
  it("carries the same glyph on the button as the rail carries for this panel", () => {
    renderPanel();

    expect(screen.getByText("Kuyruğa ekle").querySelector("[data-glyph='photo']")).toBeTruthy();
  });
```

`renderPanel` dosyanın kendi yardımcısıdır; adı farklıysa o dosyadaki kalıba uy.

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: iki dosyada birer FAIL — `data-glyph` taşıyan bir öğe yok.

- [ ] **Adım 3: İkon dosyasını yaz**

`queen-editor/frontend/src/features/photo_generation/glyphs.jsx`:

```jsx
// The design names the rail's icons but never draws them: it says a photo frame, a video camera, a
// wave. They are drawn here in the kit's own language -- 14x14 box, currentColor, 1.5 rounded
// stroke -- and not in vendor/, which is a verbatim copy of the design's own files.
//
// data-glyph is the icon's identity. Which glyph got drawn is otherwise unreadable from the DOM,
// and the photo panel draws the same one twice -- on the rail and on its button -- so that sameness
// has to be something a test can hold on to.
function Glyph({ name, size = 16, children }) {
  return (
    <svg data-glyph={name} width={size} height={size} viewBox="0 0 14 14" fill="none"
         aria-hidden="true">
      {children}
    </svg>
  );
}

// A framed picture: the frame, a sun in its corner, a hill line across it.
export const PhotoGlyph = ({ size }) => (
  <Glyph name="photo" size={size}>
    <rect x="1.75" y="2.75" width="10.5" height="8.5" rx="1.5"
          stroke="currentColor" strokeWidth="1.4" />
    <circle cx="4.9" cy="5.6" r=".95" stroke="currentColor" strokeWidth="1.2" />
    <path d="M2.4 9.9 5.4 7l1.9 1.8L9.1 7.4l2.5 2.5" stroke="currentColor" strokeWidth="1.4"
          strokeLinecap="round" strokeLinejoin="round" />
  </Glyph>
);

export const QueueGlyph = ({ size }) => (
  <Glyph name="queue" size={size}>
    <path d="M2 4h10M2 7h10M2 10h6" stroke="currentColor" strokeWidth="1.5"
          strokeLinecap="round" />
  </Glyph>
);

export const AgentGlyph = ({ size }) => (
  <Glyph name="agent" size={size}>
    <path d="M2 4.5A1.5 1.5 0 0 1 3.5 3h7A1.5 1.5 0 0 1 12 4.5v4A1.5 1.5 0 0 1 10.5 10H6l-3 2V10
             A1 1 0 0 1 2 9V4.5z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
  </Glyph>
);
```

- [ ] **Adım 4: Şeridi bu dosyaya bağla**

`SidePanel.jsx` — yerel `GLYPH` bloğunu ve üstündeki yorumu sil, yerine import ve harita:

```jsx
import { Mono } from "../../vendor/kit.jsx";
import AgentPanel from "./AgentPanel.jsx";
import GeneratePanel from "./GeneratePanel.jsx";
import { AgentGlyph, PhotoGlyph, QueueGlyph } from "./glyphs.jsx";
import QueuePanel from "./QueuePanel.jsx";
```

```jsx
// Which panel gets which icon. The drawings live in glyphs.jsx, because the photo one is also the
// icon its own submit button carries.
const GLYPH = { photo: PhotoGlyph, queue: QueueGlyph, agent: AgentGlyph };
```

- [ ] **Adım 5: Butona aynı ikonu koy**

`GeneratePanel.jsx` — kit import'undan `Icon` düşer (başka kullanıcısı yok):

```jsx
import { Mono, Note } from "../../vendor/kit.jsx";
import { PhotoGlyph } from "./glyphs.jsx";
```

```jsx
          {submitting
            ? <><span className="qe-spinner" aria-hidden="true" /> Ekleniyor…</>
            : <><PhotoGlyph size={14} /> Kuyruğa ekle</>}
```

- [ ] **Adım 6: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: 14 dosya PASS.

---

### Görev 5: Kapanış

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx:57` (yorum)

- [ ] **Adım 1: Eski adı anan yorumu düzelt**

`ProjectScreen.jsx`:

```jsx
  // Pressing Kuyruğa ekle persists the panel first, whether or not the frames are accepted -- text
```

- [ ] **Adım 2: Eski adın kalmadığını doğrula**

`queen-editor/frontend/src` altında `Üretime ekle` aranır; sonuç boş olmalı.

- [ ] **Adım 3: İki takımı da koş**

Koş: `npm test --prefix queen-editor/frontend -- --run` → 14 dosya PASS
Koş: `python -m pytest queen-editor -q` → 371 PASS (arka uca dokunulmadı, sayı düşmemeli)

- [ ] **Adım 4: Derle**

Koş: `npm run build --prefix queen-editor/frontend`
Beklenen: `dist/` yeniden üretilir.

- [ ] **Adım 5: Tek commit**

Spec, plan, kaynak, testler ve `dist/` birlikte gider.

```bash
git add -A
git commit -F - <<'MSG'
feat(queen-editor): the panel says what it makes, not what it does

The right-hand panel was named after the act of submitting. That works while
there is one of it; the moment video and audio panels stand beside it, three
panels all named after the same act tell the rail nothing. So the panel takes
the name of what it produces, and the button keeps the act -- one label the
other two panels will share, told apart by the layer's own icon in front of it.

The two places that quoted the old name follow it, and the plus on the rail
becomes the picture frame the design asks for -- the same glyph the button now
carries, so the button and its panel are visibly the same thing.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
MSG
```

## Öz denetim

**1. Spec kapsaması:** Spec'in altı kararı da bir göreve düşüyor — 1 ve 2 (ad, büyük harf) Görev 1;
3 (madde 42) Görev 3; 4 ve 5 ve 7 (buton ikonu, ikon dosyası, `data-glyph`) Görev 4; 6 (panel
kimliği) Görev 1. Kabul kriterinin beş maddesi de test edilmiş ya da Görev 5'te doğrulanıyor.

**2. Yer tutucu taraması:** Yok — her adımda çalışacak kod var.

**3. Tür tutarlılığı:** `PhotoGlyph` / `QueueGlyph` / `AgentGlyph` adları Görev 4'ün üç yerinde de
aynı; `data-glyph` değerleri (`photo` · `queue` · `agent`) panel kimlikleriyle birebir; panel
kimliği `photo` Görev 1'de tanımlanıp Görev 4'te kullanılıyor.
