# Madde 211 · Silinen işin satırı kalıyor — uygulama turunun tasarımı

**Tarih:** 13 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)
**Test turu:** [tasarım](2026-09-13-queen-editor-m211-silinen-is-testler-design.md) ·
[plan](../plans/2026-09-13-queen-editor-m211-silinen-is-test-plan.md) · kırmızı `91bc4e5`

## Düzeltme nereye ait

Üç yer düşünüldü:

| Nereye | Ne yapardı | Neden değil |
|---|---|---|
| `remove_layer` | silerken eski plan satırını da atardı | Silme tek yol değil — kuyruğu boşaltmak da hücreyi kapatıyor ve satırı bırakıyor. Aynı hata ikinci bir kapıdan geri gelirdi. |
| `queue_layer` | yeni satır eklemek yerine eskisini değiştirirdi | Plan deposunun sözleşmesinde *([ports.py](../../../queen-editor/backend/features/photo_generation/domain/ports.py))* yalnız `read` ve `append` var. Satır değiştirmek portu, iki gerçeklemeyi ve her sahteyi büyütür — hatanın büyüklüğüyle orantısız. |
| **`open_jobs`** | aynı çiftin yalnız **son** satırını borç sayar | **Seçilen.** |

Sebebi bir kaçış değil, tanımın kendisi: durum **(kare, katman) başına tek hücre**. Tek hücre varsa o
çifte borç da tektir, ve borçlu olunan şey **en son istenen**. `open_jobs` zaten *"kuyruk neyi
borçlu"* sorusunun cevabı, yani kuralın yaşaması gereken yer orası.

Plan dokunulmadan kalıyor, ve bu doğru: plan **ne istendiğinin** kaydı. Üç kez istenip iki kez
silinmiş olması gerçekten olmuş bir şey, ve onu silmek geçmişi düzeltmek olurdu.

## Ne değişiyor

`open_jobs` her tür için satırları süzerken, aynı kareye ait satırlardan yalnız sonuncusunu tutar.
Sıra bozulmuyor: liste planın kendi sırasında yeniden kuruluyor, o karenin **son** satırının durduğu
yerde. `sorted` kararlı olduğu için galerinin sırası da eskisi gibi belirleyici.

Bu tek değişiklik kırmızının üçünü birden yeşile çeviriyor:

- `owed` tek satır döner → kart bir kez *"video üretiliyor"* der;
- üç tur da tek satır bırakır;
- **üretilen iş son istenen olur** → loop istenince loop çıkar, silinmiş standart geri gelmez.

## Sınırda duran bir şey — kapsam dışı

`counts` *(aynı dosya)* kuyruk toplamını `len(jobs)` ile sayıyor, yani **eskimiş satırları da**
sayıyor. Sil-ve-yeniden-ekle sırasından sonra ekrandaki toplam olduğundan büyük kalıyor. Aynı kökten
gelen üçüncü bir belirti, ama kullanıcının bildirdiği şey değil ve maddenin kabul cümlesinde yok —
kendi kırmızısını hak ediyor. Buraya yazıldı ki kaybolmasın; koşu sonunda kullanıcıya sorulacak.

## Dokunulmayanlar

- **14 Ağustos'un düzeltmesi.** `queue_layer`'ın settled hücreye `queued` yazması yerinde kalıyor.
  Hatanın kaynağı o satır değil, o satırın tek hücreye bakan birden çok plan satırını birden açması.
  Üç çivisi de bu turda yeşil kalmak zorunda.
- **Plan deposu, portu, ve sahteleri.**
- **`next_job`, `cancel_generation`, `resume_batch`** — hepsi `open_jobs`'u çağırıyor, yani düzeltmeyi
  kendiliğinden alıyorlar.

## Değişen

[queue.py](../../../queen-editor/backend/features/photo_generation/domain/queue.py). Ön yüz
değişmiyor, `dist` de derlenmiyor.
