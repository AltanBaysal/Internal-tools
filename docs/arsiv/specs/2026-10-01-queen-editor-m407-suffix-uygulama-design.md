# Madde 407 — Prompt'u yazan modelin system prompt'una suffix, uygulama turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 6 · **Parça:** 407 · v8-6 · **Tur:** 2/2 — kırmızı testleri yeşile
çeviren kod. **Testler:** [m407 test turu](2026-10-01-queen-editor-m407-suffix-testler-design.md).

**Kullanıcıdan gereken — yok.** Metnin nasıl paylaşılacağı test spec'inde kararlaştırıldı: Queen
Editor kendi kopyasını tutar, ve bir test onu QueenAgent'ınkine bağlar.

## Parçalar — yalnız `backend/features/photo_generation/data/prompt_writer.py`

### 1. Suffix'in kopyası

`SYSTEM_PROMPT_SUFFIX`, QueenAgent'ın
[prompt.py](../../../queen-agent/backend/features/workspace/domain/prompt.py)'sindekinin harfi harfine
aynısı — üç tırnaklı, baştaki ve sondaki satır sonu dahil. `AUDIO_INSTRUCTION`'ın arkasında, `asked`'ın
önünde durur: dosyanın metinleri bir arada kalır.

Üstündeki yorum kodun söyleyemediğini söyler: metin sahibinin ve QueenAgent'ın; burada bir kopya,
çünkü iki araç çalışırken birbirine bağlanmaz; kopyayı QueenAgent'ınkine `test_video_prompt_writer.py`
bağlar, ve sahibi QueenAgent'ınkini değiştirdiği gün o test kırmızıya döner. Her modda en sona gelir.

### 2. Üç yazar onu en sona ekler

Suffix, her yazarın `complete`'e verdiği system mesajının sonuna, mesaj tamamlandıktan sonra
eklenir:

- **WAN** — `asked(VIDEO_INSTRUCTION, mode) + SYSTEM_PROMPT_SUFFIX`.
- **H3** — mod kuralları (`LOOP_RULE`, sonrakine bağlıda `LINKED_RULE`) eklendikten sonra:
  `instruction + SYSTEM_PROMPT_SUFFIX`.
- **Ses** — `AUDIO_INSTRUCTION + SYSTEM_PROMPT_SUFFIX`.

**`asked()`'a konmaz:** H3 `LINKED_RULE`'u `asked()`'tan sonra ekliyor, yani suffix orada olsa
sonrakine bağlı karede kuraldan önce kalırdı; sesin yazarı da `asked()`'ı kullanmıyor. Üç çağrının
her birinde açıkça yazılması, suffix'in en son geldiğini koda bakınca gösterir.

**Ayraç yok:** dosyanın metinleri başında ve sonunda birer satır sonuyla yazılı, ve mod kuralları
`+` ile, araya bir şey koymadan ekleniyor. Suffix de öyle başlıyor; yan yana gelince arada bir boş
satır kalır, tıpkı `LOOP_RULE`'da olduğu gibi.

## Bilinçli olarak yapılmayan

- QueenAgent'ın `prompt.py`'sine dokunulmaz.
- DeepSeek istemcisi değişmez: prompt'tan habersiz kalır (test spec'inin kural 4'ü).
- Yazarların metinleri ve mod kuralları değişmez.
- Boş suffix için ayrı bir dal yok: boş metni eklemek mesajı değiştirmez.
- Ekran değişmez; dist yok. Yol haritasına dokunulmaz.

## Bitti sayılır

Dört satır yeşil: Queen AI'ın H3, WAN ve ses prompt'larını yazarken aldığı system prompt her modda
QueenAgent'taki suffix'le bitiyor, ve Queen Editor'ün suffix'i QueenAgent'ınkiyle birebir aynı.
