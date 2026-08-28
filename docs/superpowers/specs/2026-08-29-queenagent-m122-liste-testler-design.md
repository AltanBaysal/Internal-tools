# Madde 122 — Numaralı liste bire takılmıyor · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 122.
**Gözlenen** *(28 Ağustos)*: sohbette numaralı liste `1 2 3` yerine `1 1 1` sayıyor.

## Kök neden — bulundu

Model numaralı maddelerin arasına boş satır koyuyor — `1. a\n\n2. b\n\n3. c`, LLM'lerin olağan
yazımı — ve `markdown.js`'te boş satır bloğu bitiriyor: `listFrom` yalnız ardışık satırları
topladığı için üç madde **üç ayrı liste** oluyor. `Markdown.jsx` her listeyi kendi `<ol>`'ü
olarak çizince tarayıcı her birini 1'den sayıyor. Yazılan rakamın kendisi zaten okunmuyor
*(`NUMBER` deseni `\d+`'ı yakalamadan atıyor)* — sayıyı sıra verir, tarayıcı çizer.

## Kural

Boş satır listeyi ancak ardından **liste olmayan bir şey** geliyorsa bitirir. Boşluğun ötesindeki
ilk dolu satır aynı türden ve en az aynı derinlikte bir maddeyse liste sürer; farklı türdense
*(numaranın altında bullet)* ya da daha sığsa liste orada biter.

**Bilerek yapılmayan:** `<ol start>` — yazılan rakam okunmaya başlanmıyor. Sayıyı sıra verir;
`3.` ile açılan yalnız bir liste hâlâ 1'den sayar, ve bu gözlenen şikâyet değil.

## Testler

**`markdown.test.js`** — üç yeni: boş satırla ayrılmış numaralar tek liste *(üç item)*; boş
satırla ayrılmış bullet'lar da tek liste; boş satırdan sonra paragraf gelirse liste bitiyor
*(iki blok)*.

**`Markdown.test.jsx`** — bir yeni: boş satırlı numaralı metin tek `<ol>` ve üç `<li>` çiziyor.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `markdown.test.js` | 2 *(paragraf testi bugün de geçer — davranış korunuyor)* |
| `Markdown.test.jsx` | 1 |

## Bilerek yapılmayanlar

- **`markdown.js` ve `Markdown.jsx` açılmaz** — tur 2.
- **`dist` bu turda derlenmez** — kaynak tur 2'de değişiyor.
