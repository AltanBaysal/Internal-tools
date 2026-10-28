# Madde 493 · QueenAgent yönü ve klip süresini başta sorar — plan

**Hedef:** iki start skill'i önce yönü ve bir klibin süresini sorar, cevaplar `<senaryo>-notes.md`'ye
yazılır, iki edit onu okur ve yoksa sorar; hiçbir metin süreyi ya da boyutu sabitlemez; prompt'lar
fotoğrafı seçilen yöne göre kadrajlar.

**Spec:** [m493](../specs/2026-10-22-queen-agent-m493-orientation-length-design.md) — metinlerin tam hâli
onun eklerinde; bu plan onları kopyalamaz, yerini söyler.

Önce testler yazılır ve kırmızı görülür, sonra metinler. Yollar `queen-agent/backend/` altında. Kod,
araç, ön yüz değişmez; `dist` kurulmaz. Takımlar teker teker koşar.

## Görev 1: Testler

1. **`tests/test_skills.py`:**
   - `STEPS` 11 başlık (yeni Step 1 *ask the orientation and the video length*, Step 7 *fit each scene
     into the video length*); `test_the_flow_runs_eleven_numbered_steps`.
   - Adım numaralı testler birer kayar: plan `_step(2)` (`- [ ] 2.` / `- [x] 2.`), karakterler
     `_step(3)`, mekânlar `_step(4)`, sahneler `_step(5)`, kareler `_step(6)` (sıra testi Rule 7'ye
     kadar), `CHECKS = [7, 8, 9, 10]`, görüntü denetimleri `[8, 9, 10]`, onaysız adımlar `[6 … 10]`,
     negatif liste `_step(11)`; süre denetimi *"video of exactly the video length"*, *"two scenes of the
     video length each"*, *"rules of Step 6"*.
   - Yeni: SDXL Step 1 soruyor ve notes'tan okuyabiliyor; Step 3 notes'u açıyor
     (`beach-notes.md for beach.sdxl.json`); Step 6'da Rule 7.
   - `KREA_STEPS` 6 başlık; Krea testleri birer kayar; yeni: Step 2 notes'u açıyor
     (`beach-notes.md for beach.krea.json`), Step 4 görünüşleri *the notes file*'a yazıyor, Step 5
     kadrajı söylüyor.
   - Yeni bölüm *the orientation and the video length (Madde 493)*: iki start'ın Step 1'i; iki start
     *"The user chooses both in Step 1."*; iki edit notes'u okuyor ve eksikse sorup yazıyor; dört
     skill'de *"video length"* var, *"four seconds"* ve *"1536"* yok.
   - Tavan testi: dört yeni tavan ve yazılı karar (spec, *Testler*).
2. **`tests/test_prompt.py`:** sahne bölümü *"short enough for the video length"*, belgede *"four
   seconds"* yok; iki belge kadraj satırını taşıyor; her belge kendi boyutunu iki yön için veriyor
   (SDXL `1536 x 864` / `1024 x 1536`, Krea `1280 x 720` / `832 x 1248`).
3. **`tests/test_tools.py`:** `test_the_document_gives_the_photos_size_and_no_models_name` *"1536 x
   864"* ve *"1024 x 1536"* arıyor.
4. `python -m pytest queen-agent -q` — yeni ve kayan testler kırmızı.

## Görev 2: Metinler — `features/workspace/domain/prompt.py`

1. `EDIT_PROMPTS` — spec Ek B.
2. `START_A_SCENARIO` — spec Ek A: Context, yeni Step 1, plan Step 2, notes satırı Step 3'te, sahne
   satırı, Rule 7, Step 7'nin süre cümleleri, bütün adım ve review numaraları.
3. `KREA_START_SCENARIO` — spec Ek C; `KREA_EDIT` — spec Ek D.
4. `SDXL_GUIDE`, `KREA_GUIDE` — spec Ek E.
5. Yorumlar: skill bloğu (*Steps 7 – 11*), Krea skill'leri (adım numaraları, 493'ün notu), belgeler
   (iki boyut, kaynakları; *"No size: that is v11-6's"* kalkar).
6. Tavan testi kırmızıysa sayıları okuyup tavanları metinlerin geldiği yer + birkaç kelime yap, yazılı
   kararla.
7. `python -m pytest queen-agent -q` yeşil.

## Görev 3: Belgeler

1. Yol haritası: v11-6 → `493 · v11-6`, `ALIGNED`, kullanıcının 22 Ekim sözleri, *Bitti sayılır*;
   başlıktaki *Durum*.
2. Spec ve bu plan.

## Görev 4: Dört takım, tek tek

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```
