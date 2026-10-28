# Madde 80 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-26-queenagent-m80-gonder-durdur-ikona-doner-testler-design.md](../specs/2026-08-26-queenagent-m80-gonder-durdur-ikona-doner-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

**İki işaret, her yerde aynı:** gönderme `↑` (U+2191), durdurma `⏹` (U+23F9).

---

## Sıra

### 1. `Composer.test.jsx` — dört yeni test

Dosyanın sonuna, 79'un bölümünün altına, kendi başlığıyla:

```jsx
// --- kelime yerine işaret (Madde 80) -------------------------------------------------------------
//
// Düğmenin ne yaptığı değişmiyor; üstünde ne yazdığı değişiyor. Ad `aria-label`e taşınıyor, yani
// görünmez oluyor -- yok olmuyor. Bunun kanıtı bu dosyanın geri kalanı: her testi düğmeyi
// `{ name: "Send" }` ile buluyor.

test("the button carries an arrow, not the word", () => {
  const { button } = draw();
  expect(button.textContent).toBe("↑");
});

test("hovering says what the arrow does", () => {
  // Bir işaretin kendini açıklaması gerekir, ve fare bunu soracak tek yer.
  expect(draw().button.getAttribute("title")).toBe("Send");
});

test("while an answer runs the arrow becomes a stop", () => {
  render(<Composer action="Send" running onStop={vi.fn()} />);
  const button = screen.getByRole("button", { name: "Stop" });
  expect(button.textContent).toBe("⏹");
  expect(button.getAttribute("title")).toBe("Stop");
});

test("the project screen's button is the same arrow under another name", () => {
  // İkisi de "yazdığımı gönder" demek, o yüzden işaret aynı. Ayrılan şey ad.
  render(<Composer action="Start" placeholder="Start a new chat in this project..." />);
  const button = screen.getByRole("button", { name: "Start" });
  expect(button.textContent).toBe("↑");
});
```

Bugün dördü de kırmızı: metin `Send` / `Stop` / `Start` geliyor, `title` yok.

### 2. `Composer.test.jsx` — ayaktaki sıra testi güncellenir

`the foot has room to the left of Send` testinin beklentisi:

```jsx
expect(buttons.map((button) => button.textContent)).toEqual(["Grok 4.5", "↑"]);
```

Adı da yerinde tutan bir satır ekleniyor, çünkü metin artık kimliği söylemiyor:

```jsx
expect(buttons[1].getAttribute("aria-label")).toBe("Send");
```

### 3. `ChatScreen.test.jsx` — iki sıra testi güncellenir

`the foot carries Skills, the model and Send, in that order`:

```jsx
expect(buttons.map((button) => button.textContent)).toEqual(["Skills⌄", "Grok 4.6⌄", "↑"]);
expect(buttons[2].getAttribute("aria-label")).toBe("Send");
```

`while an answer runs the row ends in Stop, and there is no fourth button`:

```jsx
expect(buttons.map((button) => button.textContent)).toEqual(["Skills⌄", "Grok 4.6⌄", "⏹"]);
expect(buttons[2].getAttribute("aria-label")).toBe("Stop");
```

Testin adındaki *Send* / *Stop* duruyor — ad hâlâ o, yalnız artık `aria-label`de.

### 4. `ProjectScreen.test.jsx` — bir sıra testi güncellenir

```jsx
expect(buttons.map((button) => button.textContent)).toEqual(["Skills⌄", "Grok 4.6⌄", "↑"]);
expect(buttons[2].getAttribute("aria-label")).toBe("Start");
```

### 5. `workspace.css.test.js` — bir yeni test

`the extension chip is a fixed square` testinin hemen üstüne, aynı kalıpla:

```js
test("the send button is a fixed square", () => {
  // Kelime kadar geniş olmayı bırakıyor: içinde tek bir işaret var ve iki işaret aynı yeri
  // kaplamalı, yoksa düğme akan cevapla birlikte genişleyip daralır.
  const send = rule(".composer__send");
  expect(send).toContain("width: 32px");
  expect(send).toContain("height: 32px");
});
```

`rule()` bu dosyada zaten var *(55. satır)* ve `\n.composer__send {` ile başlayan bloğu okuyor.

## Toplu değiştirme yok

Beklenti satırları birbirine benziyor: dört dosyada `buttons.map(...)` var ve üçünün beklediği dizi
neredeyse aynı. **`replace_all` kullanılmıyor**, her biri kendi çevresiyle tek tek düzeltiliyor —
77'de aynı görünen on bir satırdan ikisi değiştirilmek istenmiş, on biri birden değişmiş ve dokuz
sahte kırmızı çıkmıştı.

## Beklenen kırmızı

Ön yüzde **9 failed, 498 passed** — beş yeni testle toplam 507:

| Nerede | Kaç |
|---|---|
| `Composer.test.jsx` — yeni | 4 |
| `Composer.test.jsx` — güncellenen | 1 |
| `ChatScreen.test.jsx` — güncellenen | 2 |
| `ProjectScreen.test.jsx` — güncellenen | 1 |
| `workspace.css.test.js` — yeni | 1 |

Arka uçta **2 failed, 442 passed** — ikisi defterin dalı, bu maddeyle ilgisi yok.

**Kırmızının okunabilir olması şart.** `container.querySelector(...).textContent` yolu, eleman
yoksa `TypeError` veriyor ve testin ne beklediğini gizliyor; 68 ile 78'de iki kez oldu. Burada
`screen.getByRole(...)` kullanılıyor — bulunamayınca ne aradığını söyleyerek düşüyor.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `Composer.jsx`, `ChatScreen.jsx`, `workspace.css` bu turda açılmıyor.
- **`dist` derlenmez.** Kaynak değişmiyor.
- **Ad testleri yazılmaz.** Adın durduğunu zaten on iki eski test kanıtlıyor; onları
  tekrarlamak, düşmesi gereken yerde iki kez düşmek olurdu.
- **Başka düğmeye dokunulmaz.** `Try again`, `New chat`, onay kutusu — hepsi kelime kalıyor.
