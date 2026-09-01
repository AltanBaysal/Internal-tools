# Defterin adı aracının adı olsun · Tur 1 (test) — Tasarım

**Kaynak:** Kullanıcının isteği *(1 Eylül)*: "queen-editor'ün defterinin adı şu an `app.ipynb`,
adını düzgün yazalım."
**Numarasız:** Madde sayacı QueenAgent'ın ürün yol haritasının; bu iş iki aracın deposuna dokunuyor.
**Dal:** `feat/defter-adi`.

## Sorun

`queen-editor`'ün defteri `app.ipynb` adını taşıyor. Bu ad aracın hangisi olduğunu söylemiyor, ve
söylememesinin bir bedeli var — bedeli de zaten yazılı. `queen-agent`'ın defter testinde, kendi
defterinin neden `queenagent.ipynb` olduğunu anlatan yorum şunu diyor
([test_notebook.py](../../../queen-agent/backend/tests/test_notebook.py)):

> Not app.ipynb: queen-editor's notebook is called that, and Colab shows a notebook by its file
> name alone. Two tabs both saying app.ipynb are two tabs nobody can tell apart, and pressing
> Run all in the wrong one clones the wrong repo and starts the wrong app.

Yani gerekçe düşünülmüş ve yazılmış; yalnız queen-editor tarafına hiç uygulanmamış. Colab bir defteri
sekmede **yalnız dosya adıyla** gösterir — defterin içindeki `# Queen Editor — Colab kurulumu`
başlığı *(v8 · Görev 3'te düzeltilmişti)* sekmeye çıkmaz. İki araç aynı anda açıkken ayırt edici
olan tek şey dosya adı, ve `app.ipynb` hiçbir şey ayırt etmiyor.

## Kural

**Bir aracın defteri, aracının adını taşır — tireler düşer.** `queen-agent` → `queenagent.ipynb`,
`queen-editor` → `queeneditor.ipynb`.

Klasör adının kopyası değil, türevi: kural klasör adından okunuyor, o yüzden bir araç yeniden
adlandırılırsa kural onunla gelir. Ve tire düşmesi keyfî değil — `queenagent.ipynb` bugün öyle
duruyor, kural o yerleşmiş biçimi tarif ediyor.

Kural yalnız bu iki araca bakıyor. `collab-toolbox` kapsam dışı: orada `api.ipynb` ve `manual.ipynb`
kasten tekrar eden adlar, çünkü onlar bir uygulamanın kurulum defteri değil, bir klasörün içindeki
iki kullanım biçimi.

## Bu turun testleri

Bugünkü testlerin hiçbiri adı korumuyor. İkisinde de defterin yolu bir sabit
*(`NOTEBOOK = .../app.ipynb`)*, ve bir sabit her adla yeşil kalır — sabiti değiştiren, kuralı da
değiştirmiş olur. Yani ad, yalnız bir yorumun koruduğu şey. **Bu turun asıl işi o yorumu teste
çevirmek**; dosyanın taşınması ikinci turda.

Her iki aracın kendi defter testine, klasör adından türeyen tek bir test giriyor:

```python
def test_the_notebook_carries_the_tool_s_own_name():
    found = sorted(n for n in os.listdir(TOOL) if n.endswith(".ipynb"))
    assert found == [os.path.basename(TOOL).replace("-", "") + ".ipynb"]
```

- `queen-editor` → **kırmızı**: `['app.ipynb'] != ['queeneditor.ipynb']`.
- `queen-agent` → **yeşil daha ilk anda**, çünkü kural orada zaten tutuyor. Bu turun kırmızısı
  değil, kuralın ikinci ayağı: bugüne kadar yalnız bir yorumdu, bundan sonra bir bekçi. Yorumun
  kendisi ikinci turda düzeltilecek — bu tur yalnız test dosyalarına dokunuyor, ve o yorum
  yeniden yazıldığında dayanağı test olacak.

Ayrıca queen-editor'ün `NOTEBOOK` sabiti ve ön yüzün kullanıcıya gösterdiği metni bekleyen test,
yeni adı bekler hâle geliyor — ikisi de bu turda kırmızıya döner:

- `test_notebook_installs_the_producer_groups.py` — sabit `queeneditor.ipynb`'yi gösterince dosya
  bulunamaz; o dosyadaki testlerin tamamı kırmızı.
- `QueuePanel.test.jsx` — panelin bastığı cümle *"…defterinden kurulur — app.ipynb'de kutusunu
  işaretleyip çalıştır"* yeni adı bekler; kaynaktaki metin *(`useProducers.js`)* ikinci turda
  değişeceği için şimdi kırmızı.

## Ayakta kalması gerekenler

Dört test komutunun tamamı. queen-agent'ın iki koşusu ve queen-editor'ün ön yüzünün geri kalanı bu
turda hiç sarsılmamalı.

## Bilerek yapılmayanlar

- **`docs/superpowers/` altındaki plan ve spec'lerde `app.ipynb` aramak.** Onlar o günün kaydı; bir
  kayıt geriye dönük yazılmaz. Bugünü anlatan dosyalar düzeltilir, geçmişi anlatanlar durur.
- **Deponun tamamında defter adı tekilliği aramak.** Yukarıdaki gerekçe: `collab-toolbox` başka bir
  şey yapıyor.
- **Defteri bu turda taşımak.** Taşıma uygulama turunun işi; şimdi taşınırsa kırmızı diye bir şey
  kalmaz.
