# Madde 183 · test turu — prompt yazan model Grok 4.3 olur

**Kaynağı:** [yol haritası, Madde 183](../plans/2026-09-06-queenagent-v8-roadmap.md).
v8'in ilk maddesi, `feat/queenagent-v8`'in ilk kodu.

---

## Ne kanıtlanacak

`config.PROMPT_MODEL` `grok-build-0.1` yerine **`grok-4.3`** olur, ve eski satır `MODELS`'ten
**kalkar**. Kimlik doğrulandı: xAI'ın kendi model listesinde duruyor *(docs.x.ai/docs/models,
6 Eylül)*. O string doğrudan sağlayıcıya gidiyor — `client.py`'nin `payload["model"]`'i — yani
kanıtlanacak şey bir takma adın çözülmesi değil, **config'in doğru adı taşıması.**

## Taramanın söylediği: iki yerde `grok-4.3` zaten var, ve ikisi de yanlış tarafta

Depoda `grok-4.3` bugün **bilinmeyen model** örneği olarak kullanılıyor:

- `test_config.py`'de *"bilinmeyen bir ad varsayılana düşer"* testinin örneği.
- `test_xai_engine.py`'de *"kablolanmamış bir model istenirse varsayılan yanıtlar"* testinin örneği.

İkisi de bu maddeden sonra **yanlış sebeple** geçer: ad artık bilinen bir ad, ve test onu bilinmeyen
sanarak yeşil kalır. İkisinin örneği **hiçbir zaman model olamayacak** bir adla değişiyor —
`a-model-nobody-wired`. Bir örneğin işi bir şeyi göstermek, ve gösterdiği şey değiştiyse örnek
değişir.

## Yedi test

`test_config.py`:

| # | Test | Ne söylüyor |
|---|---|---|
| 1 | `PROMPT_MODEL` `grok-4.3`'tür | maddenin kendisi |
| 2 | `grok-4.3` tabloda | yazar kablolanmamışsa ilk karede `KeyError` |
| 3 | Adresi ve anahtarı | `https://api.x.ai/v1`, `XAI_API_KEY` |
| 4 | **`grok-build-0.1` tabloda yok** | silmenin kanıtı bir yokluk, ve onu ancak arayan test görür |
| 5 | Bilinmeyen ad hâlâ varsayılana düşer | örneği değişti, kuralı değil |

`test_xai_engine.py`:

| # | Test | Ne söylüyor |
|---|---|---|
| 6 | Motorun fikstürleri ölü bir kimlik taşımaz | `DEFAULT` ve kablolama `grok-4.3` olur |
| 7 | Kablolanmamış model varsayılana düşer | örneği `a-model-nobody-wired` olur |

## Frontend'e dokunulmuyor, ve sebebi

`ModelPicker.test.jsx` ve `models.test.js` `grok-build-0.1`'i **emekli kimlik** örneği olarak
kullanıyor — *"eski bir mesaj onu adlandırabilir, ve seçicide artık satırı yok"*. Bu madde onu
gerçekten emekli ediyor, yani o testler **daha da doğru** hâle geliyor. `models.test.js`'in
`grok-4.3`'ü de seçiciye göre hâlâ bilinmiyor *(besteci yalnız iki DeepSeek satırı gösteriyor)*, o da
yerinde kalıyor.

`test_stream_answer.py` ve `test_file_chat_store.py`'deki kimlikler **eski kayıtların** içinde —
bir sohbet, bugün var olmayan bir modeli adlandırabilir, ve o testlerin söylediği tam olarak bu.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent` **5 kırmızı** verdi.

**Tahmin 6 demişti, ve şaşmasının sebebi kaydedilmeye değer.** 6. ile 7. sıradaki değişiklikler
`test_xai_engine.py`'nin **fikstürleri** — `DEFAULT` sabiti ve *"kablolanmamış model"* örneği. Bunlar
config'e bağlı değil, dosyanın kendi içinde uydurulmuş adlar: hangi string yazılırsa yazılsın test
aynı şeyi ölçüyor. Yani onlar **iddia değil, düzeltme.**

Aralarındaki fark önemli: `a-model-nobody-wired`'a geçiş bir tercih değil, **testi dürüst tutan**
şey. Örnek `grok-4.3` kalsaydı, uygulama turundan sonra *"bilinmeyen ad varsayılana düşer"* diyen
test **bilinen bir adla** koşacaktı ve yeşilliği hiçbir şey kanıtlamayacaktı. Kırmızı vermeyen bir
değişiklik de gerekli olabilir; gerekliliği kırmızıdan değil, testin ne ölçtüğünden gelir.

5 kırmızının hepsi `test_config.py`'de, ve hepsi tek satırın iki yerde okunmasından.

## Kırmızı turun tuzağı

v7'de altı kez çıktı: **hiçbir şey olmadığı için geçen test.** Buradaki hâli 4. testte — *"eski
kimlik tabloda yok"* diyen bir `not in`, tablo bomboş olsa da geçer. Bu yüzden 4. test önce **yeni
kimliğin tabloda olduğunu** ölçüyor, sonra eskisinin olmadığını.
