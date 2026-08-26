# Madde 85 — Çağrı kartı geriye oturur · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 4, Madde 85 ·
**Üstüne geldiği:** [Madde 84](2026-08-26-queenagent-m84-tool-callar-karta-doner-uygulama-design.md) —
kartın kendisi.
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod yazılmaz, ve tur kırmızı
commit'lenir.

---

## Neden fazla canlı

84 kartı dosya kartının iskeletiyle kurdu, ve iskeletle birlikte onun ışığını da aldı:

| | Çağrı kartı bugün | Sayfa | `Stopped` |
|---|---|---|---|
| Zemin | `--surface` `#fffdfa` | `--canvas` `#f7f5f1` | yok |
| Metin | `--ink` `#22201d` | — | `--muted` `#8b8378` |

Zemin sayfadan **daha parlak**. Bu, kartı sayfanın üstüne kaldırıyor — beyaz bir kutu, cevabın
üstünde. Metin de neredeyse siyah, yani cevabın gövdesiyle aynı ağırlıkta.

İkisi birlikte, bir kaydı bir duyuru gibi okutuyor.

**Dosya kartı için doğru olan buydu:** o bir kapı, basılınca dosya açılıyor, ve öne çıkması
gerekiyor. Çağrı kartı bir kayıt. Aynı iskeleti giyer ama aynı ışığı almaz.

## Ne olacak

**Zemin bir tık koyuya iner:** `#f4efe7`. Sayfadan *(#f7f5f1)* aşağıda, yani kart öne çıkmak yerine
geriye oturuyor. Renk uydurulmuyor — deponun en açık tonu, bugün `.file-card--selected`'da duruyor.

**Metin `Stopped`'ın grisine iner:** `var(--muted)`. Kullanıcının verdiği ölçü bu.

## Kararı verilmiş

*(kullanıcı kararı, 26 Ağustos)*

**Zemin kalkmıyor.** Çerçevesiz, zemini sayfaya bırakan bir kart önerildi ve reddedildi: *"zemin
kalkmasın, zeminde sussun daha soluk olsun"*. Kart kart kalıyor.

**Bedeli biliniyor:** başlık da sonuç da `--muted` olunca kart tek düz tona iniyor. Kullanıcının
verdiği ölçü *"`Stopped` yazısı gibi"* ve `Stopped` tam olarak öyle — tek ton, mono, gri. Ayırt eden
şey renk değil, yer: biri solda ve uzarsa kesiliyor, öteki sağda ve yerini koruyor.

## Kırmızıya dönecek testler

Hepsi `workspace.css.test.js`'te. Bu madde yalnız iki renge dokunuyor, ve stil kilidi tam olarak
bunun için var — jsdom bu dosyayı hiç yüklemiyor, yani kilit bir davranış testi değil, yazılı bir
karar.

| # | Ne tutuyor | Bugün |
|---|---|---|
| 1 | **yeni** — kart geriye oturuyor: hem `.tool-call` hem `.tool-calls__handle` zemini `#f4efe7`, ve `--surface` hiçbirinde geçmiyor | ikisi de `var(--surface)` |
| 2 | **yeni** — metin `Stopped`'ın sesinde: `.tool-call__head` ve `.tool-calls__summary` `var(--muted)`, ve `--ink` hiçbirinde geçmiyor | ikisi de `var(--ink)` |

Toplam **iki kırmızı**.

## Dokunulmayan yeşiller

| Ne | Neyi kanıtlıyor |
|---|---|
| `a call is drawn on the card the repo already has` | İskelet duruyor: kenarlık, 12px köşe, 340px sınır |
| `only the handle offers to be pressed` | Kapı hâlâ kapı, kayıt hâlâ kayıt |
| `the stopped line reads as a note, not as the answer` | Ölçünün kendisi — bu madde ona benzeyecek, onu değiştirmeyecek |
| `ChatScreen.test.jsx`'in on üç çağrı testi | 84'ün davranışı değişmiyor: açılma, kapanma, sayı, akan turun son çağrısı |
| `.file-card` testleri | Dosya kartı parlak kalıyor; ayrışan çağrı kartı |

## Kapsam dışı

- **Davranış.** Açılma, kapanma, tutamağın ne yazdığı — 84'ün kararı, tek satırı değişmiyor.
- **İskelet.** Kenarlık rengi, köşe, genişlik, iç boşluk, `fadeIn`.
- **Dosya kartı.** O bir kapı ve parlak kalıyor.
- **`Stopped` satırı.** Ölçü o; ölçüye dokunulmaz.
- **Arka uç.** Tek satır değişmiyor.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur** — birlikte koşturulduğunda vitest bu makinede zaman aşımına düşüyor.

Arka uçta değişiklik beklenmiyor: bugünkü **2 failed, 430 passed** aynen kalır, ve o iki kırmızı
defterin `feat/queenagent-v5`'te duran dalı.

Ön yüzde bugün **505 passed**. İki yeni testle toplam **507**, ve **2 failed, 505 passed** beklenir.

`dist` bu turda derlenmiyor: kaynak değişmiyor, yalnız testler yazılıyor.
