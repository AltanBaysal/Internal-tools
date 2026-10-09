# Madde 371 (v9-8c) — Kontrol: yalnız görünen parçalar — testler

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 371 · v9-8c. *Kararları:
v9-8.* 29 Eylül paragrafları 28 Eylül metnini geçersiz kılar: H3 ve video prompt'u QueenAgent'ın değil.
Kullanıcının sözü: *"bu pov olayını var on ukaldırıyorum ve diyorumki ypatığın açıda o hangi karakterin
hangi parçaları görünüuorsa onları yaz prompta yoksa model zayıf olduğu için o özellikleri öteki
karakterler eklyior"*. Satır: kamera açısından hangi karakterin hangi parçaları görünüyorsa prompt'a
yalnız onlar girer; gerekirse görünürlük girdisi eklenir *(`man body no face`, kıyafetin `from behind`
hâli gibi)*.

**Kullanıcıdan gereken:** yok. Karar, dosya ya da ölçüm beklenmiyor. Aşağıdaki kararlar subagent'ın.

## Ne değişiyor

1. **İkinci kontrol: yalnız görünen parçalar.** `prompt.THE_CHECKS`'te `Check 1`'den sonra, kapanış
   cümlesinden önce. Böylece Start a scenario'nun 6. adımı ve Improve'un 2. adımı onu kendiliğinden
   taşır *(370'in tek yeri)*.
2. **Açı karenin aksiyonundan okunur.** Kamera açısı 5. adımda, aksiyon satırının içinde yazılıyor
   (`WRITE_FRAME_SYSTEM_PROMPT`: *"write the framing and angle into your line"*); ayrı bir kamera alanı
   yok. Kontrol her karenin açısına bakar, ve her karakterin o açıdan hangi parçalarının göründüğünü
   sorar.
3. **Düzeltme araçlarla yapılır, yeni kod yok.** Bugün bir kare kadrosunu isimle tutar: her karakter,
   giydiği kıyafetlerin listesiyle (`update_frame`'in `characters`'ı); `build_prompts` her ismin
   girdisini olduğu gibi prompt'a koyar. "Bu karede bu karakterin yalnız şu parçaları" demenin araç
   düzeyinde tek yolu **görünürlük başına ayrı bir girdi**: görünen kısmı taşıyan yeni bir karakter ya da
   kıyafet girdisi (`add_character`, `add_outfit`), ve karenin kadrosunu ona çeviren `update_frame`.
   Satırın örnekleri tam bu: `man body no face`, kıyafetin `from behind` hâli. Açıdan hiç görünmeyen
   karakter karenin kadrosundan `update_frame` ile çıkar.
4. **Asıl girdiye dokunulmaz.** Aynı karakteri öteki kareler bütün hâliyle gösteriyor; asıl girdiyi
   değiştirmek (`update_character`, `update_outfit`) o kareleri bozar.

## Kararlar (subagent'ın, kullanıcısız)

1. **Testler `THE_CHECKS`'e bakar**, 370'teki gibi: kural tek yerde, test de orada. İki skill'in onunla
   bittiğini 370'in testi zaten tutuyor.
2. **Kontrolün kendi bloğu sorulur:** `Check 2 -- visible parts` başlığından kapanış cümlesinin başına
   (`When the checks are done`) kadar olan dilim. Sıra: `Check 1` < `Check 2` < kapanış.
3. **Olgular tutulur, cümleler değil:** blokta `angle`; iki örnek `no face` ve `from behind`; araçlar
   `add_character`, `add_outfit`, `update_frame`.
4. **Asıl girdiye dokunulmaz:** blokta `update_character` ve `update_outfit` geçmez — varlık
   iddialarından sonra sorulur, ki boş bir metinde geçmesin.
5. **`pov` yasağı yerinde kalır:** `test_prompt.py`'nin taraması `THE_CHECKS`'i zaten okuyor; yeni test
   gerekmez.
6. **Tavanlar değişmez** (akış 1000, Improve 700): 367'nin kararı bu kontrol için yer bırakmıştı.
7. **Edit prompts'a dokunulmaz** *(374'ün işi)*; 372 ve 373'ün kontrolleri de yazılmaz.

## Testler

`queen-agent/backend/tests/test_skills.py`, Madde 370'in bölümünün altında yeni bölüm *(Madde 371)*:

- `test_the_second_check_comes_after_the_first_and_before_the_closing` — başlık var, sıra doğru —
  **kırmızı**.
- `test_the_second_check_reads_what_the_angle_shows` — blokta `angle`, `no face`, `from behind` —
  **kırmızı**.
- `test_a_part_the_angle_hides_goes_through_an_entry_of_its_own` — blokta `add_character`,
  `add_outfit`, `update_frame`; `update_character` ve `update_outfit` yok — **kırmızı**.

queen-editor'e ve frontend'e dokunulmaz.
