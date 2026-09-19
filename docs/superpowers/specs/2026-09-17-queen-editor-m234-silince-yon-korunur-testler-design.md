# Madde 234 · Detayda silinen kareden sonra gidilen yönde kalınır — test turunun tasarımı

**Tarih:** 17 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Kullanıcı istenen davranışı iki örnekle verdi *(1, 2, 3, 4 giderken 4 silinince 5; 5, 4,
3 giderken 3 silinince 2)*, teknik kararları da bıraktı.

## Bugün ne oluyor

[`PhotoDetail.jsx`](../../../queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx)'de
`handleRemove` silmeden önce gidilecek kareyi `next || previous` ile seçiyor. Kullanıcının hangi oka
bastığını bilen bir yer yok. Geriye doğru temizleyen kullanıcı her silmede ters yöne atılıyor.

Sayfa kareler arasında kurulu kalıyor *(oklar yalnız adresi değiştiriyor)*, yani bir önceki basışı
hatırlamak sayfanın kendi işi olabilir.

## Ne olacak

1. **Yön, kareyi değiştiren son basış.** Ekrandaki ‹ ve › ile klavyedeki ← ve → aynı şeyi sayıyor.
2. **Silince o yöndeki kareye geçilir.** Geçiş de aynı yönü taşır, yani art arda silmek aynı yönde
   ilerler.
3. **O yönde kare yoksa öbür yöne**, hiç kare kalmamışsa galeriye dönülür. Bu bugün de böyle.
4. **Henüz ok basılmamışsa yön ileri** *(`next`)*, bugünkü gibi. Galeriden açılan detay böyle başlar.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | ‹ ile gelinen karede silince bir öncekine geçiliyor | **kırmızı** |
| 2 | ← ile gelinen karede de aynısı | **kırmızı** |
| 3 | › ile gelinen karede silince bir sonrakine geçiliyor | yeşil *(bekçi)* |
| 4 | Art arda iki silme aynı geri yönde ilerliyor | **kırmızı** |
| 5 | Geri yönde kare kalmamışsa öbür yöne düşülüyor | yeşil *(bekçi)* |

Galeriden açılıp hiç ok basılmadan silmenin bir sonrakine geçtiği ve son kare silinince bir öncekine
düşüldüğü mevcut testlerde zaten çivili *(`asks before deleting, then opens the next photo`,
`falls back to the previous photo when the last one is deleted`)*.

## Bu turda değişen

Yalnız testler: `PhotoDetail.test.jsx`.
