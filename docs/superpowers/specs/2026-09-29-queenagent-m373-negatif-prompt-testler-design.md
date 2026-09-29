# Madde 373 (v9-8e) — Negatif prompt — testler

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 373 · v9-8e. *Kararları:
v9-8 ve v9-7.* 29 Eylül paragrafları 28 Eylül metnini geçersiz kılar: H3 ve video prompt'u QueenAgent'ın
değil. Kullanıcının sözü: *"senaryoya ve karakterlere özel negatic promtplar yazıdıyıroum karakterlerin
özeliklkerinin karışmaması için"*. Satır: senaryo başına tek liste, kadroya göre, kontrollerin en
sonunda; prompt listesinin yanında ayrı bir dosyaya yazılır *(v9-7 — "abi negatif ayrı dursun queen
agentta user manuel kopyala yapıştır yapsın")*. Kullanıcının bulduğu dersler uygulanır: negatif kişiye
özel çalışmaz, asıl çözüm pozitif tarafta; koyu ten negatife yazılmaz — yazılınca adam beyaz çıktı —,
yerine adama özel karşıt etiketler girer (`pale male`, `white man`); karakterin kendi özellikleri
negatife girmez.

**Kullanıcıdan gereken:** yok. Karar, dosya ya da ölçüm beklenmiyor. Aşağıdaki kararlar subagent'ın.

## Ne değişiyor

1. **Dördüncü kontrol: negatif prompt.** `prompt.THE_CHECKS`'te `Check 3`'ten sonra, kapanış
   paragrafından önce, başlığı `Check 4 -- the negative prompt`. Seçicideki açıklama zaten *four checks*
   diyor *(370)*. Start a scenario'nun 6. adımı ve Improve'un 2. adımı onu kendiliğinden taşır.
2. **Tek liste, kadrodan, bütün hâlinde.** Senaryo başına bir negatif prompt, kadronun bugünkü
   hâlinden yazılır, ve her seferinde bütün olarak verilir — eski listeye eklenmez. 374 kadro
   değişince listeyi yeniden yazdıracak; metin bunun "baştan yazmak" olduğunu şimdiden söyler.
3. **Kullanıcının dersleri metinde:** liste bütün resme işler, bir kişiye değil; bu yüzden bir
   karakterin kendi özelliği yazılmaz (koyu ten yazılınca adam beyaz çıktı); yerine özelliğin karşıtı,
   yalnız sahibine uyan kelimelerle (`pale male`, `white man`). Yapılamıyorsa yazılmaz — özelliği
   sahibinde tutan pozitif taraftır.
4. **Kontrol kare değiştirmez;** listeyi gösterir ve evet'i bekler (önsözün kuralı).
5. **Ayrı dosya, onu yazan bir araçla: `write_negative`.** Girdileri: yapı dosyasının adı (`file`) ve
   liste (`tags`). Dosyanın adı kodun: yapının adı + `-negative.txt` — `bar-scene.json` →
   `bar-scene-negative.txt`, `build_prompts`'un yazdığı `bar-scene.py`'nin yanında. İçinde yalnız
   etiketler var, Python sarmalı yok: dosya panelinin Copy düğmesi dosyanın tamamını kopyalar *(193)*,
   ve kullanıcı onu doğrudan queen-editor'ün negatif alanına yapıştırır. Her çağrı öncekini ezer.
6. **Kapanış iki dosyayı da adlandırır:** prompt dosyası ve negatif dosyası.

## Kararlar (subagent'ın, kullanıcısız)

1. **Neden yeni bir araç, `create_file` değil.** `create_file` alınmış adı reddeder, yani liste ikinci
   kez (374) ancak `edit_file` ile, eski metni birebir alıntılayarak değişirdi — bu yama, baştan yazma
   değil. Adı da modelin uydurmasına kalırdı; FOUNDATION 5: her seferinde aynı çıkması gereken şeyi kod
   kurar. Araç küçük: dosya var mı, etiket boş mu, yaz.
2. **Liste yapı dosyasına girmez.** Yapı dosyası kareleri ve girdileri tutar; negatif liste
   `build_prompts`'un birleştirdiği bir parça değil, modelin yazdığı bir metin. Kendi dosyası tek iş.
3. **Araç yapı dosyası yoksa reddeder** (`There is no file by that name.`), hiçbir şey yazmaz: yanına
   yazılacak liste yoksa isim bir yazım hatasından gelir. JSON'u açmaz — içeriği okumaz, yalnız varlığı.
4. **Boş liste reddedilir**, hiçbir şey yazmaz.
5. **Kartlar:** `write_negative` `WRITES_FILES`'ta — sohbet dosya kartı çizer. `created` yazılan dosya,
   `target` yapı dosyası (`build_prompts` gibi), `outcome` `Written`.
6. **Modlar:** edit modu sormadan çalıştırır (mevcut test bunu her araç için zaten ister); ask modu
   sorar — `test_modes.py`'nin `WRITES` listesine girer.
7. **Tavan.** Blok ve kapanıştaki ek, Start a scenario'nun kalan ~100 kelimesini aşar. Akışın tavanı
   1000'den 1025'e çıkar, gerekçesi 367 ve 370'in yazdığı yorumda. Improve 700'de kalır (~660).
8. **Testler olguları tutar, cümleleri değil**, 370–372'deki gibi. Blok `Check 4` başlığından bloğun
   sonundaki boş satıra kadar kesilir.
9. **Frontend değişmez:** dosya paneli her dosyayı gösterir ve Copy düğmesi dosyanın tamamını kopyalar.
   queen-editor'e dokunulmaz. Edit prompts'a dokunulmaz *(374)*.

## Testler

`queen-agent/backend/tests/test_skills.py`, Madde 372'nin bölümünün altında yeni bölüm *(Madde 373)*:

- `test_the_fourth_check_comes_after_the_third_and_before_the_closing` — **kırmızı**.
- `test_the_negative_prompt_is_one_list_written_whole_from_the_cast` — blokta `one negative prompt`,
  `cast`, `write_negative`, `never added to` — **kırmızı**.
- `test_the_negative_prompt_never_holds_a_characters_own_feature` — blokta `own feature`, `whole
  picture`, `pale male`, `white man` — **kırmızı**.
- `test_the_negative_check_changes_no_frame_and_waits_for_a_yes` — blokta `no frame`, `wait for their
  yes` — **kırmızı**.
- `test_the_closing_names_the_negative_file_too` — kapanışta `negative file` — **kırmızı**.
- `test_the_texts_stay_short_enough_to_be_read` — akışın tavanı 1025, gerekçesiyle — yeşil kalır.

`queen-agent/backend/tests/test_tools.py`, yeni bölüm *(Madde 373)*:

- `test_every_tool_is_declared_to_the_model` — kümeye `write_negative` — **kırmızı**.
- `test_the_negative_list_is_written_beside_the_prompt_list` — `bar-scene.json` için
  `bar-scene-negative.txt`, içinde yalnız verilen etiketler; `created` o dosya; araç `WRITES_FILES`'ta —
  **kırmızı**.
- `test_writing_the_negative_again_replaces_it` — ikinci çağrı ezer; projede numaralı kopya yok —
  **kırmızı**.
- `test_a_negative_for_a_scenario_that_is_not_there_is_refused` — `no file by that name`, dosya yok —
  **kırmızı**.
- `test_a_negative_with_no_tags_is_refused` — hiçbir şey yazılmaz — **kırmızı**.
- `test_the_negative_call_reports_the_structure_and_says_it_wrote` — `target` yapı dosyası, `outcome`
  `Written` — **kırmızı**.
- `test_the_negative_tool_says_the_file_is_one_list_to_copy_whole` — açıklamada `negative`, `copy`,
  `replaces` — **kırmızı**.

`queen-agent/backend/tests/test_modes.py`: `WRITES`'a `write_negative` — `test_ask_mode_asks_before_it_writes`
**kırmızı** (bilinmeyen araç sorulmaz).
