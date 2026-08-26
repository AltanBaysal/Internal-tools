# Madde 83 — Mesajın damgası altına iner · **uygulama turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 4, Madde 83 ·
**Test turu:** [testler spec'i](2026-08-26-queenagent-m83-damga-mesajin-altina-iner-testler-design.md) ·
commit `5e46002`, **11 kırmızı**.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder. Testler yazıldı ve kırmızı commit'lendi;
burada onların tarif ettiği şey yapılıyor.

---

## Ne kırmızı

| Nerede | Kaç |
|---|---|
| `ChatScreen.test.jsx` | 9 |
| `workspace.css.test.js` | 2 |

Arka uçta hiçbir şey kırmızı değil ve olmayacak: damga zaten diskteki `at` ile `usage` alanlarından
çiziliyor, ve ikisi de yerinde.

## İki bileşen bire iner

Bugün mesajın iki ucunda iki şey var, ve ikisi ayrı yerde yazılı:

- **`msg__label`** — mesajın döngüsünde, satır içinde kurulan bir `div`. Cevapta `QueenAgent · 11:05`,
  kullanıcının mesajında yalnız `11:04`. Bekleyen ve akan kutular aynı metni `waitingLabel`
  değişkeninden alıyor.
- **`TokenCount`** — kendi bileşeni, mesajın en altında, sayı sıfırsa hiç çizilmiyor.

İkisi **`Stamp`** olarak birleşiyor. Tek bileşen, tek yer, üç çağrı: saklanmış mesaj, akan kutu,
bekleyen kutu.

```jsx
function Stamp({ at, usage }) {
  if (!at) return null;
  const spent = (usage?.sent ?? 0) + (usage?.answered ?? 0);
  const when = clockTime(at);
  return <div className="msg__stamp">{spent ? `${when} · ${shorten(spent)} tokens` : when}</div>;
}
```

Üç şeyi birden söylüyor ve üçü de karar:

- **Saat hiç düşmüyor**, sayı düşüyor. Sayı bir ölçüm ve ölçülmemiş olabilir; saat değil, bir şey her
  hâlükârda bir saatte söylendi.
- **Saat yoksa hiçbir şey çizilmiyor.** Bekleyen kutunun saati ilk çizimde henüz damgalanmamış
  oluyor *(`askedAt` bir efektle stamplanıyor)*, ve boş bir satır çizmektense hiç çizmemek doğru.
- **`shorten` olduğu yerde kalıyor.** 68'in kararı; `Stamp` onu çağırıyor, yeniden yazmıyor.

`waitingLabel` değişkeni siliniyor — `Stamp` doğrudan `askedAt`'i alıyor, arada bir metin
kurulmuyor.

## Sayı yalnız cevaba ait

Damga iki rolde de çiziliyor ama sayı yalnız cevapta:

```jsx
<Stamp at={message.at} usage={message.role === "ai" ? message.usage : null} />
```

Rol kontrolü kâğıt üstünde gereksiz — sunucu kullanıcının mesajına da bir `usage` gönderiyor ve
içi sıfır, yani `spent` zaten sıfır çıkardı. Ama duruyor, çünkü **bir kural söylüyor**: harcamak
cevabın yaptığı şey, ve sorunun altındaki bir sayı onun fiyatı gibi okunur. Sunucunun sıfırlarına
yaslanan bir kural, o sıfırlar değiştiği gün sessizce kırılır.

## Damga her mesajın son çocuğu

Üç yerde de en altta, hiçbir istisna yok:

| Kutu | Damganın üstünde ne var |
|---|---|
| Saklanmış mesaj | tool call'lar · metin ya da baloncuk · `Stopped` · dosya kartları |
| Akan kutu | tool call'lar · metin · doğmakta olan dosya |
| Bekleyen kutu | tool call'lar · üç nokta · doğmakta olan dosya |

Kural tek cümle olduğu için üç kutuda da aynı yeri buluyor, ve bir test onu bu cümleyle tutuyor:
her `.msg`'nin son çocuğu `msg__stamp`.

## Stil: iki kural düşer, biri gelir

`.msg__label` ve `.token-count` siliniyor. Yerine `.msg__stamp`:

```css
.msg__stamp {
  margin-top: 8px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--muted);
}
```

`.token-count`'un ölçüleri birebir — o zaten mesajın altındaki nottu ve doğru duruyordu. Gelen şey
`.msg__label`'ın **getirmediği**: `text-transform: uppercase` ile `letter-spacing`. İkisi bir isim
için vardı; `11:05` için bir anlamı yok.

Sağa yaslanma için hiçbir şey yazılmıyor: `.msg--user` zaten `align-items: flex-end` taşıyor, ve
damga onun çocuğu.

## Üç yorum koda uyduruluyor

CLAUDE.md'nin kuralı: bir yorum yalnız bugün doğru olanı söyler, ve çatışmada düzeltilen yorumdur.

1. **`.msg--waiting`'in üstündeki** — bugün *"10px between the label and the dots"* diyor. Etiket
   noktaların altına iniyor; sayı aynı kalıyor, ölçtüğü boşluğun adı değişiyor.
2. **`.msg__stopped`'ın üstündeki iki yorumdan biri öksüz.** *"What the turn cost..."* diye başlayan
   yorum `.token-count`'u anlatıyor ama iki kural yukarıda, `.msg__stopped`'ın üstünde duruyor — 81
   araya girerken kalmış. `.token-count` ile birlikte gidiyor.
3. **`.msg__stopped`'ın kendi yorumu** *"the count below"* diyor; aşağıdaki artık bir sayı değil,
   damga.

## Kapsam dışı

- **Arka uç.** Tek satır değişmiyor.
- **Sayının içeriği.** Neyin toplandığı, `shorten`'ın eşiği, önbellek payının çizilmemesi — 68 ile
  76'nın kararları.
- **`askedAt`.** Bekleyen kutunun saatini damgalayan efekt aynen duruyor; yalnız çıktısını `Stamp`'e
  veriyor.
- **Kenar çubuğundaki `QueenAgent`.** Uygulamanın adı orada kalıyor. Silinen şey mesajın üstündeki
  tekrar.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur.** Arka uçta **2 failed, 430 passed** — ikisi defterin dalı, bu maddeyle
ilgisiz. Ön yüzde **497 passed**, kırmızı yok.

`dist` bu turda **derlenip aynı commit'e giriyor**: ön yüz kaynağı değişiyor, ve
`test_dist_is_committed.py` bunu zaten zorluyor.
