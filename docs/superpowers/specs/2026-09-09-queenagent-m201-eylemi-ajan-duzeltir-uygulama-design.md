# Madde 201 · uygulama turu — eylem satırını ana ajan düzeltir

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 201, ve
[test turu](2026-09-09-queenagent-m201-eylemi-ajan-duzeltir-testler-design.md) — 5 kırmızı.

---

## Ne yazılacak

### `tools.py`

- `update_frame`'in şemasına `action`, açıklaması `prompt.UPDATE_FRAME_ACTION`.
- `_update_frame`'in okuduğu alanlar demetine `action` girer, ve verilen değer `strip`'lenir —
  sahnenin yaptığı gibi. Gerisini bugünkü döngü hallediyor: **dolu yazar, boş kaldırır.**
- İşlevin docstring'i tersine dönüyor. Bugün *"never the action"* diyor ve gerekçesini
  *"ana model o cümleyi iyi yazmaz"* diye veriyor; o gerekçe kalktığı için cümle de kalkıyor.
  Yerine ayrımın kendisi yazılıyor.

### `prompt.py`

- `UPDATE_FRAME`: okuyucuyu başka araca gönderen son cümle gidiyor, yerine action'ın da bu alanların
  arasında olduğu.
- **Yeni** `UPDATE_FRAME_ACTION`: alanın kendi metni — satırın yerine geçtiği, boşun satırı
  kaldırdığı, ve kuralların *(`SDXL_PROMPT_RULES`)* burada da geçerli olduğu.
- `EDIT_PROMPTS`: yanlış okunan satır **kendi turunda** düzeltiliyor. Yazara gitmek duruyor ama
  ikinci sıraya düşüyor — **sahneden yeniden yazılsın** istendiğinde.

## Kelime tavanı

`EDIT_PROMPTS`'un tavanı **200 kelime** ve bugün ona yakın. Yeni cümle, yerini aldığı cümlenin
yerine geçiyor — tavan yükselmiyor, çünkü bu koşunun bağlayıcı kuralı bu.

## Ne değişmiyor

`write_frame_prompt` ve notu duruyor: **satırın ne olması gerektiğini biliyorsan** kendin
yazıyorsun, **sahneden yeniden yazılmasını** istiyorsan yazara gidiyorsun. `write_missing_actions`
hiç değişmiyor — boş kare zaten ajanın işi değil.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, sırayla, birebir: **944 · 648 · 739 · 591**. Ön yüz derlenmiyor.
