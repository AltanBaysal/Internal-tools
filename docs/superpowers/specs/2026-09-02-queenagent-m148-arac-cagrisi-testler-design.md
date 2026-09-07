# Madde 148 · Tur 1 (test) — Tasarım

**Kaynak:** [v6 yol haritası](../plans/2026-09-01-v6-roadmap.md), Madde 148
**Dal:** `feat/v6` · **Bu tur yalnız test yazar.**

## Kusur

`start-a-scenario` seçili bir turda **`Couldn't get a response. 'name'`**. Grok Build'de yok,
DeepSeek'in **iki** modelinde de var — Flash ile Pro aynı API'yi paylaştığı için bu bir sağlayıcı
farkı.

`'name'` bir `KeyError`'ın metni.
[client.py:91](../../../queen-agent/backend/services/xai/client.py#L91) her `tool_calls` deltasını
**tam bir çağrı** sayıp olduğu gibi yukarı veriyor. xAI için doğru; DeepSeek OpenAI gibi parçalıyor:

```
delta.tool_calls = [{"index": 0, "id": "call_1", "type": "function",
                     "function": {"name": "write_plan", "arguments": ""}}]
delta.tool_calls = [{"index": 0, "function": {"arguments": "{\"na"}}]
delta.tool_calls = [{"index": 0, "function": {"arguments": "me\": \"x\"}"}}]
```

İkinci ve üçüncü parçada `name` yok. `stream_answer` bunları `extend` ile ayrı çağrı gibi biriktirip
`call["function"]["name"]` diyor ve düşüyor.

**Kusur skill'e bağlı değil, araç çağrısına bağlı.** `start-a-scenario` ilk turda `write_plan`
çağırdığı için ilk oradan görüldü.

## Düzeltme nerede durur

**İstemcide.** Yukarısı zaten tam çağrı bekliyor ve bekleyeceği yer doğru: parçalanma taşımanın bir
ayrıntısı, ve taşıma bu dosya. Bugünkü yorum sözleşmeyi zaten yazıyor — eksik olan, onu bir
varsayım olarak değil bir garanti olarak sağlamak.

Birleştirme **`index` üzerinden**, sıra üzerinden değil: alan bunun için var, ve tek turda iki araç
çağrılırsa parçaları birbirine karışır.

**Tam çağrı akışın sonunda veriliyor**, parça geldikçe değil — bir çağrı ancak bittiğinde tamdır.
Bu yukarısını etkilemiyor: `stream_answer` çağrıları döngü bittikten sonra işliyor.

## Kırmızıya dönecek iddialar

1. **Parçalı bir çağrı tek ve tam olarak çıkıyor.** Üç parça giriyor, bir `tool_calls` çıkıyor, ve
   `function.name` ile `function.arguments` yerinde.
2. **Argümanlar sırayla birleşiyor.** Parçalar geldiği sırada ekleniyor; sonuç geçerli JSON.
3. **Tek parça gelen bir çağrı bozulmuyor.** xAI'nin yolu — bugün çalışan şey çalışmaya devam
   ediyor, çünkü tek parça da bir parçadır.
4. **İki araç aynı turda çağrılırsa parçaları karışmıyor.** `index` 0 ve 1 ayrı ayrı birleşiyor ve
   ikisi de çıkıyor.
5. **Metin ile araç çağrısı aynı akışta bir arada duruyor.** Model önce konuşup sonra çağırabiliyor;
   metin geldiği anda çıkmaya devam ediyor, çağrı sonda.
6. **Hiç araç çağrılmayan bir akış hiç `tool_calls` vermiyor.** Boş bir birleştirici, boş bir liste
   yayınlamamalı — `stream_answer` onu `else` dalında araç sanır.

## Yeşil kalması gerekenler

- **Bütün mevcut `test_xai_client.py`** — özellikle jeton sayıları, kesme, ve tek parça çağrı.
- **Bütün `test_stream_answer.py`** — bu madde o dosyaya dokunmuyor; dokunmak zorunda kalırsam
  düzeltme yanlış katmandadır.
- Madde 146'nın hepsi.

## Kapsam dışı

- **`stream_answer` ve yukarısı.** Tek satır değişmiyor.
- **`finish_reason`'a bakmak.** Birleştirilen çağrı akışın sonunda veriliyor; hangi sebeple bittiği
  ayrı bir bilgi ve bu kusurun parçası değil.
- **Parçalı çağrının ekranda ilerlerken gösterilmesi.** Kart zaten çağrı çalıştıktan sonra doluyor.
