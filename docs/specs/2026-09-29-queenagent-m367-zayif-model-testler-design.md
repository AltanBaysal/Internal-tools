# Madde 367 (v9-8a) — Bütün skill'ler zayıf modeli bilir, ve `pov_` kalkar: testler

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 367 · v9-8a. *Kararları: v9-8*
— 29 Eylül paragrafları 28 Eylül metnini geçersiz kılar: H3 prompt'unu QueenAgent yazmaz, bu madde
hiçbir H3 ya da video prompt'u yazmaz.

**Kullanıcıdan gereken:** yok. Karar, dosya ya da ölçüm beklenmiyor. Tavanın yükselmesi kullanıcının
28 Eylül kararı; yeni sayılar teknik bir seçim, gerekçesiyle aşağıda.

## Ne değişiyor

Modele giden üç şey:

1. **Her skill metni zayıf modeli, tek anı ve 4 saniyeyi söyler.** Bugün iki skill var — Start a
   scenario ve Edit prompts *(`skills.py`'nin `INSTRUCTIONS`'ı)*. İkisi de yalnız "SDXL" diyor;
   modelin zayıf olduğunu, her karenin tek bir anın tek resmi olduğunu ve o resmin 4 saniyelik bir
   videoya dönüştüğünü söylemiyor.
2. **`pov_` kalkar.** Bugün üç yerde modele yazdırılıyor: Start a scenario'nun 2. adımı her karakter
   için bir `pov_` girdisi açtırıyor; Edit prompts'un 2. adımı POV karesinin kadrosuna `pov_` girdisini
   yazdırıyor; `add_character` ve `update_character`'ın `tags` tarifi `pov_` girdisinin sayı
   taşımadığını söylüyor. Yapı ve build kodunda `pov_`'a özel bir şey yok — `pov_` yalnız bir ad
   kuralıydı *(Madde 182)*. Üçü de gider; eski dosyalardaki `pov_` girdileri sıradan karakter olarak
   kalır.
3. **Kelime tavanı yükselir** *(kullanıcı kararı, 28 Eylül)*: Start a scenario 450 → 1000, Edit
   prompts 260 → 700.

## Kararlar (subagent'ın, kullanıcısız)

1. **"Her skill" testte `INSTRUCTIONS`'ın her girdisi**, bugünkü iki adın listesi değil: Improve
   *(370)* geldiğinde aynı test onu da tutar.
2. **Testler olguyu tutar, bir cümleyi değil:** metinde `weak`, `one moment` ve `4-second video`
   geçer. Nasıl yazılacağı uygulama spec'inin işi.
3. **Kare yazarı da zayıf modeli bilir.** `WRITE_FRAME_SYSTEM_PROMPT` bir skill değil, ama fotoğraf
   prompt'unun aksiyon satırını yazan metin o; kullanıcının şikâyeti — "modelin yapamayacağı kadar
   kompleks şeyleri yazıyor" — en çok orada doğuyor. Tek an ve kare zaten orada yazılı; 4 saniye
   eklenmez, çünkü o model yalnız fotoğrafı yazar. Testi: metinde `weak`.
4. **`pov_` için tek bir süpürme testi:** `prompt.py`'nin büyük harfle adlandırılmış her metni ve
   `TOOL_SPECS`'in tamamı `pov` içermez *(büyük-küçük harf gözetmeden)*. Araç metinlerinin hepsi
   `prompt.py`'den geliyor *(test_prompt.py'nin kendi testi)*; `TOOL_SPECS` ayrıca parametre adları için.
5. **`pov_`'u isteyen testler davranışla birlikte gider:**
   - `test_skills.py`: `test_the_flow_opens_a_pov_entry_beside_each_character`,
     `test_a_pov_entry_carries_neither_a_count_nor_an_outfit` *(kıyafet yarısı test_tools.py'de
     `those are outfits` olarak zaten tutuluyor)*, `test_a_pov_frame_names_the_pov_entry_in_its_cast`,
     ve Madde 182'nin başlık yorumu.
   - `test_tools.py`: `test_an_entry_for_somebody_half_in_shot_carries_no_count`.
   - `test_no_instruction_names_a_tool_that_is_gone`'daki `pov_` istisnası kalkar: bundan sonra
     skill metninde `pov_` geçerse o test de kırmızı olur.
   - `test_the_rules_carry_nothing_that_belongs_to_one_field`'in listesinden `pov_` çıkar: bir alana
     taşındığı için değil, hiç olmadığı için yok artık, ve bunu süpürme testi tutuyor.
6. **Tavanın kararı testin kendi yorumunda yazılır**, Madde 123'ün ve 20. düzeltmenin yazıldığı yerde
   *(`test_the_texts_stay_short_enough_to_be_read`)*. `prompt.py`'nin skill bloğundaki yorum da
   tavandan söz ediyor; uygulama turunda o yorum kararı tekrar etmeden teste işaret eder.
   - **Neden yükselir:** Madde 123'ün tavanı, uzun metnin ortasını okumayı bırakan, o günün daha
     zayıf modeli için kondu. Bugün metni okuyan model DeepSeek'in Flash'ı, ve kullanıcı kararıyla
     tavan yükseliyor.
   - **Neden bu sayılar:** kontroller *(370–373)* tek yerde yazılıp Start a scenario'nun son adımı
     olacak, Edit prompts da onlarla bitecek *(374)*; 368 ve 369 da sahne adımına birer cümle ekliyor.
     Yeni tavan onlara yer bırakır: iki metin de aşağı yukarı ikiye katlanabilir.
   - **Tavan yine bekçi:** tavana varan metne bir cümle, yine ancak bir cümle silinerek girer.

## Testler

`queen-agent/backend/tests/test_skills.py`:

- Her skill metni modelin zayıf olduğunu söyler (`weak`). — **kırmızı**
- Her skill metni bir karenin tek an olduğunu ve 4 saniyelik bir videoya döndüğünü söyler
  (`one moment`, `4-second video`). — **kırmızı**
- Tavan testi 1000 ve 700'e, kararıyla. — yeşil kalır *(tavan yükselmesi kırmızı veremez)*.
- `pov_`'u isteyen üç test ve istisna kalkar.

`queen-agent/backend/tests/test_prompt.py`:

- Modele söylenen hiçbir metin `pov` içermez. — **kırmızı**

`queen-agent/backend/tests/test_tools.py`:

- Kare yazarının metni modelin zayıf olduğunu söyler. — **kırmızı**
- `pov_`'u isteyen test ve listedeki `pov_` kalkar.

Frontend'e ve queen-editor'e dokunulmaz: `pov_` orada hiç geçmiyor.
