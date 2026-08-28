# Madde 122 — Numaralı liste bire takılmıyor · Tur 2 (uygulama) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 122 ve
[tur 1'in tasarımı](2026-08-29-queenagent-m122-liste-testler-design.md). Kök neden orada:
boş satır her listeyi bitiriyor, üç `<ol>` üçü de 1'den sayıyor.

## Değişen tek yer: `markdown.js` · `listFrom`

Döngünün başına boş satır dalı: boşluğun ötesindeki ilk dolu satıra bakılır —

- daha sığ, madde değil, ya da aynı derinlikte **farklı türden** ise liste biter *(bugünkü
  davranış: listeden sonra paragraf, numaranın altında bullet)*;
- aynı türden ve en az aynı derinlikteyse boşluk atlanır ve liste sürer — derin olan zaten
  var olan iç-liste dalına düşer.

`Markdown.jsx` değişmiyor: tek liste geldiğinde tek `<ol>` çiziyor ve tarayıcı doğru sayıyor.

## Bilerek yapılmayan

**`<ol start>` yok** — yazılan rakam okunmaya başlanmıyor; sayıyı sıra verir. `3.` ile açılan
tek başına bir liste 1'den sayar, ve bu gözlenen şikâyet değil.

## `dist`

Ön yüz kaynağı değişiyor — aynı commit'te derlenir.

## Beklenen yeşil

Frontend suite'in tamamı, üç yeni dahil; backend olduğu gibi, defter çifti bilinen kırmızı.
