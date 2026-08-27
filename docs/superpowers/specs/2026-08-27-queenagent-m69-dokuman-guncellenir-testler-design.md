# Madde 69 — Doküman güncellenir, yeniden yaratılmaz · **test turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası, Madde 69](../plans/2026-08-25-queenagent-v5-roadmap.md)
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod yazılmaz.

---

## Ne bozuk

Model var olan bir belgeyi düzeltmesi gerektiğinde çoğu zaman `create_file` çağırıyor. O araç asla
üstüne yazmıyor: `unique_name` devreye giriyor ve yanına `bar-scene-2.md` doğuyor. Sonuçta aynı işin
iki sürümü duruyor, ve bir sonraki adımın hangisini okuyacağı belirsiz.

Yerinde değiştiren bir yol zaten var — `edit_file`. Eksik olan, onu kullanmanın **modelin seçimine**
bırakılmış olması. Yönergeye *"onu kullan"* yazmak FOUNDATION'ın 5. ilkesine çarpıyor: modelin her
seferinde tekrarlaması gereken şeyi kod yapar.

## Karar: dolu bir ada yazılmaz, reddedilir

*(kullanıcı kararı, 27 Ağustos — sunulan iki seçenekten birincisi)*

Aynı adda dosya varken `create_file` **hiçbir şey yazmıyor** ve modele bu adda bir dosya olduğunu,
değiştirmek için `edit_file`'ı, yeni bir belge için başka bir adı kullanması gerektiğini söylüyor.

Neden bu, üstüne yazıp eskisini çöpe atmak yerine:

- **1. ilkeyle hiç pazarlık etmiyor.** Hiçbir şey yok edilmediği için geri alınabilirliğe dayanmasına
  gerek kalmıyor. Üstüne yazma sessiz bir sürpriz olurdu — geri alınabilir, ama yine de sürpriz.
- **5. ilkeyi yerine getiriyor.** Karar yönergeden koda iniyor. Model `edit_file` kullanmayı
  *unutamaz*, çünkü `create_file` o işi artık yapmıyor.
- **Bedeli bir fazladan tur**, ve o turun yönergesi araç cevabının kendisi.

**Numaralı kopya ölmüyor:** `unique_name` yerinde kalıyor, çünkü çöp onu kullanıyor — aynı ad iki
kez silindiğinde. Ölen şey `create_file`'ın onu çağırması.

**Araç tarifi de söylüyor.** Reddi kod garanti ediyor, ama tarif onu önceden söylerse olağan durumda
o fazladan tur hiç yaşanmıyor. Bu bir *özen ricası* değil, aracın ne yaptığının tarifi — `write_plan`
zaten aynı biçimde *"Writes over the plan of that name if there is one, so read it first"* diyor.

## Kesikli kart da bu maddede iniyor

*(kullanıcı kararı, 27 Ağustos — sunulan iki seçenekten birincisi)*

Dosya yazan bir araç çağrıldığında `stream_answer` önce `FileStarted` veriyor: ad, araç koşana kadar
belli değil. Tarayıcı onu görünce kesikli kartı kaldırıyor ve **yalnız `file` karesiyle** indiriyor.
Dosya doğmayan bir çağrıda kart tur bitene kadar havada kalıyor.

Bu bugün de var — plan üstüne yazıldığında (91) ve `build_prompts` reddettiğinde. Ama nadir. **69 onu
olağan hâle getiriyor:** artık her *"şu belgeyi düzelt"* turu önce bir ret alıyor.

Ölçü hazır: her araç çağrısından sonra `call` karesi zaten geliyor. Kesikli kartın ömrü tam olarak
*"model istedi"* ile *"araç cevapladı"* arası, ve `call` ikincisinin ta kendisi. Sıra her zaman
doğru — `file-start → (file) → call` — yani `call` gelince kartı indirmek hiçbir durumda erken
olmuyor.

69'un yarattığı bir hata değil, 69'un görünür kıldığı bir hata; ayırmak bilerek kırık bir ara durum
bırakmak olurdu.

## Testler nasıl kırmızı olur

### `backend/tests/test_tools.py`

| Test | Ölçü | Bugün |
|---|---|---|
| `..._over_a_name_that_is_taken_writes_nothing` | eski içerik yerinde, listede tek ad | **kırmızı** — ikinci dosya doğuyor |
| `..._points_at_the_tool_that_can_do_it` | cevapta `edit_file` geçiyor | **kırmızı** |
| `..._brings_no_file_into_being` | `created is None` | **kırmızı** — `plan-2.md` |
| `..._names_the_file_that_was_in_the_way` | `target == "plan.md"` | **kırmızı** — `plan-2.md` |
| `..._does_not_say_it_saved` | `outcome == "Already there"` | **kırmızı** — `Saved` |

**Silinen iki test**, konularını kaybettikleri için: `test_creating_reports_the_name_actually_used`
ve `test_a_created_file_reports_the_name_it_actually_got`. İkisi de numaralı kopyayı tarif ediyor.

Boş bir ada yazmanın testleri — kaydedildiği, kart doğurduğu, *"Saved"* dediği — dokunulmadan
duruyor ve yeşil kalıyor. Değişen şey **dolu bir ad**, boş olan değil.

### `frontend/src/App.test.jsx`

| Test | Ölçü | Bugün |
|---|---|---|
| `a call frame takes the dashed card down` | akış sürerken `creating file…` yok | **kırmızı** |

`gatedSse` yardımcısı bunun için zaten var: ilk kareler verilir, akış açık tutulur, ve iddia cevap
hâlâ koşarken ölçülür. Kareler `chat` → `file-start` → `call`, `file` yok — reddedilen bir yazma tam
olarak bu.

## Beklenen kırmızı

**Arka uç 5, ön yüz 1.** Altı.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Nasıl görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

`dist` bu turda derlenmiyor: ön yüz kaynağı yalnız testte değişiyor.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `tools.py` ve `useChat.js` bu turda açılmaz.
- **`edit_file` değişmez** — bugünkü hâliyle doğru çalışıyor; eksik olan ona gidilmesiydi.
- **`unique_name` silinmez** — çöp onu kullanmaya devam ediyor.
- **`write_plan` ve `build_prompts` değişmez** — ikisinin de üstüne yazma kuralı kendi gerekçesini
  taşıyor, ve bu madde `create_file`'ı konuşuyor.
- **Diskte duran numaralı kopyalar temizlenmez** — bugüne kadar doğmuş `-2` dosyaları yerinde kalıyor.
