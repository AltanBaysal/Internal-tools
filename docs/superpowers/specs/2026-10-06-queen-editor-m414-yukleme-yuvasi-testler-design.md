# Madde 414 — Yüklenen resim tıklanan yuvaya, test turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 414 · v9-6 · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Madde 5 Ekim'de hizalandı: olan ve olması gereken kullanıcının
sözleri. Kuralı da onun *("bug çözerken nedenini anlaumazsan rastgeke çözüm yapma bulmadım de
lütfen")*:
sebep bulunmadan düzeltme yazılmaz. **Bu turun kırmızı testleri sebebi gösterir**; gösteremezlerse
uygulama turu yazılmaz ve madde *"bulamadım"* diye döner.

## Olan

Fotoğraflar satırında 1 numarada bir fotoğraf varken, 2. yerdeki *fotoğraf ekle* kartından yüklenen
resim 1 numaraya iniyor, eski fotoğraf 2'ye geçiyor. **Olması gereken:** yeni resim 2'ye iner, eski
1'de kalır.

## Sebep — izden, kodla

**Yol:** Ekle kartı yalnız satırın tipini gönderiyor, bir yer göndermiyor *(`uploadReferences`,
[api.js:281-287](../../../queen-editor/frontend/src/shared/api.js))* → `POST …/references` →
`add_references` dosyayı yazıyor, sıra belgesine *(`references.json`)* hiçbir şey yazmıyor
*([add_references.py:60-64](../../../queen-editor/backend/features/photo_generation/domain/usecases/add_references.py))*
→ `list_references` → `references.placed`. `placed` belgede adı geçmeyen her dosyayı satırın sonuna
**ad sırasıyla** diziyor
*([references.py:87-89](../../../queen-editor/backend/features/photo_generation/domain/references.py))*.

**Sonucu:** Fotoğraflar satırı hiç sürüklenmediyse belgede fotoğraf listesi yok, ve satırın bütün
fotoğrafları adlarına göre diziliyor. Yeni dosyanın adı eskininkinden önce geliyorsa yeni dosya 1.
yuvaya, eski 2.'ye geçiyor — kullanıcının gördüğü bu. Satır sürüklenmişse ama eski fotoğraf
sürüklemeden sonra geldiyse aynısı: ikisi de belgede yok.

**Ad sırası kolayca tutuyor:** Python'un sırası kod noktası — büyük harf küçükten, rakam harften
önce. **Aynı resmi ikinci kez yüklemek her seferinde tutuyor:** `free_name` ikinci `kadin.png`'yi
`kadin-2.png` yapıyor
*([references.py:60-64](../../../queen-editor/backend/features/photo_generation/domain/references.py))*,
ve `-` *(0x2D)* `.`'dan *(0x2E)* önce geldiği için `kadin-2.png` `kadin.png`'nin önüne düşüyor.

**Elenenler:**
- **Ekran yuvaya karar vermiyor.** Sunucunun gönderdiği sırayı çiziyor, numarası `row.slot`
  *([ReferencePanel.jsx:93, 244, 254](../../../queen-editor/frontend/src/features/photo_generation/ReferencePanel.jsx))*.
- **Yüklemeden sonra sıra gönderilmiyor:** `saveReferenceOrder` yalnız bırakmada
  *(ReferencePanel.jsx:219)*.
- **Belgede eski fotoğraf varken yeni dosya hep sona iniyor** *(`placed`'in `sequence`'i önde)* — o
  hâlde hata çıkamaz. Tek istisnası Drive'dan elle silinmiş bir adın belgede kalıp aynı adla
  yeniden yüklenmesi; o da yüklemenin sıraya yazılmamasından.

**İz bu turda sebep sayılmıyor:** aşağıdaki üç test kullanıcının yolunu gerçek kodla yürür. Bugün
kırmızı olmaları ve **kırmızı oldukları yer — yeni dosyanın 1. yuvada olması** — sebebi kanıtlar.

## Kurallar

1. **Ekle kartından yüklenen dosya kendi satırının sonuna iner; satırdakiler yerinde kalır.** Kart
   satırın son referansından sonra duruyor *(madde 320)*: tıklanan yer satırın sonu.
2. **Yeniden başlatınca da aynı** — yer diskte *(FOUNDATION 2)*.
3. **Aynı adla gelen ikinci dosya da sona iner.**

## Nasıl kanıtlanıyor

- **Kapı testleri gerçek klasörle:** `test_reference_routes.py`'nin sunucusu — `DriveStorage`,
  `DriveReferenceStore`, `DriveReferenceOrderStore`, gerçek kapı. İstek ekranın gönderdiği biçimde:
  tek dosya ve `kind=picture`. İkinci sunucu yeniden başlatmanın kendisi.
- **Use case testi sahte portlarla** *(CODE-STANDARD, Tests)*.
- Ekran testi yok: ekran sunucunun cevabını çiziyor, hata orada değil.

## Yazılacak testler

### `backend/tests/test_reference_routes.py`

Yeni yardımcı **`pick(client, name, data=b"PNG")`** — Fotoğraflar'ın Ekle kartının isteği: tek
dosya, `kind=picture`.

1. **`test_a_picture_picked_after_the_first_lands_in_slot_two`** — `zeynep.png`, sonra `ayse.png`:
   cevapta `[("zeynep.png", 1), ("ayse.png", 2)]`; ikinci sunucu da aynısını okuyor.
2. **`test_the_same_picture_picked_again_lands_in_slot_two`** — `kadin.png` iki kez:
   `[("kadin.png", 1), ("kadin-2.png", 2)]`.

### `backend/tests/test_reference_usecases.py`

3. **`test_an_upload_joins_the_end_of_its_row`** — `zeynep.png` yüklü; `ayse.png` `row=PICTURE`
   ile: cevap ve yeniden okunan havuz `[("zeynep.png", 1), ("ayse.png", 2)]`.

### Değişen testler — söyledikleri aynı, bugün de yeşil

- **`test_the_pool_carries_the_slot_each_reference_stands_in`** sırayı dosyalardan önce kuruyor:
  dosyası olmayan adlar, sonra yüklenen dosyaları eski yerlerine çekiyor. Kural 1'le yükleme
  satırın sırasını kendisi yazacak, ve dosyası olmayan ad yeni yüklemeyi çekmeyecek — `remove_reference`
  ve `save_reference_order`'ın belgelerinin istemediği şey *(madde 321)*. Test sırayı dosyalar
  yüklendikten sonra kuruyor; söylediği aynı: havuz kayıtlı sıranın yuvalarını taşır.
- **`test_the_pool_lists_in_one_stable_order`'ın belgesi** ve
  **`test_two_references_are_uploaded_listed_and_one_is_deleted`'ın yorumu** *"kimse sürüklemedikçe
  satırın içi ad sırasıyla"* diyor; kural 1'den sonra yüklenenler için doğru değil. İkisinin de
  satırında tek dosya var: yorum, söyledikleri *"satır satır"*a iniyor.

## Kırmızı beklenen

- 1, 2, 3 kırmızı: yeni dosya 1. yuvada, eski 2.'de.
- Öteki her şey yeşil; öteki üç satır yeşil.

## Bilinçli olarak yapılmayan

- Ekran değişmiyor; frontend testi yok.
- Bir basışta birden çok dosya: kart tek dosya alıyor *(madde 320)*, sıraları test edilmiyor.
- Drive'a elle konan dosya bugünkü gibi sonda, ad sırasıyla *(madde 297, 300)*.
- `dist`'e ve yol haritasına dokunulmuyor.

## Bulunan, bu maddede değil

**Bir satırı sürüklemek öteki satırların sırasını siliyor:** ekran yalnız sürüklenen satırı
gönderiyor *(ReferencePanel.jsx:219)*, ve `save_reference_order` belgeyi yalnız gönderilen tiplerle
baştan yazıyor
*([save_reference_order.py:26-27](../../../queen-editor/backend/features/photo_generation/domain/usecases/save_reference_order.py))*.
Videolar sürüklenince fotoğrafların kaydı gidiyor ve satır yine ad sırasına dönüyor — aynı görüntü,
başka bir tetik. Kullanıcının anlattığı yolda sürükleme yok; ayrı bir madde olarak koşuya bildirilir.
