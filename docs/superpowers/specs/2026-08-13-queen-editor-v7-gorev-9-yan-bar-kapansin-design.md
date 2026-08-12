# Görev 9 — Yan barda açık ikona basınca panel kapansın

**Roadmap:** [v7](../plans/2026-08-13-queen-editor-v7-roadmap.md) · Blok 4

## Sorun

Yan bardaki ikonlar yalnız seçim yapıyor: açık olanın ikonuna tekrar basmak hiçbir şey yapmıyor.
Panel her zaman açık, 320 piksel her zaman dolu, tuval hiç genişlemiyor.

## Kararlar

1. **Açık panelin ikonu onu kapatır.** Başka bir ikon eskisi gibi o paneli açar; aynı ikon aç/kapa
   olarak çalışır — kod editörlerindeki davranış.
2. **Kapalı, "boş panel" değil, "panel yok" demektir.** Sütun hiç çizilmez, genişliği tuvale
   geçer; kullanıcının istediği şey yer.
3. **Şerit her zaman durur.** Kapalıyken de ikonlar orada: geri açmanın yolu odur.
4. **Kapalıyken hiçbir ikon "açık" işareti taşımaz.** Şeritteki kenar çizgisi hangi panelin açık
   olduğunu söylüyor; açık panel yokken söyleyecek bir şey de yok.
5. **İlk açılış değişmez.** Ekran hâlâ fotoğraf paneliyle geliyor; kapalı başlamak, ilk kez
   girenden bir tıklama daha isterdi.
6. **Kapalılık bu sütunun kendi bilgisi.** Bugün hangi panelin açık olduğu da öyle; ne sunucu ne
   proje ekranı bunu bilmek zorunda.

## Testler

- Açık panelin ikonuna basınca panel ekrandan kalkar.
- Aynı ikona bir daha basınca geri gelir.
- Panel kapalıyken şerit yerinde ve hiçbir ikon açık olarak işaretli değil.
- Başka bir ikona basmak eskisi gibi o paneli açar.

## Öz eleştiri

- *Kapalıyken tuvalin genişlediğini test edebiliyor muyuz?* — Doğrudan değil; test edilen şey
  panelin çizilmediği. Genişlik oradan geliyor: sütun düzeninde olmayan bir kutu yer kaplamıyor.
  Piksel ölçmek, düzeni test etmek değil düzeni tekrarlamak olurdu.
- *Kapalı hâl hatırlansın mı?* — Hayır. Ekran her açılışta fotoğraf paneliyle geliyor ve bunu
  değiştirmek ayrı bir karar; bu görev istenen davranışı ekliyor, yenisini icat etmiyor.
