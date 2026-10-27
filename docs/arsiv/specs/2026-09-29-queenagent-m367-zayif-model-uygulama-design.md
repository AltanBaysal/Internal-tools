# Madde 367 (v9-8a) — Bütün skill'ler zayıf modeli bilir, ve `pov_` kalkar: uygulama

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 367 · v9-8a. *Kararları: v9-8.*
**Testler:** [2026-09-29-queenagent-m367-zayif-model-testler-design.md](2026-09-29-queenagent-m367-zayif-model-testler-design.md)
— `5c013526`'da kırmızı.

**Kullanıcıdan gereken:** yok.

## Tek dosya

Değişen yalnız `queen-agent/backend/features/workspace/domain/prompt.py` — modele söylenen her metin
orada *(Madde 189)*. Kod değişmez: `pov_`'u tanıyan bir satır yok, yapı ve build ona dokunmuyor.

## Kararlar

1. **Zayıf model paragrafı bir kez yazılır, her skill onu taşır.** Yeni sabit `THE_IMAGE_MODEL`,
   skill bölümünde; Start a scenario ve Edit prompts onu açılış paragraflarının hemen arkasına
   ekler. Neden sabit: iki metin aynı olguyu söylüyor, ve iki kopya bu modülün kaldırmak için
   yazıldığı şey *(bir kural iki yerde, biri eskir)*. Improve *(370)* geldiğinde aynı sabiti taşır.
   `SYSTEM_PROMPT`'a girmez: temel metin görev adı taşımaz *(Madde 73; `test_the_base_names_no_task`)*.
2. **Metni:**
   > The prompts go to a weak text-to-image model of the SDXL family. It cannot draw anything
   > complex, so ask it only for what is simple to draw. Each frame is one moment, drawn as one still
   > picture, and that picture becomes a 4-second video.

   Yalnız bilgi ve onun doğrudan sonucu — *basit iste*. Kontrol yok: tek an kontrolü 370'in, çizebilir
   mi kontrolü 372'nin.
3. **Start a scenario'nun açılışı kısalır**, çünkü SDXL'i ve kareyi artık paragraf söylüyor:
   *"prompts for an SDXL-family image model, one frozen frame at a time"* →
   *"image prompts, one per frame"*.
4. **Kare yazarı** *(`WRITE_FRAME_SYSTEM_PROMPT`)*: *"An SDXL-family image model draws it."* →
   *"A weak SDXL-family image model draws it, and it cannot draw anything complex."* 4 saniye girmez.
5. **`pov_` üç yerden çıkar:** Start a scenario'nun 2. adımının son maddesi, Edit prompts'un 2.
   adımının son maddesi, `ADD_CHARACTER_TAGS`'in `pov_` cümlesi *(`UPDATE_CHARACTER_TAGS` ondan
   türüyor, kendiliğinden düşer)*. Yerine bir şey yazılmaz: modele "`pov_` yazma" demek, bilmediği bir
   şeyi ona öğretmek olur. Görünmeyen parçaların işi 371'in.
6. **Yorumlar bugünü söyler:** skill bloğundaki tavan yorumu kararı tekrar etmez, teste işaret eder;
   34. düzeltmenin yorumundaki *"a pov_ entry"* çıkar.

## Görünen sonuç

Her skill metni zayıf modeli, tek anı ve 4 saniyelik videoyu söylüyor; kare yazarı zayıf modeli
biliyor; modele giden hiçbir metin `pov` içermiyor. Suite yeşil.
