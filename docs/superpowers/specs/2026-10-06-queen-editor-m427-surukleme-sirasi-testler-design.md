# Madde 427 — Bir satırı sürüklemek öteki satırların sırasını silmesin, test turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 427 · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Madde 6 Ekim'de hizalandı *(kullanıcı — "427 de ui tasrımı ve ya
behaviroyusa konuşalım yoksa en mantıklı şekilde çöz")*: ekran ve davranış değişmez, hata giderilir.
Kural 414'teki gibi: sebep bulunmadan düzeltme yazılmaz. **Bu turun kırmızı testleri sebebi
gösterir**; gösteremezlerse uygulama turu yazılmaz ve madde *"bulamadım"* diye döner.

## Olan

Fotoğraflar satırında sırası kaydedilmiş referanslar varken Videolar satırında bir referans
sürükleniyor. Videoların yeni sırası kaydediliyor, ama fotoğrafların kaydı gidiyor: fotoğraflar
adlarına göre diziliyor, ve adı önce gelen fotoğraf 1 numaraya geçiyor. **Olması gereken:** yalnız
sürüklenen satırın sırası değişir; öteki satırlar kayıtlı sıralarında kalır, sunucu yeniden
başlayınca da.

## Sebep — izden, kodla

**Yol:** Bırakmada ekran yalnız sürüklenen satırın yeni sırasını gönderiyor
*(`saveReferenceOrder(project, { [kind]: placed })`,
[ReferencePanel.jsx:219](../../../queen-editor/frontend/src/features/photo_generation/ReferencePanel.jsx))*
→ `PUT …/references/order` → `save_reference_order` sıra belgesini *(`references.json`)* yalnız
gönderilen tiplerden kurulan yeni bir sözlükle baştan yazıyor; belgede kayıtlı olanı hiç okumuyor
*([save_reference_order.py:24-25](../../../queen-editor/backend/features/photo_generation/domain/usecases/save_reference_order.py))*
→ `list_references` → `references.placed`. `placed` belgede satırı olmayan bir tipin bütün
dosyalarını **ad sırasıyla** diziyor
*([references.py:89-90](../../../queen-editor/backend/features/photo_generation/domain/references.py))*.

**Sonucu:** Videolar sürüklenince belgede yalnız `video` kalıyor; `picture` ve `audio` satırları
siliniyor. Fotoğraflar ve sesler ad sırasına dönüyor — 414'teki görüntü, başka bir tetikle. Madde
300'den beri böyle: o zaman sırayı yalnız sürükleme yazıyordu, ve başka bir satırın sürüklenmesi bu
satırın sürüklenmiş sırasını siliyordu. 414'ten beri her yükleme de satırını yazıyor, yani hata artık
hiç sürükleme yapılmamış bir fotoğraf satırını da vuruyor.

**Elenenler:**
- **Ekran yuvaya karar vermiyor.** Sunucunun cevabını çiziyor, numarası `row.slot`
  *(ReferencePanel.jsx:93, 244, 254)*. Yalnız sürüklenen satırı göndermesi tasarımın sözleşmesi
  *("the whole row goes down"* — [api.js:289-290](../../../queen-editor/frontend/src/shared/api.js),
  ve ekran testi `sends the order a drag makes`)*: bir satırın sırası o satırın bütünüdür.
- **Belgenin deposu suçsuz.** `DriveReferenceOrderStore.write` kendisine verileni yazıyor
  *([reference_order_store.py](../../../queen-editor/backend/features/photo_generation/data/reference_order_store.py))*;
  belgenin içine ne gireceği use case'in kararı.
- **Yükleme ve silme öteki satırları koruyor.** İkisi de belgeyi önce okuyor: yükleme yalnız
  dosyanın geldiği satırı yeniden yazıyor, silme yalnız silinen adı çıkarıyor *([add_references.py:72-75](../../../queen-editor/backend/features/photo_generation/domain/usecases/add_references.py),
  [remove_reference.py:19-20](../../../queen-editor/backend/features/photo_generation/domain/usecases/remove_reference.py))*.
  Okumadan yazan tek yol sürükleme.

**İz bu turda sebep sayılmıyor:** aşağıdaki iki test kullanıcının yolunu gerçek kodla yürür. Bugün
kırmızı olmaları ve **kırmızı oldukları yer — fotoğrafların ad sırasına dönmesi, belgede yalnız
sürüklenen satırın kalması** — sebebi kanıtlar.

## Kurallar

1. **Bir satırı sürüklemek yalnız o satırın sırasını değiştirir.** Öteki satırlar kayıtlı
   sıralarında kalır.
2. **Yeniden başlatınca da aynı** — sıra diskte *(FOUNDATION 2)*.
3. **Sürüklenen satırın yeni sırası kaydedilir** — bugünkü gibi, süzgeciyle *(madde 321)*.

## Nasıl kanıtlanıyor

- **Kapı testi gerçek klasörle:** `test_reference_routes.py`'nin sunucusu — `DriveStorage`,
  `DriveReferenceStore`, `DriveReferenceOrderStore`, gerçek kapı. Dosyalar ekranın gönderdiği
  biçimde yükleniyor: tek dosya, satırın tipiyle. Sıra ekranın gönderdiği biçimde: yalnız
  sürüklenen satır. İkinci sunucu yeniden başlatmanın kendisi.
- **Use case testi sahte portlarla** *(CODE-STANDARD, Tests)*: üç satır, biri sürükleniyor.
- Ekran testi yok: ekran sunucunun cevabını çiziyor, ve gönderdiği değişmiyor.

## Yazılacak testler

### `backend/tests/test_reference_routes.py`

**`pick`** yardımcısı satırın tipini de alır — `kind="picture"` varsayılan, Videolar'ın Ekle kartı
için `kind="video"`. Bugünkü çağrılar değişmez.

1. **`test_dragging_the_videos_leaves_the_pictures_where_they_stood`** — Fotoğraflar'a `zeynep.png`,
   sonra `ayse.png` *(ikincisi adıyla önce gelir; 414'ten beri yükleme satırı yazıyor)*; Videolar'a
   `bir.mp4`, sonra `iki.mp4`. Videolar sürükleniyor: `{"video": ["iki.mp4", "bir.mp4"]}`. Cevapta
   `[("zeynep.png", 1), ("ayse.png", 2), ("iki.mp4", 1), ("bir.mp4", 2)]`; ikinci sunucu da aynısını
   okuyor.

### `backend/tests/test_reference_usecases.py`

2. **`test_a_dragged_row_leaves_every_other_row_as_it_was_saved`** — havuzda üç satır, belgede üçü
   de ad sırasının tersiyle kayıtlı: fotoğraflar `zeynep.png, ayse.png`, videolar
   `iki.mp4, bir.mp4`, sesler `rüzgar.wav, kuş.wav`. Videolar `bir.mp4, iki.mp4` diye
   sürükleniyor. Belge: fotoğraflar ve sesler olduğu gibi, videolar yeni sırasıyla; cevaptaki yuvalar
   da öyle.

### Değişen testler — yok

`test_the_order_the_user_dragged_is_stored`, `test_a_sent_order_keeps_only_the_names_the_pool_holds`
ve `test_the_order_is_saved_and_read_back` belgede tek satırla çalışıyor: kural 1'le de söyledikleri
aynı, bugün de yeşil.

## Kırmızı beklenen

- 1 ve 2 kırmızı: fotoğraflar `ayse.png` 1, `zeynep.png` 2; belgede yalnız `video` satırı.
- Öteki her şey yeşil; öteki üç satır yeşil.

## Bilinçli olarak yapılmayan

- Ekran değişmiyor; frontend testi yok.
- Öteki satırların belgedeki adlarına dokunulmuyor: dosyası Drive'dan elle silinmiş bir ad orada
  kalabilir, ve `placed` onu saymaz *(madde 321)*; o satırın kendi yüklemesi ya da silmesi onu
  temizler *(madde 414)*.
- `dist`'e ve yol haritasına dokunulmuyor.
