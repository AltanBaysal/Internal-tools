# `Engine` portundaki ölü `model` parametresi · **uygulama turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5`
**Test turu:** [testler tasarımı](2026-08-27-queenagent-port-model-parametresi-testler-design.md) · kırmızı commit `f70a3a9`
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder. Yeni test yazılmaz.

---

## Tek dosya

`domain/ports.py`, ve içinde yalnız `Engine`. Başka hiçbir şey açılmıyor — `XaiEngine` ve
`XaiClient` zaten doğru, yanlış olan sözleşmeydi.

## `complete`

`model` parametresi ve onu anlatan paragraf gidiyor. Geriye tek cümlelik docstring kalıyor:
mesajların alanın kendi rollerini taşıdığı. Model, çağrının bir alanı değil — motorun kurulduğu
şeyin bir parçası, ve `config.py` onu bir kez söylüyor.

## `stream`

`model` parametresi gidiyor; `on_open` ve altı satırlık docstring dokunulmadan kalıyor. Docstring'in
içindeki *model* geçişleri — *"the model asks for one"*, *"the model says what the answer cost"* —
bu parametreyle ilgili değil, cevabı veren şeyden bahsediyor ve duruyor.

## Neden bir cümle daha ekleniyor

`Engine`'in kendisi artık model seçmediğini söylemiyor, ve bir sonraki okuyucu için o bir soru.
Sınıf docstring'i o soruyu kapatıyor: motorun hangi modelle konuştuğu kurulumun işi, çağrının değil.
Bu, koddan okunamayan bir şey — bir parametrenin **yokluğu** sebebini anlatmaz.

## Üç kırmızının karşılığı

| Test | Karşılığı |
|---|---|
| `..._asks_for_what_its_adapter_takes[complete]` | `complete`'ten `model` |
| `..._asks_for_what_its_adapter_takes[stream]` | `stream`'den `model` |
| `..._no_longer_hands_a_model_to_the_call` | *"travels with the call"* cümlesi |

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
```

**İki kırmızı bu işin değildir:** `test_notebook`'un ikisi.

Ön yüz açılmıyor, `dist` derlenmiyor.

## Bilerek yapılmayanlar

- **Yeni test yazılmaz.**
- **`xai_engine.py`, `client.py`, `config.py` açılmaz.**
- **`complete` silinmez** — alanın onu çağırmadığı test turunda kaydedildi ve kendi turunu
  bekliyor. Bir imzayı düzeltmek ile bir yöntemi silmek aynı iş değil.
- **Öteki üç port açılmaz.**
