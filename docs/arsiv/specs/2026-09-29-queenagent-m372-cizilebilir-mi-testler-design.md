# Madde 372 (v9-8d) — Kontrol: zayıf model bunu çizebilir mi — testler

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 372 · v9-8d. *Kararları:
v9-8.* 29 Eylül paragrafları 28 Eylül metnini geçersiz kılar: H3 ve video prompt'u QueenAgent'ın değil.
Kullanıcının sözü: *"fotoğra üretene yapay zeka modeli çok zayıf sence yazdığın promptu bu yapayzeka
üretevbilir"*. Satır: son hâldeki prompt'a bakar, ve çizilemeyecek olanı sadeleştirir. Akıştaki yeri:
tek an (Check 1) ve görünen parçalar (Check 2) bittikten sonra — *"son hâldeki prompt'a bakar"*.

**Kullanıcıdan gereken:** yok. Karar, dosya ya da ölçüm beklenmiyor. Aşağıdaki kararlar subagent'ın.

## Ne değişiyor

1. **Üçüncü kontrol: çizilebilir mi.** `prompt.THE_CHECKS`'te `Check 2`'den sonra, kapanış cümlesinden
   önce. Start a scenario'nun 6. adımı ve Improve'un 2. adımı onu kendiliğinden taşır *(370'in tek
   yeri)*.
2. **Son hâldeki prompt okunur.** Son hâl, `build_prompts`'un yazdığı dosya: her karenin `{scene,
   photo}` kaydı *(366)*. Önsöz her kontrolden sonra `build_prompts`'u çağırttığı için dosya Check 1 ve
   2'den sonra günceldir. Kontrol yapı dosyasını değil, bu dosyadaki fotoğraf prompt'larını okur.
3. **Düzeltme, parçanın geldiği yerde.** `build_prompts.py`'ye göre bir fotoğraf prompt'u şunlardan
   birleşir: kalite zinciri (kodun, dokunulmaz); her kişinin karakter girdisi ve giydiği kıyafet
   girdileri; karenin aksiyonu; mekânın girdisi. Prompt'un kendisi elle düzeltilmez — yeniden kurulur.
   Bu yüzden çizilemeyen parça geldiği yerde sadeleşir: aksiyon karenin kendisinin (`update_frame`);
   karakter, kıyafet ve mekân birer girdi (`update_character`, `update_outfit`, `update_location`), ve
   girdi değişikliği onu adlandıran her kareye ulaşır.
4. **Zayıf model yeniden anlatılmaz.** `THE_IMAGE_MODEL` *(367)* bunu her skill'e zaten söylüyor;
   kontrol yalnız ne yaptığını söyler.

## Kararlar (subagent'ın, kullanıcısız)

1. **Testler `THE_CHECKS`'e bakar**, 370 ve 371'deki gibi. İki skill'in onunla bittiğini 370'in testi
   tutuyor.
2. **Kontrolün kendi bloğu sorulur:** `Check 3 -- can it be drawn` başlığından bloğun sonundaki boş
   satıra kadar olan dilim. Sıra: `Check 2` < `Check 3` < kapanış.
3. **371'in dilimi kendi bloğunda biter.** Bugün `_second_check()` `Check 2`'den kapanışa kadar
   kesiyor; `Check 3` araya girince o dilim onu da içerir, ve 371'in "blokta `update_character` ve
   `update_outfit` yok" iddiası Check 3'ün araçlarına takılır. Dilim, bloğun sonundaki boş satırda biter
   (bloklar birbirinden bir boş satırla ayrılıyor). Kırmızı hâlde de 371'in testleri yeşil kalır.
4. **Olgular tutulur, cümleler değil:** blokta `build_prompts` (okunan dosya), `final` (son hâl),
   `photo prompt`; sadeleştirme (`simplif`); araçlar `update_frame`, `update_character`,
   `update_outfit`, `update_location`.
5. **Tekrar yok:** blokta `weak` geçmez, ve `THE_IMAGE_MODEL` `THE_CHECKS`'in içinde değil — varlık
   iddialarından sonra sorulur, ki boş bir metinde geçmesin.
6. **Tavanlar değişmez** (akış 1000, Improve 700). 373 de `THE_CHECKS`'e girecek; blok kısa tutulur.
   Sığmazsa tavan yükseltilmez, durulur.
7. **Edit prompts'a dokunulmaz** *(374)*; 373'ün kontrolü yazılmaz.

## Testler

`queen-agent/backend/tests/test_skills.py`, Madde 371'in bölümünün altında yeni bölüm *(Madde 372)*:

- `test_the_third_check_comes_after_the_second_and_before_the_closing` — başlık var, sıra doğru —
  **kırmızı**.
- `test_the_third_check_reads_the_prompts_in_their_final_form` — blokta `build_prompts`, `final`,
  `photo prompt` — **kırmızı**.
- `test_the_third_check_simplifies_the_part_where_it_comes_from` — blokta `simplif` ve dört araç —
  **kırmızı**.
- `test_the_third_check_does_not_tell_the_model_is_weak_again` — blokta `weak` yok, `THE_IMAGE_MODEL`
  `THE_CHECKS`'te yok — **kırmızı** (blok yokken dilim alınamaz).

Değişen yardımcı: `_second_check()` bloğun sonundaki boş satırda biter; 371'in üç testi yeşil kalır.

queen-editor'e ve frontend'e dokunulmaz.
