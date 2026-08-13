# v11 Görev 5 — kare köşeleri yeniden dağıtılır: İMPLEMENTASYON döngüsü (tasarım)

**Tarih:** 2026-08-13 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v11](../plans/2026-08-13-queen-editor-v11-roadmap.md) · **Döngü:** 2/2
**Testler:** [test spec'i](2026-08-13-queen-editor-v11-gorev-5-testler-design.md) ·
commit `527393a` (beş test kırmızı)

## Yerleşim

Üç satır içi konum değişiyor: etiket sol üste, halka sağ üste, rozet yerinde. Dördüncü köşe
(sahiplik) ve kartın ortası aynı.

## İki tuzak, ikisi de bu spec'te çözülüyor

**1. Kit'in `Mono`'su `className`'i birleştirmiyor.** `<span className="wf-mono" {...rest}>` yazıyor,
yani dışarıdan gelen `className` `wf-mono`'yu **siliyor** — rozet mono yazı tipini kaybederdi.
`vendor/` elle düzenlenmiyor (CODE-STANDARD), dolayısıyla çözüm çağrı yerinde: sınıf
`"wf-mono qe-badge"` olarak veriliyor ve neden tekrarlandığı yorumla söyleniyor.

**2. Satır içi `opacity` CSS'i yener.** Rozet bugün fotoğrafı olmayan kare için satır içi
`opacity: 0.5` taşıyor. `.qe-tile:hover .qe-badge { opacity: 0 }` kuralı ona karşı kaybeder ve numara
hiç kaybolmazdı. Sönük ton da CSS'e taşınıyor (`qe-badge--muted`), böylece iki kural aynı dilde
yarışıyor ve daha belirgin olan — gizleme — kazanıyor.

İkincisi görünmez bir hata olurdu: test satır içi konumu okur, geçer; ekranda numara halkanın
altında durmaya devam ederdi.

## Gizleme neden CSS'te

Halka iki durumda beliriyor — fare üstündeyken ve seçim modunda — ve ikisi de CSS'te
(`.qe-tile:hover .qe-check`, `.qe-tile--selecting .qe-check`). Rozetin gizlenmesi onun aynadaki
görüntüsü: aynı iki seçici, ters etki, yan yana duran iki kural. Numarayı JavaScript'le gizlemek
seçim modunu test edilebilir yapardı ama fare hâlini yine CSS'te bırakırdı — tek davranış, iki
mekanizma. Testin bu sınırı `527393a`'da yazılı.

## Değişen yerler

| Dosya | Ne olacak |
|---|---|
| `.../photo_generation/frame_status.jsx` | `PILL` alt-sol yerine üst-sol |
| `.../photo_generation/Gallery.jsx` | `CHECK` sol yerine sağ; rozete `qe-badge` sınıfı, satır içi opaklık kalkar |
| `.../shared/app.css` | rozetin sönük tonu + halkanın belirdiği iki durumda gizlenmesi |
| `queen-editor/frontend/dist/` | yeniden derlenir (aynı commit) |

## Kapsam dışı

- Sahiplik rozetleri, kartın ortası, sürükleme, silme çubuğu.
- Halkanın ne zaman var olduğu (Görev 4).

## Bitti sayılır

`npm test --prefix queen-editor/frontend` → 322 geçen, 0 düşen. Beş testin hiçbiri değiştirilmemiş,
`dist/` aynı commit'te yeniden derlenmiş olur.
