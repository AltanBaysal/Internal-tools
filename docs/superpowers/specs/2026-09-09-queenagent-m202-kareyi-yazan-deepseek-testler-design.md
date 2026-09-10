# Madde 202 · test turu — kareyi yazan da DeepSeek, ve son eki taşır

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 202.

---

## Bugün ne oluyor

`config.PROMPT_MODEL` **`grok-4.3`** *(Madde 183)*, ve kareyi yazan her istek oraya gidiyor —
`write_frame_prompt` tek tek, `write_missing_actions` topluca. O isteğin sistem metni
`WRITE_FRAME_SYSTEM_PROMPT`, ve **196'nın son ekini taşımıyor**: o madde açıkça *"yalnız besteci"*
demişti, çünkü kareyi yazan başka bir servisti.

## Ne kurulacak

- `PROMPT_MODEL = "deepseek-v4-flash"`. Tek sabit, yani iki araç birden taşınıyor.
- `prompt.write_frame_system_prompt()` — `system_prompt()`'un aynısı, kareyi yazanın metni için:
  sabit metin, ardından son ek. **İşlev, sabit değil**, ki bugün yazılan bir son ek bir sonraki
  isteğe yetişsin.
- İki araç da o işlevi çağırıyor.

### Ters çevrilen iki kayıt

- `PROMPT_MODEL`'in `grok-4.3` olduğunu pinleyen test **bu maddenin kararını** yazar.
- 196'nın *"kareyi yazanın metnine dokunulmuyor"* gerekçesi düşer: yazar artık aynı servis.

### `grok-4.3` satırı duruyor

183'ün *"kimse kullanmayacak satır ölü yapılandırma"* kuralına **bilerek** verilen istisna. Satırı
silmek `XAI_API_KEY`'i ve notebook'un üç sırrını peşinden sürüklerdi; geri dönüş ise tek sabit.
Testi yerinde kalıyor, **gerekçesi** değişiyor — bir yorum bugün doğru olanı söyler.

## Testler

### `test_config.py`

1. **yazar flash modeldir** — bugünkü `grok-4.3` pini ters çevriliyor.
2. **satır tabloda kalıyor** — yeşilden yeşile; adı ve gerekçesi bu maddeye göre yazılıyor.

### `test_prompt.py`

3. **kareyi yazanın metni son eki taşır** — sabitle başlar, son ekle biter.
4. **boş son ek metni bayt bayt bırakır** — 196'nın kuralı burada da geçerli.

### `test_tools.py`

5. **tek kare aracı o metinle sorar** — yazarın gördüğü sistem metni son ekle bitiyor.
6. **toplu araç da öyle sorar** — döngünün her isteği aynı metni taşıyor.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. Arka uçta **5 kırmızı**: sabit hâlâ Grok'u gösteriyor,
`write_frame_system_prompt` diye bir işlev yok, ve iki araç da sabiti doğrudan gönderiyor. 2 numara
baştan yeşil ve öyle olduğu yukarıda yazılı. Ön yüz ve `queen-editor` kımıldamıyor:
**648 · 739 · 591** yerinde.
