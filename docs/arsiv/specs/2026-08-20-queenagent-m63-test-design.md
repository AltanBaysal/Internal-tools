# Madde 63 · Tur 1 (test) — Tasarım

**Madde:** yeni — kullanıcı isteği, 20 Ağustos: "sohbette dosya açınca sağda sadece dosya görünsün,
Project files görünmesin; geriye basınca oraya geri geliyoruz zaten."
**Bu belgenin konusu:** rayın okuma hâlinde **ne olduğunu** ne tutacak.

---

## Bugünkü karar, ve neden değişiyor

Ray bir dosya açıkken ikiye bölünüyor: solda `Project files` başlığı ve bütün liste, sağında
okunan dosya. Kodun kendi yorumu gerekçesini yazıyor — *"bu panel rayın genişlemiş hâli, ve
genişlerken yanından ayrıldığı liste hâlâ yanında duruyor"* — ve amacı belliydi: **bir dosyayı
kapatmadan başkasına geçebilmek.**

Kullanıcının kararı bunun tersine: okunan şey ekranın tamamını hak ediyor. 560 pikselin 200'ü bir
listeye gidiyordu ve o liste bir tık uzakta zaten duruyor.

Bu, kodun kendi başına söyleyemeyeceği bir şey. İki düzen de tutarlı; hangisinin doğru olduğu
kullanılırken anlaşılıyor, ve kullanan kişi söyledi.

## Karar

Okuma hâlinde rayda **yalnız okuyucu** var. Başlık yok, sayı yok, liste yok, satır yok.

Geri düğmesi (`←`) zaten duruyor ve listeye döndürüyor — o yüzden bu bir kayıp değil, bir tık.

## Bunun götürdükleri

Üç davranış bu kararla birlikte **ortadan kalkıyor**, ve üçü de bugün kendi testine sahip:

1. **Açık bir dosyanın yanından başkasına geçmek.** Kullanıcının bilerek verdiği bedel; artık önce
   geri, sonra öbür dosya.
2. **Okunan satırın işaretli olması.** Görünecek satır kalmıyor.
3. **Okunurken satırlardan silmek** — ve onunla birlikte, okunan dosyanın satırının × taşımaması
   kuralı. İkisi de aynı sebeple: ortada satır yok.

Üçü de silinen davranışlar, kırılan testler değil. Kaydı burada.

## Testin sorması gerekenler

- Okuma hâlinde rayda **liste yok**: başka bir dosyanın adı geçmiyor.
- Okuma hâlinde **`Project files` hiç yazmıyor** — ne başlık ne etiket olarak.
- Okuma hâlinde **hiçbir silme düğmesi yok**. Bugün yandaki listede duruyorlar.
- Biçem tarafında: `.rail__list` diye bir kural **kalmıyor**, ve `.rail--open` artık iki şeyi
  ayıran bir boşluk taşımıyor — ayıracak iki şey yok.
- Ve bütün kararın dayandığı söz, uçtan uca: sohbette dosya açılınca yalnız belge kalıyor, `←`
  basılınca **liste geri geliyor**. Bu App seviyesinde sorulmalı, çünkü geri dönüşü sağlayan
  `close` rayın değil App'in.

## Dokunulmayan, ve neden

**`FileRow`'un `selected` prop'u.** Rayın listesi artık onu hiç geçirmiyor, ve proje ekranı da
geçirmiyordu — yani uygulamada çağıranı kalmayacak. Yine de kaldırılmıyor: `FileRow` sunum
bileşeni, bu durum onun kendi testinde tanımlı, ve bir bileşenin yeteneğini budamak bu maddenin
sorduğu soru değil. **Çağıransız kaldığı burada yazılı** — kaldırılacaksa ayrı bir karar olarak.

**Rayın okuma hâlindeki 560 piksellik genişliği.** Değişmiyor. O genişlik zaten belge için
istenmişti; şimdi tamamı belgeye gidiyor, 360'ı yerine.
