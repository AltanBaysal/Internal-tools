# Madde 492 · QueenAgent Krea için prompt yazar — plan

**Hedef:** iki salt okunur prompt belgesi (`sdxl-prompt-writing.md`, `krea-prompt-writing.md`) her
projenin dosyalarında; seçicide dört skill, Improve yok; türü dosyanın adı söyleyen SDXL ve Krea
senaryoları; dört yeni Krea aracı ve `sdxl_` önekli dokuz araç; `SDXL_DOCUMENT` artık her isteğe gitmez.

**Spec:** [m492](../specs/2026-10-22-queen-agent-m492-krea-prompts-design.md) — metinlerin tam hâli onun
eklerinde ve tablolarında; bu plan onları kopyalamaz, yerini söyler.

Her görevde önce testler yazılır ve kırmızı görülür, sonra kod. Yollar `queen-agent/` altında. Takımlar
teker teker koşar. Var olan kodu yeniden yapılandırmak gerekirse durulur ve ana ajana sorulur.

## Görev 1: Metinler — `prompt.py`, `skills.py`

1. **Testler, `backend/tests/test_prompt.py`:**
   - `test_no_tool_carries_the_sdxl_document` → `test_no_tool_carries_a_guides_rule`: `GUIDES`'ın iki
     metninin her `- ` satırı hiçbir araç ve alan açıklamasında yok (`_descriptions_in` ile); önce her
     belgede > 5 kural olduğu söylenir.
   - Yeni: hiçbir belgenin kural satırı `SYSTEM_PROMPT`'ta yok.
   - Yeni: Krea belgesinde `SDXL`, `Danbooru`, `tag` olarak yazılmış kurallar (`Write tags`) yok; SDXL
     belgesinde `Krea` yok. SDXL belgesi bugünkü `SDXL_DOCUMENT`'ın her kural satırını, `solo`'yu,
     *whoever is written first*'ü, *fixed order*'ı ve *The scene*'i taşıyor.
   - `MUST_BE_FULL`: `SDXL_DOCUMENT` ve `IMPROVE` çıkar, `KREA_START_SCENARIO`, `KREA_EDIT` girer;
     `GUIDES`'ın iki metni ayrı bir testle dolu.
   - `test_no_text_is_still_written_down_where_it_used_to_live`: `("prompt", "SDXL_DOCUMENT")` ve
     `("prompt", "IMPROVE")` eklenir (kaynakta atanmamış).
2. **Testler, `backend/tests/test_tools.py`, açıklamalar (kabaca 1150 – 1300):**
   - `_rules()` `GUIDES["sdxl-prompt-writing.md"]`'yi döner.
   - `test_solo_is_kept_out_of_a_character` → solo artık belgede, alanda yok.
   - `test_the_rules_carry_nothing_that_belongs_to_one_field`: listeden `solo` çıkar, öbür dördü kalır.
   - `test_the_frames_action_points_at_the_document_by_its_title` silinir.
   - Yeni: `characters` ve `before` alanlarının spec'teki kısa cümleleri; `ADD_FRAME`'in eklenen iki
     cümlesi; hiçbir açıklamada *as tags*, *in English*, *Never tags*, *written first*, *in your own
     words*, *fixed order* yok.
   - Yeni: araç adları ve önekler — `sdxl_` / `krea_` ile başlayan her aracın açıklaması *"SDXL
     scenario:"* / *"Krea scenario:"* ile, öneksiz `remove_frame` ve `build_prompts` *"SDXL or Krea
     scenario:"* ile başlıyor; `read_file`, `create_file`, `edit_file` önek almıyor; 18 araç.
   - `test_add_frame_says_where_the_action_is_written`: *"… with sdxl_update_frame."*
   - `test_create_file_no_longer_offers_to_write_a_structure`: *"sdxl_start_scenario and
     krea_start_scenario open those"*.
3. **Testler, `backend/tests/test_skills.py`:**
   - `ALL_SKILLS = ["edit-prompts", "krea-edit", "krea-start-scenario", "start-a-scenario"]`;
     `SDXL_SKILLS`, `KREA_SKILLS`.
   - `improve`, `DELETED` listesine girer; Improve'un bütün testleri (`IMPROVE_STEPS`, `_improve*`,
     700 – 775) silinir; tavan testinden `_improve` satırı çıkar.
   - Yeni: her SDXL skill'i `"Read sdxl-prompt-writing.md first.\n\n"` ile, her Krea skill'i
     `"Read krea-prompt-writing.md first.\n\n"` ile başlıyor; Krea skill'lerinde `SDXL`, `sdxl`, `tag`
     olarak yazma kuralı yok; SDXL skill'lerinde `krea` yok.
   - Persona testleri (`test_the_flow_opens_as_a_persona`, `test_the_editor_opens_as_a_persona`) ikinci
     paragrafa bakar; Krea'nın ikisi için de aynısı.
   - `test_every_skill_says_what_the_prompts_are_for`: *makes a photo / starts from the photo* dört skill
     için; *"The image model is weak"* yalnız `SDXL_SKILLS` için.
   - `test_no_instruction_carries_the_prompt_rules`: hiçbir skill bir belgenin tamamını taşımıyor.
   - `test_the_checks_are_written_in_the_flow_itself`: dışarıda tutulanlar `START_A_SCENARIO`,
     `EDIT_PROMPTS`, `KREA_START_SCENARIO`, `KREA_EDIT` — dördü de kendi skill'i (Krea edit'in *"- Build
     the prompts again."* satırı Step 6 – 9'unkiyle aynı); `IMPROVE` çıkar.
   - Krea start: beş adım sırayla (`Step 1 -- open the scenario with its name and style` …); Step 1
     adı ve stili soruyor; Step 2 sahneleri İngilizce, cümleyle, sözler tırnakta, dört saniyede yazdırıyor;
     Step 3 `-notes.md`; Step 4 notlardan, toplu, onaysız; kapanış *"Tell the user the prompts are
     complete."*
   - Krea edit: senaryoyu ve notları okuyor; görünüş değişikliği notlara ve karelere; *"Build the
     prompts again."*
   - `test_the_scenes_are_written_in_english_with_the_words_in_quotes`: Step 4 *"- Write each scene in
     sentences, never as tags.\n"*'i de taşıyor.
   - Tavanlar: `_flow` ≤ 1835 (kullanıcı, 22 Ekim — Step 4'ün sahne satırı), `_edit` ≤ 205, Krea start
     ≤ 430, Krea edit ≤ 270; yorumda kararın kendisi.
4. **`backend/features/workspace/domain/prompt.py`:**
   - `SDXL_DOCUMENT` ve onun yorum bloğu yerine `GUIDES` (spec Ek A, Ek B), yorumu kullanıcının 22 Ekim
     sözleriyle; modül açıklamasındaki `SDXL_DOCUMENT` cümlesi `GUIDES`'a döner.
   - `IMPROVE` silinir; skill bloğunun yorumu dört metni söyler.
   - `START_A_SCENARIO`, `EDIT_PROMPTS`: başa `"Read sdxl-prompt-writing.md first.\n\n"`.
     `START_A_SCENARIO` Step 4'te *"- Write each scene in English.\n"*'in arkasına *"- Write each scene in
     sentences, never as tags.\n"* (kullanıcı, 22 Ekim).
   - `KREA_START_SCENARIO` (Ek C), `KREA_EDIT` (Ek D).
   - Açıklamalar spec'in 4. bölümünün tablolarına göre; yeni Krea sabitleri.
5. **`backend/features/workspace/domain/skills.py`:** `INSTRUCTIONS`'ta dört kimlik; `improve` çıkar;
   modül açıklaması.

## Görev 2: Tür ve Krea kurucusu — `krea_prompts.py`, `tools.py`

6. **Testler, yeni `backend/tests/test_krea_prompts.py`:** `krea_problems` — doğru biçim boş liste;
   üst düzeyde eksik `style` / `frames`, fazla anahtar, metin olmayan stil, liste olmayan `frames`, karede
   fazla (`characters`) ve eksik (`prompt`) anahtar, nesne olmayan kare: hepsi birden, dosya ve kare
   numarasıyla. `build_krea_prompts` — her kare `{"scene", "photo": style + " " + prompt}`, kenar
   boşlukları kırpılmış; boş stil ve boş prompt'lar hepsi birden `BadStructure`; kare yoksa
   `BadStructure`.
7. **Testler, `backend/tests/test_tools.py`, ad ve tür:**
   - Bütün çağrılar yeni adlarla (`sdxl_…`), senaryo adları `….sdxl.json` (yaklaşık 130 ad, 240 `.json`);
     testlerin söylediği şey değişmez.
   - `scenario_kind` tablosu (`.sdxl.json`, `.KREA.JSON`, `.json`, `.md`, `x.sdxl`); `scenario_name`
     tablosu (`plaj`, `plaj.json`, `plaj.krea`, `plaj.krea.json` iki türle).
   - Türsüz ad her senaryo aracında ve `build_prompts`'ta *"plaj.json is not a valid scenario file."*,
     dosya okunmadan (sayan sahte store ile 0 okuma); öbür tür doğru öneki adlayarak.
   - SDXL dosyasında `style` ya da karede `prompt` → ret, hiçbir şey yazılmıyor; `_build`'in SDXL yolu da.
   - Krea: `krea_start_scenario` dosyayı `{"style", "frames": []}` ile açıyor, alınmış adı reddediyor,
     boş stili reddediyor; `krea_set_style`; `krea_add_frame` sona ve `before` ile, `number` yazmadan,
     bozuk bir karede hiçbirini yazmadan; `krea_update_frame` sahne ve prompt, boşu reddediyor;
     `remove_frame` Krea'da numara yazmıyor, SDXL'de bugünkü gibi; `build_prompts` `.krea.py` ve
     `.sdxl.py`.
   - `WRITES_FILES` dört ad.
8. **`backend/features/workspace/domain/krea_prompts.py`** (yeni): `krea_problems`, `build_krea_prompts`.
9. **`backend/features/workspace/domain/tools.py`:** `TOOL_SPECS` (adlar, dört Krea aracı);
   `scenario_kind`; `scenario_name(name, kind)`; `run_tool`'un dalları; `_shut` cümlesi; SDXL biçim
   fonksiyonu (`_opened` ve `_build` çağırır); Krea açılışı (`krea_problems` ile); Krea araçlarının
   işleyicileri, `_numbered`, `_saved` ve yerleştirme paylaşılır; `_remove_frame` türe göre;
   `_build` türe göre, *"written over by its own output"* reddi silinir. Sebepler yorumlarda.
10. **Testler, `backend/tests/test_modes.py`:** adlar; dört Krea aracı EDIT'te sorulmadan, ASK ve PLAN'da
    soruluyor. **`backend/features/workspace/domain/modes.py`:** adlar ve dört yeni ad.

## Görev 3: Belgeler dosyalarda — `FileFileStore`, `delete_file`, `main.py`, `model_engine`

11. **Testler, `backend/tests/test_read_file.py`, `test_files_api.py`, `test_delete.py`:**
    - `FileFileStore(store, projects, GUIDES, "2026-10-22T…")` ile: `list_names` ve `list_files` projenin
      satırları ve iki belge, belgenin satırı `md` ve açılış anı; aynı adlı satır listede bir kez (belge);
      `read` ve `read_body` belgeyi bellekten veriyor — sayan sahte store ile 0 Drive okuması;
      `GET …/files` ve `GET …/files/<belge>` belgeyi gösteriyor.
    - `DELETE …/files/sdxl-prompt-writing.md` → 409, `error` belgenin adını ve *read-only*'yi söylüyor;
      store'a dokunulmuyor.
    - `edit_file` ve `create_file` belgeye: *"… is read-only; it is read, not written."*, okunmadan.
12. **Belgeyle ilgisi olmayan testlerin kurulumu:** `FileFileStore(...)` kuran yardımcılar (`test_tools`,
    `test_run_turn`, `test_delete_project`, `test_last_activity`, `test_projects_api`, `test_pin_archive`,
    `test_files_api`, `test_read_file`, `test_delete`) belgesiz kurar: `guides={}`, `listed_at=""`; dosya
    listesi assert'leri değişmez.
13. **`backend/features/workspace/data/file_file_store.py`:** kurucu `guides`, `listed_at`; `list_names`,
    `list_files`, `read`, `read_body` spec'in 2. bölümüne göre; modül açıklaması.
14. **`backend/features/workspace/domain/errors.py`:** `ReadOnlyFile`. **`domain/usecases/delete_file.py`:**
    ad `GUIDES`'taysa `ReadOnlyFile`. **`presentation/routes.py`:** `delete_project_file` onu 409'a
    çevirir.
15. **Testler, `backend/tests/test_composition.py`:** `main.py`'nin `FileFileStore`'u `GUIDES`'la kurduğu.
    **`main.py`:** `GUIDES` ve açılış anı, bir kez.
16. **Testler, `backend/tests/test_model_engine.py`:** sabit baş tek system mesajı (`system_prompt()`),
    roller `system, user, assistant`; hiçbir istekte belge yok. **`data/model_engine.py`:** `_for_model`
    yalnız `system_prompt()`; import ve yorum.
17. **`backend/features/workspace/domain/ports.py`:** `stream_alone`'un belge dizesi (82. satır) *"SDXL
    document"*u anıyor; sabit baş artık yalnız system prompt, cümle buna göre.

## Görev 4: Seçici — ön yüz

18. **Testler, `frontend/src/features/workspace/skills.test.js`:** dört kimlik sırayla; adlar *SDXL start
    scenario, SDXL edit, Krea start scenario, Krea edit*; Krea satırlarının `detail`'i Krea'yı adlıyor,
    Krea edit'inki *already* ve *fix|change*; `skillName("improve")` → `"improve"`; Improve testi silinir.
19. **`frontend/src/features/workspace/skills.js`:** spec'in 7. bölümündeki dört satır; yorum.

## Görev 5: Bitiş

20. `queen-agent` altında (dist hariç) eski adların taranması: `"start_scenario"`, `"set_character"`,
    `"add_frame"`, `"update_frame"` vb. yalnız `sdxl_` önekiyle; `SDXL_DOCUMENT`, `IMPROVE`, `"improve"`
    yalnız `DELETED`'de ve `skillName` testinde.
21. `npm run build --prefix queen-agent/frontend` (coder kurar; commit kullanıcının).
22. Dört takım teker teker: `python -m pytest queen-agent -q`, `npm test --prefix queen-agent/frontend`,
    `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`. Stage ve commit yok.
