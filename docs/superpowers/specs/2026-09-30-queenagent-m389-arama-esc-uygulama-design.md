# Madde 389 — Sohbet aramasında Esc yalnız aramayı boşaltır · uygulama turu

**Kaynak:** [yol haritasının 389'u](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); testler
[test turunun spec'inde](2026-09-30-queenagent-m389-arama-esc-testler-design.md) ve `App.test.jsx`'te
commit edildi.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne yapılacak

`Sidebar.jsx`'in arama kutusu, Esc'te kutuda yazı varsa yazıyı boşaltır **ve olayın yukarı
kabarmasını durdurur** (`event.stopPropagation()`). Kutu boşsa olaya dokunmaz: Esc `App.jsx`'in
dinleyicisine ulaşır ve bugünkü gibi sıradakini kapatır.

Neden bu tutar: React 18 kendi olaylarını uygulamanın kök düğümünde dinler; sentetik olayın
`stopPropagation`'ı yerel olayı da durdurur, ve olay kökten `document`'a, oradan `window`'a hiç
geçmez. `App.jsx`'in dinleyicisi `window`'da olduğu için o basışı görmez.

## Düşünülen öteki yol

`App.jsx`'in dinleyicisi `event.defaultPrevented`'a bakar, kutu `preventDefault` çağırır. İki dosyaya
dokunur ve App'e bir alanın ayrıntısını öğretir; `stopPropagation` tek dosyada, kutunun kendi
işleyicisinde kalır. Seçilmedi.

`App.jsx`'in "stopping propagation does not stop a sibling" yorumu doğru kalır: o, `window`'a asılı iki
dinleyici hakkında; burada durdurulan, kutudan `window`'a giden yol.

## Dokunulan dosyalar

- `queen-agent/frontend/src/features/workspace/Sidebar.jsx` — `onKeyDown`'ın Esc dalı ve üstündeki
  yorum.
- Başka hiçbir şey. `dist` bu ajanın işi değil: derleme birleştirmeden sonra yapılır.

## Başka her Esc

- Kutu boşken Esc: bugünkü gibi — açık dosyayı (ya da sıradaki açık şeyi) kapatır.
- Kutunun dışındaki Esc: değişmez.
- Mesaj düzeltme kutusu ve proje adı alanı: değişmez; madde onlar hakkında değil.

## Nasıl görülür

Dört satır paralel: `npm test --prefix queen-agent/frontend`'te test turunun kırmızısı yeşile döner,
ötekiler yeşil kalır.

Adım adım dökümü
[uygulama planında](../plans/2026-09-30-queenagent-m389-arama-esc-uygulama-plan.md).
