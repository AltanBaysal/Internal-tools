# Madde 83 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-26-queenagent-m83-damga-mesajin-altina-iner-uygulama-design.md](../specs/2026-08-26-queenagent-m83-damga-mesajin-altina-iner-uygulama-design.md)
**Testler:** commit `5e46002` — **11 kırmızı**, ikisi stil kilidinde.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

**İki dosya:** `ChatScreen.jsx` ve `workspace.css`. Arka uç açılmıyor.
**`dist` bu turda derlenir ve aynı commit'e girer.**

---

## Sıra

### 1. `ChatScreen.jsx` — `TokenCount` yerine `Stamp`

`shorten` olduğu gibi kalıyor; altındaki `TokenCount` **tamamen** şununla değişiyor:

```jsx
// The note that closes a message: when it was said, and -- for an answer that was measured -- what
// it cost. Under the message rather than over it, because a note about a thing is read after it.
// One line rather than two at the two ends, and no name in it: the sidebar carries the name, and
// which side a message sits on says who wrote it.
//
// One number out of the three the record keeps. The other two say what the cache saved, and that is
// a question about how requests are built rather than something a reader of the chat is asking. The
// count drops at zero -- an answer from before this existed reads back as zero, and a number there
// would claim a measurement nobody took. The time never drops: it was said at a time either way.
function Stamp({ at, usage }) {
  // The wait is stamped by an effect, so the first draw of a pending box has no time yet. Nothing
  // rather than an empty line.
  if (!at) return null;
  const spent = (usage?.sent ?? 0) + (usage?.answered ?? 0);
  const when = clockTime(at);
  return <div className="msg__stamp">{spent ? `${when} · ${shorten(spent)} tokens` : when}</div>;
}
```

### 2. `ChatScreen.jsx` — `waitingLabel` silinir

```jsx
const waitingLabel = askedAt ? `QueenAgent · ${clockTime(askedAt)}` : "QueenAgent";
```

satırı gidiyor. `Stamp` `askedAt`'i doğrudan alıyor; arada metin kuran bir değişkene gerek yok.

Üstündeki `onDisk` satırı ve yorumu duruyor.

### 3. `ChatScreen.jsx` — mesaj döngüsü

Baştaki `msg__label` bloğu **siliniyor**:

```jsx
{/* No name over the user's own bubble: ... */}
<div className="msg__label">
  {message.role === "user" ? clockTime(message.at) : `QueenAgent · ${clockTime(message.at)}`}
</div>
```

Sondaki `TokenCount` çağrısı **şununla değişiyor**:

```jsx
{/* Closes the turn. Only an answer carries a count: spending is what an answer does, and a
    number under the question would read as its price. The server sends the user's own message
    a usage of zeros, so this would hold without the check -- but a rule that leans on someone
    else's zeros breaks the day they change. */}
<Stamp at={message.at} usage={message.role === "ai" ? message.usage : null} />
```

### 4. `ChatScreen.jsx` — akan ve bekleyen kutular

Akan kutuda `<div className="msg__label">{waitingLabel}</div>` siliniyor, `CreatingFile`'ın
**altına** damga geliyor:

```jsx
{creatingFile ? <CreatingFile /> : null}
<Stamp at={askedAt} />
```

Bekleyen kutuda aynısı — etiket gidiyor, `CreatingFile`'ın altına `<Stamp at={askedAt} />` geliyor.

Her iki kutuda da damga **son çocuk**; testin tuttuğu kural bu.

### 5. `workspace.css` — bir kural gider, biri gelir

`.msg__label` bloğu (`font-family` · `font-size: 10.5px` · `letter-spacing` · `text-transform` ·
`color`) **tamamen siliniyor**.

`.token-count` bloğu da siliniyor, ve `.msg__stopped`'ın altına şu geliyor:

```css
/* The note that closes a message: when it was said, and what it cost. One step calmer than the
   stopped line above it, because it closes the turn rather than ending a sentence. No uppercase:
   the label this replaces wore it for a name, and a clock has no case. */
.msg__stamp {
  margin-top: 8px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--muted);
}
```

Sağa yaslama yazılmıyor: `.msg--user` zaten `align-items: flex-end` taşıyor.

**Dikkat:** stil kilidi `expect(CSS).not.toContain(".msg__label")` diyor ve **bütün dosyayı**
tarıyor, yorumlar dâhil. Yeni yorumda iki eski ad nokta ile yazılmıyor.

### 6. `workspace.css` — üç yorum koda uydurulur

**Bir**, `.msg--waiting`'in üstündeki:

```css
/* The design measures the wait at 10px, where a message uses 6. It named the gap between the label
   and the dots; the stamp sits under them now, and the wait is what the number was always for. */
```

**İki**, `.msg__stopped`'ın üstündeki **öksüz** yorum siliniyor — *"What the turn cost. Same family
as the steps above the answer and the label above that..."* diye başlayan blok. `.token-count`'u
anlatıyor ama iki kural yukarıda duruyor; 81 araya girerken kalmış, ve anlattığı kural artık yok.

**Üç**, `.msg__stopped`'ın kendi yorumu *"the count below"* yerine *"the stamp below"* diyor:

```css
/* Where the answer stopped. The same register as the steps above it and the stamp below: all three
   are notes about the text rather than the text itself. */
```

### 7. `dist` derlenir

```
npm run build --prefix queen-agent/frontend
```

Kaynakla **aynı commit'e** giriyor; `test_dist_is_committed.py` bunu zorluyor.

## Turda çıkan: bir testin kapsamı fazla genişti

Kod bittiğinde 11 kırmızının 10'u yeşile döndü, biri kalmaya devam etti — ve kalan **kodda değil,
testte**. `an answer is stamped with the time and nothing else either` şunu diyordu:

```jsx
expect(screen.queryByText(/QueenAgent/)).toBeNull();
```

`ChatScreen` dosya rafını da çiziyor, ve rafın boş hâli *"No files yet — send a message and
QueenAgent will create one."* diyor. Regex onu yakalıyor. Testin iddiası doğru — cevabın üstünde ad
yok — ama baktığı yer bütün ekrandı.

Kapsam sohbet sütununa çekildi:

```jsx
expect(container.querySelector(".chat__column").textContent).not.toContain("QueenAgent");
```

**Test turunda da kırmızıydı ve doğru sebeple kırmızıydı** — o gün etiket `.chat__column`'un
içindeydi. Yani kırmızı yanlış yerde değildi, yalnız fazlasını da kapsıyordu. Düzeltme bu turun
commit'ine giriyor.

**Ders:** ekranın tamamına sorulan bir yokluk iddiası, o ekranın çizdiği her şeye sorulur.
`ChatScreen` üç şey çiziyor: sohbet, yazma kutusu, dosya rafı. Bir iddia hangisi hakkındaysa oraya
sorulur.

## Beklenen yeşil

Arka uçta **2 failed, 430 passed** — ikisi defterin dalı, bu maddeyle ilgisiz.
Ön yüzde **497 passed**, kırmızı yok.

## Bilerek yapılmayanlar

- **Arka uca dokunulmaz.** Damga `at` ile `usage`'dan çiziliyor ve ikisi de yerinde.
- **`shorten` değiştirilmez.** Eşiği ve biçimi 68'in kararı.
- **`askedAt` efektine dokunulmaz.** Bekleyen kutunun saatini damgalayan şey aynen duruyor; yalnız
  çıktısı `Stamp`'e gidiyor.
- **`clockTime` değiştirilmez.** `16:27` biçimi deponun kendi biçimi; kullanıcının örneğindeki
  `16.27` bir yazım.
- **Kenar çubuğunun `QueenAgent`'ı silinmez.** `Sidebar.jsx`'teki kelime uygulamanın adı.
- **Testlere dokunulmaz.** Bir test kod yazılırken düzeltiliyorsa kırmızı yanlış yerdeydi; o zaman
  durup söylenir.
