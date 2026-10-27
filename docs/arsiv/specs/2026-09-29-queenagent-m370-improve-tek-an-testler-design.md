# Madde 370 (v9-8b) — Improve skill'i açılır, ilk kontrolüyle: tek an mı — testler

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 370 · v9-8b. *Kararları:
v9-8; tasarım: 138, 179.* 29 Eylül paragrafları 28 Eylül metnini geçersiz kılar: H3 ve video prompt'u
QueenAgent'ın değil. Bir kareyi değiştiren kontrol yalnız onun **fotoğraf** prompt'unu yeniler; bölünen
kare kendi aksiyonunu ve fotoğraf prompt'unu alır.

**Kullanıcıdan gereken:** yok. Karar, dosya ya da ölçüm beklenmiyor. Aşağıdaki kararlar subagent'ın;
iki okunuşu olan tek nokta *(plan dosyası)* gerekçesiyle yazılı, ve rapora açık nokta olarak gider.

## Ne değişiyor

1. **Üçüncü skill: Improve** *(id `improve`, ad `Improve`)*. Seçicide en sonda, Edit prompts'tan
   sonra; açıklaması tasarımın sözü: *Run four checks on a scenario's frames and prompts, and say yes
   after each one.* Sunucuda `INSTRUCTIONS`'a kendi metniyle girer.
2. **Kontroller tek yerde yazılır:** `prompt.py`'de tek bir metin, `THE_CHECKS`. Improve'un metni ve
   Start a scenario'nun metni onunla **biter**; bugün bir skill ötekini çağıramadığı için iki metin
   aynı parçayı taşır. 371–373 kendi kontrollerini yalnız oraya ekler.
3. **İlk kontrol: tek an mı.** Birden fazla anı anlatan kare tek ana iner ya da bölünür. Değişen
   karenin fotoğraf prompt'u yenilenir, bölünen kare kendi aksiyonunu ve fotoğraf prompt'unu alır —
   bugünkü araçlarla: `update_frame`, `add_scene`, `write_missing_actions`, `build_prompts`.
4. **Her kontrol ne değiştirdiğini gösterir ve evet'i bekler.**
5. **Uzun senaryoda kontroller birkaç tura yayılır:** tur sınırı (16) değişmez, kalınan yeri plan
   dosyası tutar, kullanıcı "devam" der.
6. **Start a scenario altı adımlı olur:** 6. adım kontroller. 5. adım artık son söz değil — onay
   beklemeden kontrollere geçer; kapanış cümlesi *(dosyayı adlandır, bir şey önerme, bir şey sorma)*
   kontrollerin sonuna taşınır, böylece 371–373'ün kontrolleri de ondan önce girer.

## Kararlar (subagent'ın, kullanıcısız)

1. **"Tek yer" testte bir sabit:** `prompt.THE_CHECKS`. Test iki şeyi tutar: iki skill metni de onunla
   biter (`endswith`), ve her birinde bir kez geçer. Böylece kontrol iki kez yazılamaz ve Start a
   scenario'da son adım olur.
2. **Kontrolün testleri `THE_CHECKS`'e bakar**, skill'lere değil: kural tek yerde, test de orada.
   Olgular tutulur, cümleler değil: `one moment`, `split`, dört aracın adı, `photo prompt`, `wait for
   their yes`, `plan`, `continue`.
3. **Video ve H3 yok:** `THE_CHECKS`'te `video` ve `h3` geçmez *(29 Eylül kararı)*. Varlık testlerinden
   sonra sorulur, ki boş bir metinde geçmesin.
4. **Plan dosyası — iki okunuşu olan nokta.** Madde 203 (10 Eylül) akışın adımlarının plana
   dokunmadığını söyledi: nerede kalındığını dosyalar söylüyor. Kontrollerde dosyalar bunu söyleyemez —
   düzeltilmiş bir kare, bakılmamış bir kareyle aynı görünür. 28 Eylül kararı açık: *"kalınan yeri plan
   dosyası tutar"*. Seçilen: kontroller plana hangi kontrolde olduklarını yazar. Adım 1–5 yine plana
   dokunmaz; `test_no_step_is_ticked_off_the_plan_at_all` iddialarını tutar (`mark_step_done` ve
   `edit_file` adı akışta geçmez — hangi aracın yazacağını SYSTEM_PROMPT zaten söylüyor), ve yorumuna
   bu istisna yazılır. Yeni test: `THE_CHECKS` `plan` ve `continue` der.
5. **Kapanış kontrollerin içinde:** `offer nothing, and ask nothing` `THE_CHECKS`'te; akışın 5. adımında
   `last word` geçmez, ve 5. adım `waits for no approval` der — 1. adımın sözüyle aynı.
6. **Improve'un kimliği:** `You are an expert` ile açılır *(Madde 123'ün persona kuralı)*; var olan bir
   senaryo üstünde çalışır (`already`), ve senaryo açmaz (`start_scenario` geçmez).
7. **Improve'un tavanı: 700 kelime**, Edit prompts'unkiyle aynı; karar tavan testinin yorumunda,
   367'nin yazıldığı yerde. **Neden 700:** Improve'un kendi kısmı kısa — açılış, zayıf model, senaryoyu
   bulan bir adım; gerisi kontroller. Dört kontrol *(370–373)* ile bugünkü Edit prompts kadar yer
   tutar. Kontroller akışın 1000'ine de girdiği için onları asıl bağlayan akışın tavanı; Improve'unki
   kendi kısmının şişmesini tutar.
8. **`ALL_SKILLS`'e `improve` eklenir:** 367'nin parametreli testleri *(zayıf model, tek an, 4 saniye,
   SDXL, şema yok, talimat var)* Improve'u kendiliğinden tutar.
9. **Altı adım:** `STEPS`'e `Step 6 -- the checks` eklenir; `test_the_flow_runs_five_numbered_steps`
   `six steps` olur, `five steps` geçmez.
10. **`MUST_BE_FULL`'a** (`test_prompt.py`) `IMPROVE` ve `THE_CHECKS` girer.
11. **Frontend:** `skills.test.js` üç satırı bu sırayla ister, ve Improve'un satırı adını ve tasarımın
    açıklamasını birebir taşır. `SkillPicker.test.jsx` zaten `SKILLS`'in hepsini döner; dokunulmaz.
12. **Edit prompts'a dokunulmaz:** kontrollerle bitmesi 374'ün işi; yokluğu da iddia edilmez, yoksa 374
    bir testi silmek zorunda kalır.

## Testler

`queen-agent/backend/tests/test_skills.py`:

- `ALL_SKILLS` üç ad; `_improve()` yardımcısı. Parametreli testler Improve için — **kırmızı**
  *(talimatı yok)*; `test_the_menu_and_the_instructions_carry_the_same_names` — **kırmızı**.
- Kontroller tek yerde, iki skill onunla biter, her birinde bir kez — **kırmızı**.
- Tek an kontrolü: başlığı, `more than one moment`, `split`, dört araç, `photo prompt` — **kırmızı**.
- Her kontrol ne değiştirdiğini gösterir ve evet'i bekler — **kırmızı**.
- Kalınan yeri plan tutar, kullanıcı devam der — **kırmızı**.
- Kontroller video ve H3 anmaz — **kırmızı** *(varlık iddiası önce)*.
- Kapanış kontrollerin sonunda; 5. adım son söz değil ve onay beklemez — **kırmızı**.
- `STEPS` altı; altı adım testi — **kırmızı**.
- Improve bir persona ile açılır, var olanın üstünde çalışır, senaryo açmaz — **kırmızı**.
- Tavan testi Improve'u 700'de tutar — **kırmızı** *(talimat yok, `instruction_for` boş döner ama
  kontrol testleri zaten kırmızı; tavan satırı boş metinde yeşil kalabilir — kabul, tavan kırmızı
  veremez)*.
- `test_no_step_is_ticked_off_the_plan_at_all`'ın yorumu kontrollerin istisnasını söyler.

`queen-agent/backend/tests/test_prompt.py`:

- `MUST_BE_FULL`'a `IMPROVE` ve `THE_CHECKS` — **kırmızı**.

`queen-agent/frontend/src/features/workspace/skills.test.js`:

- Menü üç satır, sırayla `start-a-scenario`, `edit-prompts`, `improve` — **kırmızı**.
- Improve'un satırı: ad `Improve`, açıklama tasarımın cümlesi — **kırmızı**.

queen-editor'e dokunulmaz.
