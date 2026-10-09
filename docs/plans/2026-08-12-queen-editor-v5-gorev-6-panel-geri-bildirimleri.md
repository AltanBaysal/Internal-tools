# Görev 6 — Panel geri bildirimleri ayrışır · Uygulama Planı

> **Çalıştıran ajan için:** GEREKLİ ALT BECERİ: superpowers:executing-plans. Adımlar `- [ ]`
> kutucuklarıyla izlenir.

**Amaç:** Butonun altındaki satır artık iki olayı karıştırmaz — sunucu bir alan adı verdiyse o
alanın cümlesi, vermediyse "Kuyruğa eklenemedi — tekrar dene" yazar; yeşil onay kartı ikiye ayrılır
ve 10 saniye kalır.

**Mimari:** Tek dosya — `GeneratePanel.jsx`. Değişen şey butonun altındaki dal ağacı ve kutunun
altına yazılan metnin uzunluğu.

**Yığın:** React 18 + Vite · vitest + jsdom.

**Spec:** [Görev 6 tasarımı](../specs/2026-08-12-queen-editor-v5-gorev-6-panel-geri-bildirimleri-design.md)

## Global kısıtlar

- **Full TDD:** önce kırmızı test, sonra onu geçiren en küçük kod.
- **Dil ayrımı:** yorum, test adı, commit mesajı **İngilizce**; kullanıcı metni **Türkçe**.
- Sunucunun cümleleri tek doğrudur; ön yüzde metin tablosu tutulmaz.
- Test komutları: `npm test --prefix queen-editor/frontend -- --run` ·
  `python -m pytest queen-editor -q`
- Ön yüze dokunuldu: `npm run build --prefix queen-editor/frontend`, `dist/` aynı commit'te.
- **Tek commit:** görevin sonunda.

---

### Görev 1: Alan hatası kuyruğu suçlamaz

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx:62-78`,
  `:176-188`
- Test: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.test.jsx`

**Arayüzler:**
- Üretir: butonun altındaki satırın kuralı — `errorField` doluysa `error`, boşsa (ve gönderim
  reddedildiyse) "Kuyruğa eklenemedi — tekrar dene".

- [ ] **Adım 1: Testi yaz (kırmızı test)**

`GeneratePanel.test.jsx` — "GeneratePanel — a format error" bloğunun içine:

```jsx
  it("does not blame the queue for a request that never reached it", async () => {
    renderPanel({ error: "Format hatası — liste okunamadı", errorField: "prompts",
                  onGenerate: () => Promise.resolve(null) });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(screen.queryByText("Kuyruğa eklenemedi — tekrar dene")).toBeNull();
    expect(screen.getByText("Format hatası — liste okunamadı")).toBeTruthy();
  });
```

varyant kutusunun testini daralt — iddia "panel susar"dan "kutu temiz kalır"a iner:

```jsx
  it("has no error state of its own, and answers under the button instead", () => {
    renderPanel({ error: "Varyant sayısı 1-26 arası bir tam sayı olmalı.", errorField: "variants" });

    expect(variantBox().style.borderColor).toBe("");
    expect(screen.getByText("Varyant sayısı 1-26 arası bir tam sayı olmalı.")).toBeTruthy();
  });
```

ve "GeneratePanel — the confirmation" bloğundaki reddetme testini yeni metne çevir:

```jsx
  it("says one line when the queue would not take the frames", async () => {
    renderPanel({ onGenerate: () => Promise.resolve(null) });

    fireEvent.click(screen.getByText("Kuyruğa ekle"));

    await waitFor(() => expect(screen.getByText("Kuyruğa eklenemedi — tekrar dene")).toBeTruthy());
    expect(screen.queryByText(/kuyruğa eklendi/)).toBeNull();
  });
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: iki FAIL — yeni metin yok, ve format hatasında kuyruk satırı hâlâ çıkıyor.

- [ ] **Adım 3: Dal ağacını yaz**

`GeneratePanel.jsx` — `promptError` satırının yerine:

```jsx
  // What the server blamed, if it blamed anything. A named field means the request never reached
  // the queue: the answer is that field's own sentence, and saying "Kuyruğa eklenemedi" on top of
  // it would tell one event twice with two different causes.
  const fieldError = errorField ? error : null;
  // Only the prompt box carries a red border; the variant box has none by design.
  const promptError = errorField === "prompts" ? error : null;
```

Butonun altındaki öbek:

```jsx
        {added !== null ? (
          <div className="wf-stroke"
               style={{ padding: "8px 10px", display: "flex", alignItems: "center", gap: 8,
                        borderColor: "var(--ok)", background: "var(--ok-bg)" }}>
            <Note size={12} style={{ color: "var(--ok)" }}>✓ {added} kare kuyruğa eklendi</Note>
          </div>
        ) : fieldError ? (
          <Note size={12} style={{ color: "var(--danger)", textAlign: "center" }}>
            {fieldError}
          </Note>
        ) : refused ? (
          <Note size={12} style={{ color: "var(--danger)", textAlign: "center" }}>
            Kuyruğa eklenemedi — tekrar dene
          </Note>
        ) : busyElsewhere ? (
          <Note size={12} style={{ color: "var(--ink-3)" }}>
            Üretim sürüyor: {job.project} — bitmesini bekle.
          </Note>
        ) : null}
```

`:64`'teki yorum da koda uyar:

```jsx
  // Only the prompt box has an error state; the variant box has none by design, and a refusal the
  // server did not pin on a field is reported as "Kuyruğa eklenemedi".
```

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: PASS.

---

### Görev 2: Yazmak her iki satırı da siler

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx:67-78`
- Test: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.test.jsx`

- [ ] **Adım 1: Testi yaz (kırmızı test)**

"GeneratePanel — the confirmation" bloğuna:

```jsx
  it("takes the refusal back the moment the user starts a new attempt", async () => {
    renderPanel({ onGenerate: () => Promise.resolve(null) });

    fireEvent.click(screen.getByText("Kuyruğa ekle"));
    await waitFor(() => expect(screen.getByText("Kuyruğa eklenemedi — tekrar dene")).toBeTruthy());

    fireEvent.change(promptBox(), { target: { value: '["yeni"]' } });

    expect(screen.queryByText("Kuyruğa eklenemedi — tekrar dene")).toBeNull();
  });
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: FAIL — satır tuşa basıldıktan sonra da duruyor.

- [ ] **Adım 3: Düzenleme iki hatayı da temizlesin**

`GeneratePanel.jsx`:

```jsx
  // Typing is the start of the next attempt: both the field's own error and the queue's refusal
  // belong to the try that just ended.
  function clearAnswers() {
    setRefused(false);
    if (errorField) onClearError();
  }

  function edit(setter) {
    return (e) => {
      setter(e.target.value);
      clearAnswers();
    };
  }

  function editVariants(e) {
    if (!acceptsVariants(e.target.value)) return;
    setVariants(e.target.value);
    clearAnswers();
  }
```

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: PASS.

---

### Görev 3: Kutunun altına cümlenin başı gider

> **Koşu notu (2026-08-12):** Bu adım Görev 1'den ayrılamıyor. Görev 1 alan cümlesini butonun
> altına koyunca aynı metin ekranda iki yerde birden duruyor ve `getByText` çoklu eşleşmeden
> patlıyor — yani Görev 1 tek başına takımı yeşile getirmiyor. Uygulamada ikisi arka arkaya
> koşuldu; sıra Görev 1 → **Görev 3** → Görev 2 → Görev 4 oldu.

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx:128-140`
- Test: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.test.jsx`

- [ ] **Adım 1: Üç testi yaz (kırmızı test)**

"GeneratePanel — a format error" bloğundaki var olan testi yeni davranışa çevir ve iki test ekle:

```jsx
  it("reddens the prompt box and labels it short, with the sentence under the button", () => {
    renderPanel({ error: "Format hatası — liste okunamadı", errorField: "prompts" });

    expect(screen.getByText("Format hatası")).toBeTruthy();
    expect(screen.getByText("Format hatası — liste okunamadı")).toBeTruthy();
    expect(promptBox().style.borderColor).toBe("var(--danger)");
  });

  it("leaves the box wordless when the sentence has no short form", () => {
    renderPanel({ error: "Prompt listesi boş.", errorField: "prompts" });

    expect(screen.getAllByText("Prompt listesi boş.")).toHaveLength(1);
    expect(promptBox().style.borderColor).toBe("var(--danger)");
  });
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: "Format hatası" bulunamıyor; "Prompt listesi boş." iki kez bulunuyor (kutu + buton).

- [ ] **Adım 3: Kısa biçimi yaz**

`GeneratePanel.jsx` — dosya başındaki sabitlerin yanına:

```js
/** The label the red box needs: the head of the server's sentence, or nothing.
 *
 * The server writes a field's message as "<short> — <detail>", so the box takes the head and the
 * full sentence goes under the button. A sentence with no dash has no shorter form: the box then
 * says nothing and only turns red -- writing the same words twice adds nothing.
 */
function boxLabel(message) {
  const cut = message.indexOf(" — ");
  return cut === -1 ? null : message.slice(0, cut);
}
```

`promptError`'ın yanına kısa biçimi de hesapla:

```jsx
  const promptLabel = promptError ? boxLabel(promptError) : null;
```

Prompt kutusunun altı:

```jsx
        {promptLabel && <Note size={12} style={{ color: "var(--danger)" }}>{promptLabel}</Note>}
```

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: PASS.

---

### Görev 4: Yeşil kart iki parça, on saniye

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx:11-12`,
  `:176-181`
- Test: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.test.jsx:148-158`

- [ ] **Adım 1: Testi yaz (kırmızı test)**

"GeneratePanel — the confirmation" bloğundaki ilk testin yerine:

```jsx
  it("quotes the number of frames the server took in its own part of the card", async () => {
    renderPanel({ onGenerate: () => Promise.resolve({ added: 48 }) });

    fireEvent.click(screen.getByText("Kuyruğa ekle"));

    await waitFor(() => expect(screen.getByText("48 kare kuyruğa eklendi")).toBeTruthy());
    expect(screen.getByText("✓")).toBeTruthy();
  });

  it("stays long enough to be read after the eyes have moved on", async () => {
    renderPanel({ onGenerate: () => Promise.resolve({ added: 48 }) });

    fireEvent.click(screen.getByText("Kuyruğa ekle"));
    await waitFor(() => expect(screen.getByText("48 kare kuyruğa eklendi")).toBeTruthy());

    await act(async () => { vi.advanceTimersByTime(4000); });
    expect(screen.getByText("48 kare kuyruğa eklendi")).toBeTruthy();

    await act(async () => { vi.advanceTimersByTime(6000); });
    expect(screen.queryByText("48 kare kuyruğa eklendi")).toBeNull();
  });
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: FAIL — metin hâlâ "✓ 48 kare kuyruğa eklendi" tek parça, ve kart 4 sn'de kayboluyor.

- [ ] **Adım 3: Kartı ikiye ayır, süreyi 10 sn yap**

`GeneratePanel.jsx`:

```js
// Long enough to be read after the eyes have already moved to the gallery, short enough to be gone
// before the next batch is typed. The design named two different numbers; this one is the user's.
const CONFIRM_MS = 10000;
```

```jsx
          <div className="wf-stroke"
               style={{ padding: "8px 10px", display: "flex", alignItems: "center", gap: 8,
                        borderColor: "var(--ok)", background: "var(--ok-bg)" }}>
            {/* Two parts, not one sentence: the mark carries the answer at a glance and does not
                wrap onto the text's second line. */}
            <Note size={12} style={{ color: "var(--ok)" }}>✓</Note>
            <Note size={12} style={{ color: "var(--ok)" }}>{added} kare kuyruğa eklendi</Note>
          </div>
```

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
Beklenen: PASS.

---

### Görev 5: Kapanış

- [ ] **Adım 1: İki takımı da koş**

Koş: `npm test --prefix queen-editor/frontend -- --run` → 14 dosya PASS
Koş: `python -m pytest queen-editor -q` → 371 PASS

- [ ] **Adım 2: Derle**

Koş: `npm run build --prefix queen-editor/frontend`

- [ ] **Adım 3: Tek commit**

```bash
git add -A
git commit -F - <<'MSG'
feat(queen-editor): stop blaming the queue for what never reached it

A request the server turned away at the door was reported as a queue that
would not take the frames -- so a broken prompt list drew two red lines at
once, each naming a different cause. The rule is now a single question: did
the server name a field? If it did, that field's own sentence is the answer,
and the box above it shortens to the head of that sentence rather than
repeating it. If it did not, the queue line stands, and it says what to do.

Both lines now live and die together with the box's red border, so starting a
new attempt clears the last one whole. The confirmation card splits its mark
from its text and stays ten seconds.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
MSG
```

## Öz denetim

**1. Spec kapsaması:** Karar 1 ve 2 → Görev 1; karar 3 → Görev 3; karar 4 → Görev 2; karar 5 →
Görev 4; karar 6 (madde 18, iş yok) → koda dokunmuyor, gerekçe spec'te. Kabul kriterinin beş
maddesi de testlerde.

**2. Yer tutucu taraması:** Yok.

**3. Tür tutarlılığı:** `fieldError` Görev 1'de doğar, Görev 2'nin `clearAnswers`'ı onu besleyen
`errorField`'i temizler; `boxLabel` yalnız Görev 3'te tanımlanıp orada kullanılır; `CONFIRM_MS`
adı değişmez, yalnız değeri.
