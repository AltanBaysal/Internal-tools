# Madde 374 (v9-8f) — Edit prompts kontrollerle biter — testler

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 374 · v9-8f. *Kararları:
v9-8.* 29 Eylül paragrafları 28 Eylül metnini geçersiz kılar: H3 ve video prompt'u QueenAgent'ın değil,
Edit prompts yalnız fotoğraf prompt'unu yeniler. Kullanıcının sözü: *"edit prompt bitince de improvu
çağır desin"*. 28 Eylül kararı: *"Edit prompts'tan sonraki kontroller yalnız değiştirdiği karelere bakar,
ve kadro değiştiyse negatif liste de yeniden yazılır"*. Satır: Edit prompts bir kareyi değiştirince iş
yalnız o karelerin kontrolüyle bitiyor, ve kadro değiştiyse negatif liste yeniden yazılıyor.

**Kullanıcıdan gereken:** yok. Karar, dosya ya da ölçüm beklenmiyor. Aşağıdaki kararlar subagent'ın.

## Ne değişiyor

1. **Edit prompts `THE_CHECKS` ile biter**, Start a scenario ve Improve gibi: metnin sonu kontroller,
   bir kez. Kontroller ikinci kez yazılmaz; aynı sabit.
2. **Kontroller yalnız değişikliğin ulaştığı karelere bakar.** Edit prompts'un yeni `Step 4 -- the
   checks` adımı, kontrollerden önce bunu söyler. Edit prompts 3. adımında zaten *"which frames it
   reached"* diyor; kapsam aynı sözle anılır: değişikliğin ulaştığı kareler. Bir girdinin değişmesi
   (`update_character` gibi) onu adlandıran her kareye ulaşır, o kareler de buna girer.
3. **Check 4 yalnız kadro değiştiyse koşar.** Kadro senaryonun kadrosu: değişiklik bir karakteri
   ekledi, değiştirdi ya da çıkardıysa negatif liste yeniden yazılır; değilse Check 4 atlanır.
   Start a scenario ve Improve'da Check 4 her zaman koşar — koşul Edit prompts'un kendi adımında,
   `THE_CHECKS`'te değil.
4. **`THE_CHECKS`'in ilk satırı en az değişir.** Bugün *"each over every frame of the scenario"*
   diyor; Edit prompts'un önüne yazdığı *"yalnız değişikliğin ulaştığı kareler"* bununla çelişirdi.
   Satır varsayılanı korur ve adımın daraltmasına yer açar: *"… each over every frame of the scenario
   unless this step limits them."* Start a scenario ve Improve'da adım daraltmaz, okunuş aynı kalır.
5. **3. adım artık cevap değil.** Başlığı `Step 3 -- the prompts` olur; `build_prompts` yine çağrılır
   ve değişiklik söylenir, sonra onay beklemeden aynı turda 4. adıma geçilir — akışın 5. adımı gibi.
   Kapanış artık kontrollerin kapanışı: prompt dosyasını ve negatif dosyayı adlandırır, prompt'ları
   geri basmaz. Edit prompts'un eski *"The built file is the answer: its prompts are never printed
   back."* cümlesi kalkar, çünkü aynı kuralı kapanış söylüyor.
6. **Tavan.** Edit prompts kontrolleri taşıyınca ~825 kelime olur; tavanı 700'den 830'a çıkar,
   gerekçesi 367, 370 ve 373'ün yazdığı yorumda. Akış 1025'in içinde kalır (`THE_CHECKS`'e beş kelime),
   Improve 700'ün içinde.

## Kararlar (subagent'ın, kullanıcısız)

1. **Neden `THE_CHECKS` bölünmüyor ya da kopyalanmıyor.** Kontroller tek yerde durur (370'in kararı).
   Farklı olan yalnız iki şey — kapsam ve Check 4'ün koşulu —, ve ikisi de Edit prompts'un kendi
   adımına yazılır. Kapsamı `THE_CHECKS`'ten tamamen çıkarmak (her skill kendi kapsamını söyler) akışa
   ve Improve'a aynı cümleyi iki kez yazdırırdı; yerinde bırakıp *"unless this step limits them"*
   eklemek tek kopyayı korur.
2. **"Kadro değişti" ne demek.** Negatif liste *"from its cast"* — senaryonun karakterlerinden —
   yazılıyor (373). Bir karakter eklendi, değişti ya da çıktıysa liste eskir. Bir karede kimin
   durduğunun değişmesi senaryonun kadrosunu değiştirmez. Metin *"the scenario's cast"* der, çünkü
   Check 2'de *"the frame's cast"* başka bir şey. Koşul *"your change"*e bağlı: kontrollerin kendi
   eklediği görünürlük girdisi (Check 2) Check 4'ü tetiklemez, onu tetikleyen kullanıcının istediği
   değişikliktir.
3. **Değişiklik hiçbir kareye ulaşmadıysa** ayrıca bir cümle yazılmaz: önsöz zaten *"If no frame
   fails, say so and go on"* diyor.
4. **Plan.** Önsöz *"write in the plan which check it is"* diyor; Edit prompts plan yazmaz. Senaryoyu
   yapan Start a scenario bir plan yazmıştır, ve temel metin plansız uzun işe plan açtırır. Edit
   prompts'a plan satırı eklenmez; kapsam birkaç kare olduğu için iş nadiren tura sığmaz.
5. **Mevcut iki test değişir**, çünkü madde onların tuttuğu şeyi değiştiriyor:
   - `test_the_editor_writes_no_frames_at_all` — Check 1 bölünen kareyi `add_scene` ile yazar, ve
     kontroller artık Edit prompts'ta. Test, `add_scene`'in Edit prompts'un **kendi kısmında**
     (kontrollerden önce) olmadığını sorar; `add_frames` hâlâ hiçbir yerde yok.
   - `test_the_editor_closes_with_the_file_rather_than_a_menu` — kapanış artık kontrollerin. Test,
     Edit prompts'un kontrollerle bittiğini ve kapanışın prompt'ları geri basmadığını sorar.
6. **Testler olguları tutar**, 370–373'teki gibi. Edit prompts'un 4. adımı başlığından `THE_CHECKS`'in
   başladığı yere kadar kesilir.

## Testler

`queen-agent/backend/tests/test_skills.py`, Madde 373'ün bölümünün arkasında yeni bölüm *(Madde 374)*:

- `test_edit_prompts_ends_with_the_checks` — `_edit()` `THE_CHECKS` ile biter, onu bir kez taşır —
  **kırmızı**.
- `test_edit_prompts_runs_its_steps_in_order` — `Step 1 -- what the request is about`, `Step 2 -- the
  fix`, `Step 3 -- the prompts`, `Step 4 -- the checks` sırayla — **kırmızı**.
- `test_edit_prompts_goes_on_to_the_checks_in_the_same_turn` — 3. adımda `build_prompts again`,
  `which frames it reached`, `waits for no approval`, `Step 4`; `last word` yok — **kırmızı**.
- `test_after_an_edit_the_checks_read_only_the_frames_it_reached` — 4. adımda `limits the checks to the
  frames your change reached`; `THE_CHECKS`'te `every frame of the scenario unless this step limits
  them` — **kırmızı**. Akışta ve Improve'da `your change reached` yok.
- `test_after_an_edit_the_negative_is_written_again_only_if_the_cast_changed` — 4. adımda `Check 4
  runs only if`, `the scenario's cast`, `added, changed or taken out`; `THE_CHECKS`'te `runs only if`
  yok — **kırmızı**.

Değişen mevcut testler:

- `test_the_editor_writes_no_frames_at_all` — `add_scene` Edit prompts'un kendi kısmında yok —
  yeşil kalır (bugün de yok).
- `test_the_editor_closes_with_the_file_rather_than_a_menu` — `_edit()` `THE_CHECKS` ile biter, ve
  kapanışta `Do not print the prompts back` — **kırmızı**.
- `test_the_texts_stay_short_enough_to_be_read` — Edit prompts'un tavanı 830, gerekçesiyle — yeşil
  kalır.
