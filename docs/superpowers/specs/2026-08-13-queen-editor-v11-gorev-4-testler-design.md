# v11 Görev 4 — seçim kalkınca halkalar da kalkar: TEST döngüsü (tasarım)

**Tarih:** 2026-08-13 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v11](../plans/2026-08-13-queen-editor-v11-roadmap.md) · **Döngü:** 1/2 (testler)

Bu spec **yalnız testleri** tanımlıyor. Kod bu döngüde değişmiyor.

## Bu bir hata değil, geri alınan bir karar

Galeride iki ayrı şey var: **seçim** (hangi kareler) ve **seçim modu** (karoların üstünde halkalar,
tıklamak seçer, sürüklemek kapalı). Bugün mod seçimden bağımsız yaşıyor: son kare de bırakılınca
seçim boşalıyor ama mod açık kalıyor.

Bu bilinçliydi ve testte yazılı — mevcut bir testin yorumu birebir şöyle diyor: *"deselect: the mode
stays open, the bar goes"*. Kullanıcı 2026-08-13 Colab turunda bunu tersinden gördü: alttaki çubuk
kayboluyor ama halkalar duruyor, ve seçimin sürüp sürmediği anlaşılmıyor.

Yeni kural: **mod seçimin kendisidir.** Seçim boşalınca mod da biter — halkalar kalkar, karo tıklamak
yine fotoğrafı açar, sürükleme geri gelir. "Vazgeç"in yaptığı şeyin aynısı, sadece son kareyi
bırakmakla da oluyor.

Bunun bir bedeli var ve yazılı olsun: bugün son kareyi bırakıp başka bir karoya tıklayarak seçime
devam edebiliyorsun; bundan sonra o tık fotoğrafı açacak. Seçime devam etmenin yolu halkaya
tıklamak olacak — halka fare gelince zaten beliriyor.

## Vakalar

Hepsi `Gallery.test.jsx`'te; seçim modu galerinin kendi içinde yaşıyor, ekrana çıkan tek şey seçilen
kareler ve o dikişi Görev 2'nin ekran testi zaten koruyor.

| # | Vaka | Beklenen |
|---|---|---|
| H1 | Bir kare seçilir | Karolar seçim modunda |
| H2 | Sonra o kare bırakılır | Karolarda seçim modundan eser yok |
| H3 | Seçim varken "Vazgeç" | Mod kapanır (bugün de öyle — kural değişince kırılmasın diye) |
| H4 | Hepsi seçiliyken "Tümünü seç" tekrar basılır (boşaltır) | Mod kapanır |

H4 ayrı bir vaka çünkü seçimi boşaltmanın iki yolu var — kareyi bırakmak ve listeyi boşaltan düğme —
ve ikisi koddaki farklı satırlardan geçiyor. Yalnız birini sınamak ötekini açıkta bırakır.

Mevcut *"takes the bar away when the selection is emptied"* testi kalıyor: çubuğun gitmesi hâlâ
doğru. Değişen tek şey yorumundaki "the mode stays open" cümlesi, ki artık yanlış.

## Testin dürüst sınırı

Halkanın görünürlüğü CSS'te (`.qe-tile--selecting .qe-check { opacity: 1 }`). jsdom stil sayfasını
uygulamıyor, dolayısıyla test **pikseli değil, CSS'in dayandığı sınıfı** okuyor. Sınıf yanlışsa
halka da yanlış olur; sınıf doğruyken CSS bozulmuşsa test bunu göremez. Bu koşuda kapatılabilecek
bir boşluk değil — söylenmesi gereken bir sınır.

## Kapsam dışı

- **Halkanın köşesi** — Görev 5. Bu görev halkanın ne zaman var olduğunu konuşuyor, nerede
  durduğunu değil.
- Silme akışı, Esc, sürükleme: hiçbiri değişmiyor; H3 onların bozulmadığına tanık.

## Kırmızı commit

Dört test eklenir; H2 ve H4 düşer, H1 ve H3 geçer. İkisinin geçmesi bilerek: kuralın bozulmayan
yarısını da yazılı hâle getiriyorlar, yoksa implementasyon modu tümden kaldırıp ikisini birden
öldürebilir.

## Bitti sayılır

`npm test --prefix queen-editor/frontend` iki düşen test gösteriyor ve ikisi de "seçim modu sınıfı
hâlâ duruyor" diye düşüyor.
