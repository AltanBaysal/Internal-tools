# Madde 371 (v9-8c) — Kontrol: yalnız görünen parçalar — uygulama

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 371 · v9-8c.
**Testler:** [testler spec'i](2026-09-29-queenagent-m371-gorunen-parcalar-testler-design.md), kırmızı
commit `5cda0452`. Bu spec yalnız o testlerin istediğini yazar.

**Kullanıcıdan gereken:** yok.

## Parçalar

1. **`prompt.py` — `THE_CHECKS`**: `Check 1`'in son satırı ile kapanış cümlesi arasına, bir boş satırla
   ayrılmış `Check 2 -- visible parts` bloğu. Start a scenario'nun 6. adımı ve Improve'un 2. adımı onu
   `THE_CHECKS` üstünden kendiliğinden taşır.
2. **`prompt.py` — `THE_CHECKS`'in docstring'i**: bugünü söyler — sıradaki kontroller (372, 373)
   `Check 2`'den sonra girer; ve bir parçanın neden kendi girdisiyle düşürüldüğü *(aşağıda, karar 2)*.
3. Kod yok: araçlar, `build_prompts` ve yapı dosyası değişmez.

## Metin

```
Check 2 -- visible parts
- Read the camera angle in each frame's action. A frame fails when its prompt names a part of
  somebody that the angle hides, such as a face seen from behind: the model draws it anyway, or
  gives it to somebody else.
- Write a second entry of only what shows, with add_character or add_outfit, named for it: man body
  no face, dress from behind. Use it if it is already there.
- Give update_frame the frame's cast with those entries in place of the whole ones, and without
  anybody the angle does not show. The whole entries stay as they are: other frames show them whole.
```

## Kararlar

1. **Açı aksiyondan okunur.** Ayrı kamera alanı yok; açıyı aksiyon satırını yazan model yazıyor
   (`WRITE_FRAME_SYSTEM_PROMPT`). Kontrol aksiyona dokunmaz — açı doğru kabul edilir, düzeltilen
   kadrodur. Bu yüzden aksiyon boşaltılmaz (Check 1'in aksine), ve önsözün `build_prompts`'u değişen
   karenin fotoğraf prompt'unu yeniden yazar.
2. **Görünürlük başına ayrı girdi.** Bir kare kadrosunu isimle tutar, ve `build_prompts` her ismin
   girdisini bütün olarak koyar; "bu karede yalnız şu parçalar" diyecek bir alan yok. En basit araç
   düzeyi yol satırın örnekleri: görünen kısmın kendi girdisi (`add_character` / `add_outfit`) ve
   karenin kadrosunu ona çeviren `update_frame`. Yeni alan ya da yeni araç yok *(FOUNDATION 3 ve 5:
   girdiyi kod birleştirir, ve kullanıcı diskte okuyup düzeltebilir)*.
3. **Asıl girdi değişmez**: öteki kareler aynı kişiyi bütün gösteriyor, ve girdiye yapılan bir değişiklik
   onu adlandıran her kareye ulaşır.
4. **Girdi zaten varsa kullanılır**: aynı açı birkaç karede tekrar eder; `add_` araçları alınmış adı
   reddettiği için model bunu zaten öğrenirdi, ama bir cümle bir turu kurtarır.
5. **Açıdan hiç görünmeyen kişi kadrodan çıkar** — görünen parçası yoksa prompt'a giren bir şeyi de yok.
6. **Neden cümlesi modele söylenir** *(sahibin sözü: zayıf model görünmeyen özelliği öteki karakterlere
   ekliyor)*: model neden bir girdi daha yazdığını bilir.
7. **Kelimeler**: blok 112 kelime. Akış 712 → 824 (tavan 1000), Improve 370 → 482 (tavan 700).
   372 ve 373'e akışta 176 kelime kalır; blok bunun için kısa tutuldu.
8. **Kaçınılan kelimeler** *(öteki testler)*: `pov`, `shot`, `framing`, `video`, `h3`, `taken off`,
   `speak`; alt çizgili her kelime var olan bir araç.
