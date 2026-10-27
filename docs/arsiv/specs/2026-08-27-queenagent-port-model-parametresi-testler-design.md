# `Engine` portundaki ölü `model` parametresi · **test turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5`
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod yazılmaz.
**Madde numarası yok:** bu bir yol haritası maddesi değil, Madde 82'den kalan bir artığın
temizliği. Sayaç 95'te duruyor ve bu iş onu harcamıyor.

---

## Ne bozuk

[`domain/ports.py`](../../../queen-agent/backend/features/workspace/domain/ports.py) `Engine`'in iki
yöntemini de `model: str | None = None` alıyormuş gibi tanımlıyor, ve `complete`'in docstring'i
*"The model travels with the call because it belongs to the chat, not to the wiring"* diyor.

Madde 82 model seçicisini kaldırdı: tek model var ve adı `config.py`'de bir kez geçiyor. O günden
beri `model` arka uçta **yalnız bu dosyada** duruyor — `XaiEngine` almıyor, `XaiClient` almıyor,
testlerdeki sahteler almıyor. Yani port, kendi adaptöründe bulunmayan bir imza vaat ediyor.

Kimse çağırmadığı için hiçbir şey kırılmıyor, ve tam olarak bu yüzden kimse görmedi.

## Neden bu bir testle çözülüyor

Bir `Protocol` gövdesiz duruyor, yani koşarak yakalanmıyor. Ama **imzası okunabiliyor**. Sürüklenmeyi
gören ölçü de bu: portun söz verdiği parametre adları ile adaptörün gerçekten aldıkları.

Karşılaştırma gerçek adaptöre karşı yapılıyor, sahtelere karşı değil. Port, alanın neye ihtiyacı
olduğunu anlatmak için var; cevabı veren şey adaptör, ve ikisinin ayrıldığı yer hatanın yaşadığı yer.

## `backend/tests/test_ports.py` — yeni dosya

Portun bugün hiç test dosyası yok. Sürüklenmenin sebebi de bu, ve dosyanın doğması çözümün yarısı.

| Test | Ölçü | Bugün |
|---|---|---|
| `..._asks_for_what_its_adapter_takes[complete]` | imzalar eşit | **kırmızı** — port fazladan `model` |
| `..._asks_for_what_its_adapter_takes[stream]` | imzalar eşit | **kırmızı** — aynısı |
| `..._no_longer_hands_a_model_to_the_call` | kaldırılan cümle docstring'de yok | **kırmızı** |

Üçüncüsü ayrı duruyor çünkü imza testi docstring'i zorlamıyor: parametre gidip cümle kalabilir, ve
o hâlde dosya artık doğru olmayan bir şeyi söylemeye devam eder. Cümle silinmek yerine
**gözetleniyor** — depoda zaten kullanılan biçim, eski söz sessizce geri gelmesin diye.

## Kapsam dışı, ama bulundu

`Engine.complete`'i alanda **hiçbir şey çağırmıyor**: `stream_answer` `stream` kullanıyor, ve
`.complete(` yalnız `XaiEngine`'in kendi içinde ve testlerde geçiyor. Yani port, alanın ihtiyaç
duymadığı bir yöntem tanımlıyor.

Bu gerçek bir bulgu ama başka bir karar: `complete` portan çıkacaksa adaptörden ve istemciden de
çıkması gerekir mi, yoksa test edilmiş çalışan bir yol olarak kalır mı. Kendi turunu istiyor, ve bu
turda açılmıyor — bir imzayı düzeltmekle bir yöntemi silmek aynı iş değil.

## Beklenen kırmızı

**Üç.** **İki kırmızı bu işin değildir:** `test_notebook`'un ikisi.

## Nasıl görülür

```
python -m pytest queen-agent -q
```

Ön yüz açılmıyor, `dist` derlenmiyor.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `ports.py` bu turda açılmaz.
- **`xai_engine.py`, `client.py` açılmaz** — ikisi de zaten doğru; yanlış olan sözleşme.
- **`complete` silinmez.**
