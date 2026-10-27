# Madde 211 · Silinen işin satırı kalıyor — test turunun tasarımı

**Tarih:** 13 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan alınan

Yol haritası sebebi yazmamıştı, ve bu maddenin **kullanıcıdan gereken**i buydu. 13 Eylül'de soruldu:

| Soru | Cevap |
|---|---|
| Silinen standart video hangi durumdaydı? | **Henüz kuyruktaydı / üretiliyordu** |
| "İkisi birden" ekranda nasıl göründü? | **Tek kare**, ama kartın üstünde *"video üretiliyor"* **alt alta iki kez** — durdurup bir daha eklenince **üç kez** |
| Dışa aktarmaya kaç video düştü? | **Bakılmadı** |

Üçüncüsüne gerek kalmadı: sebep bulununca diske ulaşıp ulaşmadığı mekanizmadan okunuyor.

## Sebep — bulundu, tahmin değil

Durum kaydı **(kare, katman) başına tek hücre** tutuyor
*([queue.py `_status`](../../../queen-editor/backend/features/photo_generation/domain/queue.py))*, ama plan
aynı çift için **birden çok iş satırı** taşıyabiliyor. `open_jobs` her satırın durumunu o tek
hücreden okuyor, yani hücre `queued` olduğu an o çifte ait **bütün** satırlar birden açılıyor.

Sıra şöyle işliyor
*([queue_layer.py:132-143](../../../queen-editor/backend/features/photo_generation/domain/usecases/queue_layer.py))*:

1. Video kuyruğa girer → plana bir satır, hücreye bir şey yazılmaz.
2. Katman silinir → `remove_layer` hücreye `removed` yazar. **Plandaki satır durmaya devam eder.**
3. Video yeniden eklenir → hücre `queued` olur ve plana **ikinci bir satır** eklenir.
4. `open_jobs` iki satırı da açık görür → `owed` listesi `["video", "video"]` → kart iki *"video
   üretiliyor"* çizer. Bir kez daha yapılınca üç.

**Görüntüyle sınırlı değil, ama sandığım biçimde de değil.** Kırmızı koşulunca ortaya çıkan şey daha
keskin: motor iki video **üretmiyor**. İlk iş bitince hücre `done` oluyor, ve aynı hücreye bakan
öteki satırlar da onunla birlikte kapanıyor — yani tek video çıkıyor. Çıkan video **eski satırın**
videosu oluyor: plan sırayla okunuyor ve önce yazılan satır önce alınıyor.

Sonuç, kullanıcının gördüğünden daha kötü: loop istenip **standart üretiliyor**, ve silinmiş olan iş
sessizce geri geliyor. Kırmızının kendi cümlesi bunu söylüyor — `assert 'standard' == 'loop'`.

Kartta biriken satırlar da gerçek, ama geçici: ilk iş bitene kadar duruyorlar. Kullanıcının
*"durdurup bir daha ekledim, üç oldu"* demesinin sebebi bu — durdurunca hiçbiri bitmiyor, hepsi
birikiyor.

**Bu bir düzeltmenin arta kalanı.** 3. adımdaki `queued` satırı, 14 Ağustos'ta bildirilen *"kuyruk
boşaltılınca ses bir daha eklenemiyor"* hatasının çözümü — kodun kendi yorumu bunu yazıyor. O çözüm
yeni satırı görünür kılarken, aynı hücreye bakan eski satırları da dirilttiği fark edilmemiş.

## Hiçbir test neden yakalamadı

İki çivi tam bu senaryonun adını taşıyor — `test_a_sound_pulled_out_of_the_queue_can_be_asked_for_again`
ve video'nunki — ama kurdukları dünyada **plan o katman için hiç satır taşımıyor**:
`settled_slot_project` plana yalnız kareyi koyuyor, hücreyi `removed` yapıyor. Tek satır olunca ikinci
satır da olmuyor, ve hata görünmüyor.

Yani eksik olan çivi değil, **kurulan hâl**: hatanın yaşadığı yer, planın o çift için zaten bir satır
taşıdığı durum.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Kuyruktan çıkarılmış bir video yeniden istenince kare **bir** video borçlanır | **kırmızı** — `['video', 'video']` |
| 2 | Sıra üç kez tekrarlanınca da bir tane kalır | **kırmızı** — dört |
| 3 | Tek video üretilir | yeşil, ve öyle kalmalı |
| 4 | Üretilen video **son istenen modu** taşır | **kırmızı** — `'standard' == 'loop'` |
| 5 | 14 Ağustos'un çivileri ayakta kalır | yeşil, ve öyle kalmalı |

Dördüncüsü maddenin kabul cümlesinin kendisi, ve hatanın asıl zararı: sıra *standart eklendi →
silindi → loop eklendi*, ve karenin eline geçen şey **standart**.

Üçüncüsü kırmızı değil, ve olmaması bir bilgi: tek video çıkıyor, yalnız yanlış olanı. Düzeltme onu
bozabilecek biçimlerde yazılabilir *(örneğin eski satırları kapatmak yerine yenisini öne almak)*, o
yüzden çivisi var.

Beşincisi bu turun asıl riski. Hatanın kaynağı bir düzeltme olduğu için, düzeltmeyi geri almak kolay
ve yanlış bir çıkış yolu — o çiviler geri almanın önünde duruyor.

## Ölçü, planın içeriği değil

`test_a_sound_pulled_out…`'ın kendi cümlesi: *"Not the plan's contents: whether the sound was actually
made."* Aynı ölçü burada da geçerli — sayılacak şey üreticinin **kaç kez çağrıldığı** ve galerinin
kareye **kaç iş borçlu göründüğü**. Planın kaç satır taşıdığı bir uygulama ayrıntısı, ve onu çivilemek
düzeltmenin biçimini şimdiden seçmek olurdu.

## Bu turda değişen

Yalnız [test_photo_usecases.py](../../../queen-editor/backend/tests/test_photo_usecases.py): hatanın
yaşadığı hâli kuran bir yardımcı ve dört çivi. Kaynak kod uygulama turunun işi.
