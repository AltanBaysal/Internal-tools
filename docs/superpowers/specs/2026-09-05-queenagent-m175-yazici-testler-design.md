# Madde 175 · test turu — prompt yazan model bir rol oluyor

**Kaynağı:** [yol haritası](../plans/2026-09-05-queenagent-v7-roadmap.md), Madde 175. Ekranda hiçbir
şey göstermiyor: 176'nın yolunu döşüyor.

Bu tur **yalnız testleri** yazıyor ve kırmızı commit'liyor.

---

## Ne açılıyor

Bugün motorun tek canlı yolu `stream`: konuşmayı, araçları, sistem promptunu ve kabı taşıyan uzun
istek. 176'nın ihtiyacı bunun tam tersi — **tek soru, tek cevap:** kendi sistem promptu, araç yok,
konuşma yok, tur damgası yok.

`Engine.write_once(system, user)` bu. Üç katmanda birden:

| Katman | Ne yapıyor |
|---|---|
| `Engine` *(port)* | `write_once(system, user) -> dict` ilan ediyor |
| `XaiEngine` | **prompt yazıcının** istemcisini seçiyor, `[system, user]` kuruyor |
| `XaiClient` | akışsız tek POST, `{"text", "spent"}` döndürüyor |

`SYSTEM_PROMPT` bu yola **girmiyor.** `_for_xai` onu her isteğin başına koyuyor; burada sistem
promptu çağıranın, çünkü yazan model QueenAgent'ın ajanı değil, tek işi olan bir yazıcı.

## Ölü yol sökülüyor

`Engine.complete` / `XaiEngine.complete` / `XaiClient.complete` — üçü de. Üretimde hiçbir yerden
çağrılmıyor: `stream_answer` yalnız `stream` kullanıyor. Yerine `write_once` geçiyor ve **port
imzasını ölçen test canlı yola taşınıyor** — bir Protocol'ün gövdesi yok, onu adaptörüne bağlayan
tek şey o test.

**`test_the_port_no_longer_hands_a_model_to_the_call` siliniyor.** İddiası `Engine.complete`'in
docstring'inde *"travels with the call"* geçmemesi; koruduğu kural ise Madde 82'nin *"model config'te,
çağrıda değil"* kuralıydı. **O kuralı Madde 146 zaten tersine çevirdi** — `stream`'in `model`
parametresi var, model çağrıyla birlikte gidiyor. Test bugün yalnızca cümle orada olmadığı için
yeşil; koruduğu şey ortada yok. Dayandığı fonksiyonla birlikte gidiyor.

Yerine gelen: **`complete` diye bir yol kalmadığını** ölçen tek test, üç katmanda birden.

## `config.PROMPT_MODEL`

`grok-build-0.1` — ama artık **besteciden seçilebilen bir model değil, config'te bir rol.**
Kullanıcının kararı: *"Grok bir seçenek değil, config.py'de bir rol."* 177 besteciyi iki satıra
indiriyor; Grok o listeden çıkıyor ve yalnız burada kalıyor.

`MODELS`'in bir anahtarı olmak zorunda — testi bunu ölçüyor, çünkü olmayan bir anahtar
`XaiEngine`'de `KeyError` olurdu ve hata çağrı anında, deneme sırasında çıkardı.

`main.py` üçüncü adı bağlıyor: `XaiEngine(clients, default, prompt_writer=config.PROMPT_MODEL)`.

## `run_tool` motoru alıyor

`run_tool(file_store, project_id, name, arguments, engine=None)` — varsayılan `None`, ve bugün
hiçbir araç ona bakmıyor. 176'nın aracı motorsuz çağrıldığında reddedecek; bugün ölçülen tek şey
**varlığın öteki araçları bozmadığı.**

`ToolResult` beşinci alanı kazanıyor: `spent`, varsayılan `None`. Bir aracın harcaması.

## Bilerek bu maddede olmayan: damgaya ekleme

Yol haritası *"aracın harcaması turun damgasına eklenir"* diyor ve bunu 175'e koyuyor. **176'ya
taşıyorum.** Sebep: bugün harcayan bir araç yok, dolayısıyla toplamanın görülebileceği hiçbir yol
yok — testi yazmanın tek yolu `stream_answer.run_tool`'u yamalamak olurdu, bu takımda hiç
kullanılmayan bir kalıp. 176 aracı getirince toplama da gerçek bir çağrıyla ölçülüyor.

Alan burada doğuyor *(varsayılanı ölçülüyor)*, toplama orada.

---

## Çivilenen vak'alar — 27 kırmızı

**Port (2):** `write_once` imzası porta ve adaptöre uyuyor; `complete` üç katmanda da yok.

**Motor (3):** `write_once` **prompt yazıcıya** gidiyor, turun modeline değil · kendi sistem
promptunu taşıyor ve `SYSTEM_PROMPT` içinde geçmiyor · metni ve harcamayı döndürüyor.

**İstemci (6):** anahtar yokken hiçbir şey gönderilmiyor · anahtar her istekte okunuyor · istek
modeli, mesajları ve bearer'ı taşıyor · akışsız istek `stream_options` sormuyor · HTTP hatası
servisin kendi sözlerini taşıyor · ölü bağlantı da.

**Config (1) ve bileşim (1):** `PROMPT_MODEL` `MODELS`'in anahtarı; `main.py` onu bağlıyor.

**Araçlar (2):** `run_tool` motoru alıyor ve öteki araçlar etkilenmiyor · `ToolResult.spent`
varsayılanı `None`.

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **27 kırmızı.** Sayı yazılan vak'adan yüksek, çünkü `XaiEngine`'in yapıcısı üçüncü adı alınca
   `test_xai_engine.py`'nin **hepsi** düşüyor — dokuz test tek bir imza değişikliğinden. Aynısı
   istemcinin altı testinde. Bunlar yeni iddia değil, bir imzanın peşinden gelen düşüşler.
3. Kırmızıların hepsi **yokluktan** — `write_once`, `prompt_writer`, `PROMPT_MODEL`. Hiçbiri `skip`
   ya da `xfail` değil.
4. Öteki üç takım rakamlarını korudu: **586 · 739 · 591.** `dist` derlenmedi.
