# Madde 370 (v9-8b) — Improve skill'i açılır, ilk kontrolüyle: tek an mı — uygulama

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 370 · v9-8b.
**Testler:** [testler spec'i](2026-09-29-queenagent-m370-improve-tek-an-testler-design.md), kırmızı commit
`e19f6d93`. Bu spec yalnız o testlerin istediğini yazar.

**Kullanıcıdan gereken:** yok.

## Parçalar

1. **`prompt.py` — `THE_CHECKS`**, skill bloğunda `THE_IMAGE_MODEL`'in altında: kontrollerin tek yeri.
   Başlığı yok — her skill kendi adım başlığını önüne koyar, çünkü adım numarası iki metinde farklı
   (akışta 6, Improve'da 2). İçinde sırayla: bir kontrolün nasıl koştuğu (dört satır), `Check 1 -- one
   moment`, ve kapanış cümlesi. 371–373 kendi kontrollerini kapanıştan önce ekler.
2. **`prompt.py` — `START_A_SCENARIO`**: `five steps` → `six steps`; 5. adımın kapanış satırı gider,
   yerine 1. adımın sözüyle *"This step waits for no approval. Go on to Step 6 in the same turn."*;
   sonuna `Step 6 -- the checks` ve `THE_CHECKS`.
3. **`prompt.py` — `IMPROVE`**: persona, `THE_IMAGE_MODEL`, `Step 1 -- the scenario` (senaryo dosyasını
   bulur, planı okur ya da yazar, onay beklemez), `Step 2 -- the checks` ve `THE_CHECKS`.
4. **`skills.py`**: `INSTRUCTIONS`'a `"improve": prompt.IMPROVE`; docstring üç metni söyler.
5. **`skills.js`**: `SKILLS`'in sonuna `{ id: "improve", name: "Improve", detail: "Run four checks on a
   scenario's frames and prompts, and say yes after each one." }` — tasarımın `shell.js`'indeki satır
   birebir. Baştaki yorum üç satırı söyler.
6. **Yorumlar:** `prompt.py`'nin skill bloğu ve `test_the_menu_and_the_instructions_carry_the_same_names`
   bugünü söyler — üç metin.

## Metin

```
THE_CHECKS
- Run the checks below in order, each over every frame of the scenario.
- When a check starts, write in the plan which check it is: a long scenario can take more than one
  turn, and when the user says continue, carry on from there.
- A check changes only the frames that fail it. Then call build_prompts, so every changed frame's
  photo prompt is written again.
- Show what the check changed, frame by frame, and wait for their yes. A check ends when they
  approve it. If no frame fails, say so and go on to the next check.

Check 1 -- one moment
- A frame whose scene or action tells more than one moment fails. Bring it down to one moment, or
  split it into one frame per moment.
- To bring it down, give update_frame the new scene and an empty action.
- To split, bring the frame down to its first moment, then write the others with add_scene, before
  the next frame.
- Then write_missing_actions writes the emptied and the new frames, so each gets its own action.

When the checks are done, close by naming the file and saying it is ready. Do not print the prompts
back, offer nothing, and ask nothing: this is the last word.
```

## Kararlar

1. **Değişen karenin fotoğraf prompt'u bugünkü araçlarla yenilenir, yeni kod yok.** Sahnesi değişen
   karenin aksiyonu boşaltılır (`update_frame`'in boş aksiyonu *"a frame nobody has written yet"*),
   bölünen parçalar `add_scene` ile boş doğar; ikisini de `write_missing_actions` yazar, ve
   `build_prompts` listeyi yeniden kurar. Aksiyonu modelin kendisinin yeniden yazması da olurdu; ama
   aksiyonu yazan model ayrı tutuluyor *(Madde 176)*, ve boş bırakmak onu yine ona verir.
2. **Plan:** kontrol başlarken hangi kontrol olduğu plana yazılır — son turda araç koşmadığı *(Madde
   137)* için nerede kalındığı tur biterken yazılamaz, başlarken yazılır. Aynı sohbette "continue"
   sohbetin kendisinden sürer; taze bir sohbet plandan kontrolü bulur, ve düzeltilmiş kareler
   kontrolden zaten geçer. Hangi aracın yazacağı söylenmez: SYSTEM_PROMPT planı `create_file`'a,
   değişikliği `edit_file`'a veriyor.
3. **Hiç kare kalmazsa** kontrol bunu söyler ve sonrakine geçer: onaylanacak bir değişiklik yok.
4. **Improve plan yoksa yazar**, çünkü kontroller plana yazıyor; biçimini söylemez — SYSTEM_PROMPT'un
   "a job of several steps starts with a plan file" kuralı yeter.
5. **Edit prompts'a dokunulmaz** *(374'ün işi)*.
6. **Tavan:** Improve 700 *(test yorumunda)*. Akış ~700 kelimeye çıkar, 1000'in altında.
