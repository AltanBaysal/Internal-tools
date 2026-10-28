# Madde 499 · Translucent Penetration Krea'da, ve Qwen Image 2.1 Turbo — plan

**Spec:** [2026-10-27-queen-editor-m499-krea-slime-qwen-design.md](../specs/2026-10-27-queen-editor-m499-krea-slime-qwen-design.md)

Önce test yazılır ve kırmızı görülür, sonra kod. Takımlar tek tek koşar.

## Katalog ve kurallar

1. **`backend/tests/test_photo_usecases.py` — kırmızı.**
   - Model listesi Nova, DaSiWa, Krea, Qwen; Qwen'in checkpoint'i yok.
   - `list_models(["krea2"])` Krea'nın üç satırını (SNOFS, SNOFS + Slime, Boş) ve `negative: False`'u;
     `list_models(["qwen21turbo"])` Translucent Penetration ve Boş'u veriyor.
   - Krea batch'i `snofs_slime` ve `none`'ı kaydediyor; boş seçim SNOFS; Krea'da Nova'nın `slime`'ı,
     Qwen'de Krea'nın `snofs`'u, Nova'da `snofs_slime` ve bilinmeyen bir değer `InvalidLora`'yla
     duruyor (486'nın istisnası kalktı).
   - Qwen batch'i `translucent_penetration` / `none` kaydediyor, negatifi boş.
   - Yeniden üretilen bir Krea `snofs_slime` karesi `snofs_slime` kalıyor.
2. **`domain/catalog.py` — yeşil.** `QWEN`, `SLIME_TRIGGER`, `SNOFS_KREA`, `SLIME_KREA`, `SLIME_QWEN`,
   `KREA2_LORAS`, `QWEN_LORAS`; `MODELS`'ta Krea'nın `loras`'ı ve Qwen'in satırı; `own_loras`,
   `find_own_lora`, `drawn_with`, `own_pick`, `with_trigger` (üç üretici de çağırır). `find_lora`
   yalnız ortak kutu. `KREA2_LORA` ve `own_lora` gider.
3. **`domain/usecases/list_models.py`** — satırda `loras` (+ Boş). **`start_batch.py`** — kendi
   kutusu olan model kendi listesine karşı doğrulanır.
   Yorumlar (`regenerate.py`, `fix_photo.py`) kendi listesine göre.

## Üreticiler

4. **`backend/tests/test_lora_chain.py` — kırmızı.** Dosyasız zincir verileni döndürüyor; iki dosya
   `lora:1` → `lora:2`, her biri öncekinin modelini alıyor, güçleriyle.
5. **`data/lora_chain.py` — yeşil.** `chain_loras`.
6. **`backend/tests/test_comfy_krea_photo_generator.py` — kırmızı.** SNOFS'ta grafik değişmeden
   gidiyor (Nova'nın `slime`'ında da); SNOFS + Slime'da `lora:1` (Slime Krea 1,0, modeli `53:15`),
   `53:22.on_true` → `lora:1`, prompt'un önünde tetik; Boş'ta `53:23` kapalı, prompt olduğu gibi;
   eksik düğümler `53:15`, `53:22`, `53:23` de adlanıyor.
7. **`data/comfy_krea_photo_generator.py` — yeşil.**
8. **`backend/tests/test_comfy_qwen_photo_generator.py` — kırmızı.** Prompt `452`'de, seed `488`'de,
   boyut `456`'da (1536 × 864, 1024 × 1536; yönsüz 1024 × 1024); Translucent Penetration'da `490`'ın modeli
   `lora:1`, `lora:1`'in modeli `451`, tetik önde; Boş'ta `490` → `451`, tetik yok; negatif gitmiyor;
   UI biçimi ve eksik düğüm hatası; dosyaya yazılmıyor.
9. **`assets/workflow_photo_qwen_api.json`** (spec 5) ve **`data/comfy_qwen_photo_generator.py`
   — yeşil.** `config.QWEN_WORKFLOW_PATH`.
10. **`backend/tests/test_workflow_asset.py` — kırmızı → yeşil.** Beş grafik; Qwen grafiği API biçiminde,
    8 adımlık sigmas, cfg 1, euler, negatif boş, çıkışı `SaveImage`; prompt geliştirici yok; Qwen'in
    boyutları videonun oranında ve 32'nin katı; Krea'nın `53:15`'i katalogdaki SNOFS (dosya ve 0,8);
    her grafiğin dosyaları + seçeneklerinin dosyaları = gruptaki satır; Qwen ve Krea grafiğinde her
    bağlantı var olan bir düğümü adlıyor ve her düğüm bir çıkışa ulaşıyor (üreticinin gönderdiği
    grafikte de bağlantılar).
11. **`test_composition_root.py`, `test_producer_contract.py`, `test_photo_by_model.py` — kırmızı →
    yeşil.** `main.py`: `PhotoByModel`'in haritasına `catalog.QWEN`; bir Qwen karesi Qwen grafiğine
    gidiyor; gerçek döngüde Qwen'in iki varyantı iki iş.

## Üreticiler paneli ve notebook

12. **`backend/tests/test_producers.py` — kırmızı.** Gruptaki ilk satırın üç seçeneği; yalnız Qwen'li
    makinede fotoğraf kurulu.
13. **`features/producers/domain/model_groups.py` — yeşil.** `KREA2_FILES` + Slime Krea, `QWEN_FILES`.
14. **`backend/tests/test_notebook_installs_the_producer_groups.py` — kırmızı.** `HF_QWEN`'in üç
    satırı; `CIVITAI_QWEN` (3370853) ve `CIVITAI_KREA2`'deki Slime (3117012) aynadan; ikisi kutusunun
    arkasında; `+ (17 if PHOTO_QWEN21TURBO else 0)`; klasörler Qwen için de; klon beşinci grafiği arıyor.
15. **`queeneditor.ipynb` — yeşil** (spec 10).

## Ekran

16. **`GeneratePanel.test.jsx` — kırmızı.** Krea'nın kutusu üç satır, seçilebilir, SNOFS'la açılıyor,
    seçileni gönderiyor; Qwen'in kutusu iki satır, negatif yok; Nova ↔ Krea arasında iki seçim yerinde;
    `{krea2, slime}` kaydı Nova'yı Slime, Krea'yı SNOFS açıyor; `{krea2, snofs_slime}` Krea'yı SNOFS +
    Slime açıyor; taslak iki seçimi de saklıyor.
17. **`GeneratePanel.jsx` — yeşil.** `picks`, `saved`; kutunun listesi ve değeri satırdan.
18. **`PhotoDetail.test.jsx` — kırmızı → `PhotoDetail.jsx` yeşil.** Krea'nın SNOFS + Slime'ı ve Qwen'in
    Translucent Penetration'ı adıyla.
19. `npm run build --prefix queen-editor/frontend`.

## Son

20. `python -m pytest queen-editor -q`, sonra `npm test --prefix queen-editor/frontend`.
