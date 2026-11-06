# Madde 524 · Fotoğraf kaydına satırlar sırayla yazılır — tasarım

**Tarih:** 6 Kasım 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-23),
524 · v11-23 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Plan:**
[2026-11-06-queen-editor-m524-fotograf-kaydi-sirayla-plan.md](../plans/2026-11-06-queen-editor-m524-fotograf-kaydi-sirayla-plan.md)
· **Kurallar:** queen-editor [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kabul koşulu (maddeden)

Sıra ve düğmeler fotoğraf kaydına aynı anda satır yazınca satırlar bölünmüyor, kaybolmuyor ve
yazıldıkları sırada kalıyor — Drive'ın bağlantısı bunu kendisi garanti etmese de. 513'ün "bitti
ezilemez" kuralı bu sıraya dayanıyor.

Kullanıcı — *"bu hatalarıda çöz istersen"*. BACKLOG'un işi: *"Fotoğraf kaydına aynı anda iki satır
yazılabilir"* (512'nin reviewer'ı). Ekran değişmez; `dist` derlenmez.

## Bugün

`photos.jsonl`'e her yazma `DrivePhotoRecord.append`'den geçer (`mark` ve `prompt_written` de onu
çağırır), o da `Storage.append_line`'a: dosyayı ekleme kipinde açar, satırı yazar, `fsync`, kapatır.
Kilit yok. Yazanlar iki ayrı yerden gelir:

- **Sıranın döngüsü**, kendi iş parçacığında, adın kilidinde (**N**, 513): biten katmanın satırı,
  bir hata, yazılmış bir prompt.
- **Kapılar**, istek iş parçacıklarında, projenin yazma kapısında (**G**, 512): kopya karenin
  satırları, "sırada", "çıkarıldı", "silindi" işaretleri.

N ile G farklı kilitler ve döngü G'yi hiç almaz (GPU kapıları beklemesin diye, 522). Yani döngünün
bir satırı ile bir kapının satırı aynı anda yazılabiliyor. Yerel Linux'ta tek bir küçük `O_APPEND`
yazması ötekine karışmaz; Drive'ın FUSE bağlamasının bunu koruduğunu söyleyen bir şey yok. Bir yazma
dosyaya iki parça halinde ulaşırsa ve ikinci satır araya girerse iki satır da bozulur; okuma bozuk
satırı atladığı için ikisi de kaybolur. İki ekleme aynı anda uçuştaysa hangisinin önce durduğu da
bağlamaya kalır.

`DriveChatRecord` aynı sebeple satırları tek tek yazar (madde 420).

## Ne yapılır

`DrivePhotoRecord` bir kilit tutar (`threading.Lock`, sınıf başına bir tane) ve `append` satırı
yalnız onun içinde `append_line`'a verir. JSON'a çevirme kilidin dışında. Başka hiçbir şey değişmez:
diskteki biçim aynı, okumalar kilitsiz.

Böylece süreçte aynı anda en çok bir ekleme uçuşta olur; bir ekleme ancak öncekinin satırı yazılıp
`fsync` edilip dosya kapandıktan sonra açılır. Bağlamanın iki eşzamanlı eklemeyi nasıl birleştirdiği
artık hiç sorulmaz: ona yalnız art arda gelen, her biri bitmiş eklemeler gider — her kaydın zaten
yaptığı şey.

### Neden yeni bir kilit türü değil, ve neden G ya da N değil

- Bu, `DriveChatRecord`'un, `DriveMuteStore`'un ve `DriveProjectStore`'un kilidiyle aynı tür: deponun
  kendi yaprak kilidi, yalnız kendi dosya işlemi boyunca tutulur.
- **G** olmaz: döngü G'yi alırsa GPU kapıları (bir kapının bütün okumalarını ve yazmalarını) bekler.
- **N** olmaz: N döngünün okumaları boyunca tutulur (bir fotoğrafın ya da videonun baytları, referans
  havuzu); her kapı satırı onları beklerdi. Ayrıca N adların kilidi, bir veri deposunun değil.
- Proje başına değil, tek: sözlük ve onu koruyan ikinci bir kilit gerekirdi; tutuş tek bir satır
  kadar kısa, ve yazanlar bir döngü ve ara sıra bir basış.

### Okumalar neden kilitsiz

Bir okuma yazılmakta olan bir satırı yarım görebilir: o, dosyanın son satırıdır ve `_parse` onu
atlar (bugün de öyle). Kaydın önbelleği (`FileCache`) damgayı okumadan önce alır; satır bitince boy
değişir, sonraki okuma dosyayı yeniden açar. Son satırı görmeden karar veren bir kapının satırı
513'ün `from`'u ile yazılır ve ardından düşerse geçmez — 513'ün kuralı tam bunun için. Okumayı
kilide almak, döngünün her okumasını kapıların eklemelerine bekletirdi ve hiçbir şeyi düzeltmezdi.

## Neden satırlar bölünmez, kaybolmaz, sırası kaymaz

- **Bölünmez:** bir eklemenin bütün parçaları kilidin bir tutuşunda; başka bir ekleme o tutuş
  bitmeden dosyaya dokunmaz.
- **Kaybolmaz:** her ekleme dosyanın bir önceki eklemeden sonraki sonunu görür, çünkü o ekleme
  kapanmıştır; hiçbir satır başkasının üstüne düşmez.
- **Sırası kaymaz:** dosyadaki sıra kilidin alınış sırasıdır. Bir ekleme bittikten sonra başlayan
  ekleme hep sonra durur. 513'ün kuralı bunu ister: bir kararın satırı, okunduğu durumdan sonra yazılan
  bir satırın ardında durmalı. Aynı anda gelen iki ekleme için sıra zaten belli değildir; kilit
  ikisinden birini öne alır ve ikisi de bütün kalır. İkisi de 513'ün katlamasında doğru okunur:
  bitmiş bir katman `from`'suz yazılır, `from`'lu bir kararın satırı bitmiş katmanın önünde dursa da
  ardındaki "bitti" satırı onu geçer, ardında dursa da `queue.applies` onu geçersiz sayar.

## Kilitler

513–523'ün tablosuna bir yaprak eklenir: kaydın kilidi **K** (`DrivePhotoRecord._appending`).

| Kim | Sıra |
|---|---|
| Kapılar | G → … → K (her satır için ayrı, kısa) |
| Döngü | N → K (turun yazmaları) |
| Yeniden adlandırma, silme | K'ye uğramaz |

K bir yaprak: içinde hiçbir kilit alınmaz; tutulurken yalnız mount bakışı, bir yer bakışı (`disk_usage`), dosyanın
açılması, yazma, `fsync` ve kapama var. Yeni kenarlar yalnız G→K ve N→K; K'den çıkan kenar yok.
Döngü açılmaz.

**GPU hiçbir kapıyı beklemez:** döngü G'yi yine almaz. K'de yalnız yazılmakta olan satırları bekler,
bir kapının okumalarını ya da G'yi hiç: çok satır yazan bir kapı K'yi her satırda bırakır. Kilit adil
değildir; art arda satır yazan bir kapı (`remove_frames`, bir partiye `queue_layer`, kopya karenin
satırları) K'yi uyanan döngüden önce yeniden alabilir — reviewer bekleyen biri varken iki üç kapı
satırının yazıldığını ölçtü. Adil bir kilit eklenmez: bekleme yine yalnız satır yazmalarıdır. Döngünün
o satırı yazdığı an GPU zaten boştur — satır render bittikten sonra yazılır.

## Maliyet

- Drive'a ek işlem yok: her ekleme eskisi gibi bir yer bakışı, bir açma, bir yazma, bir `fsync`.
  Proje, kare ve satır sayısından bağımsız, O(1).
- Bekleme: o an yazılan satırların eklemeleri kadar (her biri Drive'da birkaç gidiş dönüş); kilit
  adil olmadığı için art arda yazan bir kapının birkaç satırı olabilir.
- Okumalar değişmez.

## Ne kaybolabilir, ne bozulabilir

- Diskte hiçbir biçim değişmez; kilit bellekte. Sunucu ölürse en çok yazılmakta olan satır yarım
  kalır ve okumada atlanır (bugünkü gibi).
- Kilidin içinde bir ekleme hata verirse (dolu Drive, kopan bağlantı) kilit bırakılır ve hata
  çağırana gider (503, bugünkü gibi).

## Sınırlar

- Kilit bir sürecin içini korur. Kaydı bir tek sunucu yazar (`main.py`'de tek `DrivePhotoRecord`);
  aynı Drive klasörünü aynı anda başka bir makineden yazan ikinci bir Colab bu maddenin dışında.
- Art arda gelen, her biri `fsync` edilip kapanmış eklemelerin Drive'da sırasıyla durduğu, her
  kaydın bugün dayandığı şey; Colab'da denenecek.

## Ne zaman bitti

- Gerçek bir klasörde, birinci eklemesi dosyaya iki parça halinde ulaşan bir depoyla, ikinci bir
  `append` parçaların arasına sokulunca dosyada iki satır bütün ve yazılış sırasıyla duruyor; ikinci
  `append` birincinin ilk baytından önce sokulunca da. Eski kodda ikisi de kırmızı (bölünen satır;
  öne geçen satır).
- BACKLOG'dan *"Fotoğraf kaydına aynı anda iki satır yazılabilir"* silindi.
- `python -m pytest queen-editor -q` yeşil (bilerek kırmızı iki `test_notebook_clones_its_branch`
  testi dışında).

## Yalnız Colab'da görülecek

- Gerçek Drive'da sıra çalışırken kopya kare ve Kuyruktan çıkar'a basmak: kayıtta yarım satır yok,
  kart ne gördüyse o.
