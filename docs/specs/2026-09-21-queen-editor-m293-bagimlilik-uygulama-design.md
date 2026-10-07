# Madde 293 — Bağımlılık tek kurala iniyor, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m293 test turu](2026-09-21-queen-editor-m293-bagimlilik-testler-design.md),
`e58cb037` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## Kural nereye yazılıyor

`domain/layers.py` — *"hangi katman neye bağlı"* katmanın kendi bilgisi, ve `domain/` dışarıdan
hiçbir şey import etmiyor *(CODE-STANDARD)*.

```
NEEDS = {AUDIO: VIDEO}        # bir katman ve altında olmak zorunda olan katman
```

Tablo **eksiltili**: bağlı olmayan katman tabloda yok. Her katman için bir satır yazıp ikisine `None`
koymak aynı şeyi söylerdi, ama o zaman *"fotoğraf serbest"* bir satır olurdu — oysa asıl söylenen,
onun hakkında söylenecek bir şey olmadığı.

`falls_with(kind)` tabloyu ters yönde okur: katmanın kendisi, ona bağlı olanlar, ve onlara bağlı
olanlar. Bugün zincir iki halka *(video → ses)*, ama okuma özyinelemeli yazılır — tabloya üçüncü bir
satır eklendiğinde `remove_layer`'ın değişmesi gerekmesin diye. Sıra **`queue.ORDER`'ın sırası**:
silme kayıtlara o sırayla yazıyor ve testler o sırayı okuyor.

## Üç okuyucu

**1. `layers.can_produce`.** `if slot == AUDIO: return is_taken(slots.get(VIDEO))` yerine tablodan
okunan tek satır: `under = NEEDS.get(slot)`, varsa dolu olmalı. Davranış aynı — `test_layers.py`'ın
bugünkü `can_produce` testleri bunun bekçisi.

**2. `queue_layer.frames_in_scope`.** Ses özel durumu tablodan okunur. Kapsamda bir fark var ve
korunur: burada **bozuk** katman da altında yok sayılır *(`VIDEO in broken`)* — üstüne ses
binmemesi için. `can_produce` orada `is_taken` ile *"kırmızı katman yuvayı doldurur"* diyor; bu iki
cümle çelişmiyor, iki ayrı soruya cevap veriyor: *"yuva boş mu"* ve *"altında sağlam bir şey var
mı"*. Kapsam ikincisini sorduğu için kontrolü kendi cümlesiyle sorar, ama **hangi katmanın altında**
olduğunu artık tablodan öğrenir.

Aynı fonksiyondaki `frame["status"] != "done"` kontrolü **duruyor**: o fotoğraf kuralı değil,
*"kartın kendisi yerleşmiş mi"* kuralı — ve madde 292'den beri kartı **açan** katmanı okuyor. Yorumu
düzeltilir, çünkü bugün *"yalnız üretilmiş bir fotoğraf bir şey taşıyabilir"* diyor.

**3. `remove_layer`.** `over = queue.ORDER[queue.ORDER.index(kind):]` yerine
`over = layers.falls_with(kind)`. Maddenin görünen değişikliği burada: fotoğraf silinince video
kalıyor.

## Kıpırdamayacaklar

- **Arayüz.** `REMOVABLE` ve `QUEUEABLE` bugünkü hâlinde: fotoğraf hâlâ ekrandan silinemiyor, ve
  fotoğraf işi hâlâ katman olarak kuyruğa verilemiyor. Fotoğrafın silinebilir bir katman olması
  **294**, ve bu maddenin işi o kapı açıldığında arkasında doğru kuralın durması.
- **Üretici.** Standart video hâlâ kaynak fotoğrafla render ediliyor; referans kipi **304**'te
  geliyor. Bu madde kuralı taşıyor, üreticiyi değil.
- **`queue.ORDER`.** Motorun çalışma sırası olarak yerinde duruyor — bağımlılık olarak okunması
  bırakılıyor. İkisi bugün aynı görünüyor, ve ayrıldıkları yer tam olarak bu maddenin düzelttiği yer.

## Belgeler

Üç dosyanın başındaki açıklama bugün kuralı kendi cümlesiyle anlatıyor ve **çelişkide yorum koda
uydurulur** *(stil kuralı)*:

- `layers.py`: yığın cümlesi yerine tabloya işaret eder.
- `remove_layer.py`: *"katman ve üstündeki her şey"* → *"katman ve ona bağlı olanlar"*; fotoğrafın
  bu kullanım senaryosunun işi olmadığını söyleyen paragraf, kuralın değil **arayüzün** kararı olarak
  yeniden yazılır *(madde 294 orayı açacak)*.
- `queue_layer.py`: *"her katman bir resme asılır"* cümlesi gider.

## Bitti sayılır

Dört satırın dördü de koşulur; `python -m pytest queen-editor -q` yeşil — turun dört kırmızısı döner
ve 960 testin hiçbiri düşmez.
