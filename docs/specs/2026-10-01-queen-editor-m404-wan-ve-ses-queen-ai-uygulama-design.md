# Madde 404 — WAN'ın ve sesin prompt'unu Queen AI yazar, uygulama turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 5 · **Parça:** 404 · v8-3d · **Tur:** 2/2 — kırmızı testleri yeşile
çeviren kod. **Testler:** [m404 test turu](2026-10-01-queen-editor-m404-wan-ve-ses-queen-ai-testler-design.md).

**Kullanıcıdan gereken — yok.** Kararlar test spec'inde; buradakiler kodun nasıl yazılacağı.

## Parçalar

### 1. Yazarlar — `data/xai_prompt_writer.py`

- `VIDEO_INSTRUCTION` `tmp/queen-editor-prompts.md`'nin "WAN (404)" bölümü, `AUDIO_INSTRUCTION` "Ses —
  MMAudio (404)" bölümü — kelimesi kelimesine, adları aynı, dosyanın alışkanlığıyla üç tırnağın içinde
  baştan ve sondan birer satır sonu. Üstlerindeki yorumlar şimdi doğru olanı söyler; collab-toolbox'tan
  miras cümlesi düşer — yeni metin oradan gelmiyor.
- Senaryonun söylenişi iki video yazarında aynı: `_scenario(scene)` → `f"Scenario: {scene}"` ya da
  boş. H3 yazarı da onu kullanır; davranışı değişmez.
- `VideoPromptWriter.write(…)`: `client.complete(asked(VIDEO_INSTRUCTION, mode), _scenario(scene),
  [source])`. Sözler gitmez; `end` yok sayılır — bağlı metin H3'ün, ve loop'un vardığı resim zaten
  gösterilen fotoğraf.
- `AudioPromptWriter.write(…)`: `client.complete(AUDIO_INSTRUCTION, f"Video prompt: {video}")`. Resim
  yok, fotoğrafın sözleri yok. Videonun prompt'u yoksa ayrı koruma yok: döngü o zaman sormaz (parça 2).
- Modülün docstring'i: üç yazar da Queen AI'la konuşur; dosya yalnız ne söyleneceğine karar verir.
  Dosyanın adı kalır — 406 grok'u silerken dosya yeniden şekillenir.

### 2. Döngü — `domain/run_loop.py`, yalnız `_unwritten`

Döngüye dokunmadan olmuyor: yazarın sorulup sorulmayacağına `_unwritten` karar veriyor, ve bugün
karenin herhangi bir sözüne bakıyor. Yazar kendisi kaçamaz — hata bir deneme sayılır, boş cevap da
karta boş bir "yazıldı" satırı olurdu. Değişen tek koşul:

```python
def _has_words(kind, said):
    """Whether the frame says anything this job's prompt can be written from. A sound is written from
    its video's prompt alone (madde 404); a video from whatever the frame says."""
    return bool(said.get(layers.VIDEO)) if kind == layers.AUDIO else any(said.values())
```

`_unwritten` `any(said.get(job["id"], {}).values())` yerine `_has_words(queue.type_of(job),
said.get(job["id"], {}))` sorar; docstring'i sesi anar. Başka satır değişmez — 405 aynı dosyada
üretimin süresine dokunuyor, ve bu değişiklik onun yerinden uzak.

### 3. Kompozisyon kökü — `backend/main.py`

Tek `_queen_ai = DeepSeekClient(...)`; H3 dalı `H3VideoPromptWriter(_queen_ai)`, WAN dalı
`VideoPromptWriter(_queen_ai)`, `_writers` sesi `AudioPromptWriter(_queen_ai)` ile. `_xai` ve
`XaiClient` içe aktarması kalkar: kurulmuş ama kullanılmayan istemci yanlış bir şey söylerdi. xAI
istemcisinin dosyası, `config`'teki xAI satırları ve defter yerinde kalır *(406)*; `config`'in xAI ve
DeepSeek yorumları şimdi doğru olanı söyler — xAI'a artık hiçbir şey sorulmuyor, DeepSeek her video ve
ses prompt'unu yazıyor.

### 4. README — Secrets satırları

- `DEEPSEEK_API_KEY`: her video prompt'u — H3'ün ve WAN'ın, karenin fotoğrafını görerek — ve her sesin
  prompt'u, videonun prompt'undan, katman kuyruğa girer girmez DeepSeek'e yazdırılır. Anahtarsız
  fotoğraflar üretilir; bir video ya da ses kuyruğa girince koşu istemcinin kendi cümlesiyle durur.
- `XAI_API_KEY`: uygulama artık hiçbir şeyi xAI'a sormuyor. Defter onu hâlâ okuyor ve CONFIG'de
  yokluyor: boşsa yalnız bir satır yazar; ölü bir anahtar video kuran bir koşuyu durdurur.

## Bilinçli olarak yapılmayan

- Dosya adı, xAI istemcisi, `config.XAI_*`, defterin xAI satırları ve yoklaması — 406'nın.
- Video işinin "çevrilecek söz" kuralı değişmez (karenin herhangi bir sözü).
- Ekran değişmez; dist yok.

## Bitti sayılır

Dört satır yeşil; `xai_prompt_writer.py`'deki iki metin `tmp/queen-editor-prompts.md`'dekilerle
karakteri karakterine aynı.
