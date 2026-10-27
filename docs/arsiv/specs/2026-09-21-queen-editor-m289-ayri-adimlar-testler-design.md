# Madde 289 · Videolar, fotoğraflar, disclaimer — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

**Hiçbir şey.** İstek kullanıcının kendi cümlesi *(21 Eylül — "ilk videolar yüklensin, sonra
fotoğraflar eklensin, sonra disclaimer eklensin gibi")*, ve bu maddede karara bağlanacak bir şey
bırakmıyor.

## Bugünkü akış, koddan

`run_export` **tek döngü**: bir kareyi kesiyor, hemen o karenin fotoğrafını Drive'a kopyalıyor,
sonra sıradaki kareye geçiyor
*([run_export.py:70-94](../../../queen-editor/backend/features/photo_generation/domain/usecases/run_export.py#L70))*.
Yani iki iş iç içe, ve **kullanıcı doğru görmüş**.

Sıra bugün şu: `kes(01) · fotoğraf(01) · kes(02) · fotoğraf(02) · …` — ve birleşik modda en sonda
birleştirme.

## Neden ayrılıyor: düzen değil, ölçüm

Ayrılmalarının görünür bir karşılığı yok — çıkan dosyalar birebir aynı. Sebep **287**: adımlar iç
içe olduğu sürece süre ölçülse bile **hangisinin pahalı olduğu ayrılamaz**. Sayaç yavaş akıyorsa
sebebi videoyu Drive'dan okumak mı, fotoğrafı Drive'a yazmak mı — bugünkü kodun cevabı yok, çünkü
ikisi aynı adımın içinde.

**O yüzden bu madde 287'den önce:** bir adım, adlandırılmadan ve ölçülmeden önce gerçekten bir adım
olmalı.

## Ekran bu maddede değişmiyor, ve bu bilerek

`written` sayacı **videoları** saymaya devam ediyor, `total` yine kare sayısı. Fotoğraf evresi
ekranda kendi adıyla görünmüyor — yani videolar bittikten sonra ekran bir süre `N/N`'de duruyor.

**Boşluk gerçek, ve adı 287.** Bir durumun hangi cümleyle göründüğü ekranın işi *(255'in kararı)*,
yani burada yeni bir durum adı açmak ön yüzü de değiştirmek, `dist`'i de yeniden build'lemek
demekti — 287'nin işini yarım yapmak olurdu. Bu madde yalnız adımları ayırıyor.

## Çivilenen olgular

**1 · Ayrı export'ta önce bütün videolar, sonra bütün fotoğraflar.** İkizlerde tek bir zaman
çizgisi tutuluyor — `piece` ve `copy_photo` aynı listeye yazılıyor — ve iki kareli bir projede o
liste `piece, piece, copy_photo, copy_photo` oluyor. Bugün `piece, copy_photo, piece, copy_photo`.

**2 · Birleşik export'ta disclaimer en sonda.** Aynı çizgi:
`piece, piece, copy_photo, copy_photo, merge, copy_export`. Disclaimer birleştirmenin kendi
çağrısında *(250)*, yani *"sonra disclaimer"* birleştirmenin fotoğraflardan sonraya düşmesi
demek — ve bugün de sondaydı, bu maddede **fotoğraflar onun önüne toplanıyor**.

**3 · İkinci döngünün kendi iptal kontrolü var.** Son parça kesildiği anda iptal edilen bir koşu
hiçbir fotoğraf yazmıyor, klasörünü geride bırakmıyor, ve `None` dönüyor. **Tek test yetiyor:**
kontrol döngünün başında duruyor, yani *"ilk fotoğraftan önce"* ile *"iki fotoğraf arasında"* aynı
satır *(FOUNDATION 3)*.

**4 · Numaralandırma değişmiyor, ve bunun bekçisi zaten yazılı.** `foto/01.png` hâlâ
`video/01.mp4`'ün fotoğrafı, paylaşılan fotoğraf bir kez ve ilk kullanan karenin numarasıyla
yazılıyor *(236)*. Mevcut beş test bunu tutuyor — `test_every_exported_frame_leaves_its_photo_beside_its_video`,
`test_a_photo_keeps_the_extension_it_was_saved_with`,
`test_frames_sharing_one_photo_leave_one_picture_in_the_export`,
`test_a_shared_photo_is_filed_under_the_first_frame_that_uses_it`,
`test_a_merged_export_writes_the_shared_photo_once_too` — ve ikinci döngü numarayı kaybederse
hepsi kırmızıya döner. **Yenisi yazılmıyor:** aynı kuralı ikinci kez çivilemek, kuralı iki yerden
yönetmek olurdu.

## Kırmızı beklentisi: üç

| Test | Bugün |
|---|---|
| Ayrı export'un sırası *(olgu 1)* | **kırmızı** — iş kare kare, iç içe |
| Birleşik export'un sırası *(olgu 2)* | **kırmızı** — aynı sebep |
| Son parçadan sonra iptal *(olgu 3)* | **kırmızı** — fotoğraflar çoktan yazılmış, koşu bitiyor ve klasörünü dönüyor |

**İkizlere eklenen tek şey zaman çizgisi.** `ExportStore.order` zaten var — birleştirme ile
Drive'a kopyalamanın sırasını tutuyor *(282)*; bu tur `copy_photo`'yu ve `piece`'i de aynı listeye
yazıyor. İkizin kendi kuralı yok, yalnız ne olduğunu sırasıyla yazıyor.

## Kapsam dışı, ve bilerek

**Ekranın fotoğraf evresini söylemesi.** 287.

**İptalin fotoğrafın ortasında çalışması.** İptal her zaman **iş birimleri arasında** — yarım
kalan bir kopya, yarım kalan bir video kadar kötüdür, ve klasör zaten gidiyor.
