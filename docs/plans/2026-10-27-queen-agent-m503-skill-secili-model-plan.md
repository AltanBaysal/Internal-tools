# Madde 503 — Skill seçili modeli söyler, plan

**Hedef:** Dört skill'in ilk satırı, kullanıcının hangi modeli seçtiğini söyleyen bir cümle; SDXL start
scenario'yla başlayan sohbette ajan model sormuyor.

**Spec:** [m503](../specs/2026-10-27-queen-agent-m503-skill-secili-model-design.md)

## Kısıtlar

- Her skill'e tek cümle, ilk satır olarak; skill metinlerinin geri kalanı değişmez.
- SDXL metninde "krea", Krea metninde "sdxl" geçmez; araç adı geçmez.
- Kelime sınırları yalnız 27 Ekim kararıyla ve yalnız cümle kadar (birkaç kelime payla) yükselir.
- Önce test kırmızı, sonra metin.

### Görev 1: Testler kırmızı

**Dosya:** `queen-agent/backend/tests/test_skills.py`

- [ ] `FIRST_LINE` → `MODEL_CHOSEN` (iki cümle, modele göre) ve `GUIDE_LINE` (bugünkü rehber satırları);
  `OPENING[skill] = MODEL_CHOSEN[skill] + "\n" + GUIDE_LINE[skill] + "\n\n"`.
- [ ] Yeni `test_every_skill_opens_by_saying_which_model_the_user_chose`: metin
  `MODEL_CHOSEN[skill] + "\n"` ile başlar.
- [ ] `test_every_skill_opens_by_sending_the_model_to_its_guide` açılışa (`OPENING`) bakar.
- [ ] `_after_the_first_line` → `_after_the_opening`, `OPENING`'in arkasını verir; iki persona testi onu
  kullanır.
- [ ] Kelime sınırları: 2040, 295, 560, 345; yorumuna madde 503'ün kararı eklenir.
- [ ] `test_every_skill_says_what_the_prompts_are_for`: "SDXL" yokluğu açılışın arkasına bakar
  (ana ajanın 27 Ekim kararı).
- [ ] `python -m pytest queen-agent/backend/tests/test_skills.py -q` — açılış testleri kırmızı.

### Görev 2: Cümleler

**Dosyalar:** `queen-agent/backend/features/workspace/skills/sdxl-start-scenario.md`, `sdxl-edit.md`,
`krea-start-scenario.md`, `krea-edit.md`

- [ ] SDXL'in ikisinin ilk satırı: `The user has already chosen the image model, SDXL: the scenario is an
  SDXL scenario, a .sdxl.json file, so never ask which model.`
- [ ] Krea'nın ikisinin ilk satırı: `The user has already chosen the image model, Krea: the scenario is a
  Krea scenario, a .krea.json file, so never ask which model.`
- [ ] Rehber satırı (`Read …-prompt-writing.md first.`) hemen arkasında, aynı paragrafta kalır.

### Görev 3: Yorum

**Dosya:** `queen-agent/backend/features/workspace/domain/prompt.py`

- [ ] Skill'lerin açılışını anlatan yorum: her skill önce kullanıcının seçtiği modeli söyler (madde
  503), sonra rehberine gönderir.

### Görev 4: Takım ve yol haritası

- [ ] `python -m pytest queen-agent -q` — yeşil.
- [ ] Yol haritasında 503 ✅, başlık "2/5 bitti". Commit'i ana ajan atar.
