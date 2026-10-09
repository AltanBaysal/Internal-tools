# Madde 372 (v9-8d) — Kontrol: zayıf model bunu çizebilir mi — uygulama

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 372 · v9-8d.
**Testler:** [testler spec'i](2026-09-29-queenagent-m372-cizilebilir-mi-testler-design.md), kırmızı
commit `2486b0a1`. Bu spec yalnız o testlerin istediğini yazar.

**Kullanıcıdan gereken:** yok.

## Parçalar

1. **`prompt.py` — `THE_CHECKS`**: `Check 2`'nin son satırı ile kapanış cümlesi arasına, bir boş satırla
   ayrılmış `Check 3 -- can it be drawn` bloğu. Start a scenario'nun 6. adımı ve Improve'un 2. adımı onu
   `THE_CHECKS` üstünden kendiliğinden taşır.
2. **`prompt.py` — `THE_CHECKS`'in docstring'i**: bugünü söyler — sıradaki kontrol (373) `Check 3`'ten
   sonra girer; ve Check 3'ün neden bitmiş dosyayı okuyup parçayı geldiği yerde düzelttiği *(aşağıda,
   karar 1–3)*.
3. Kod yok: araçlar, `build_prompts` ve yapı dosyası değişmez.

## Metin

```
Check 3 -- can it be drawn
- Read each photo prompt in the file build_prompts wrote, in its final form. A frame fails when it
  asks for more than the model can draw: a hard pose, too many things, or what no picture shows.
- Simplify that part where it comes from, and keep the moment: the action with update_frame, an
  entry with update_character, update_outfit or update_location, which reaches every frame naming it.
```

## Kararlar

1. **Bitmiş dosya okunur, yapı dosyası değil.** Satır *"son hâldeki prompt'a bakar"* diyor; zayıf modelin
   eline geçen, `build_prompts`'un birleştirdiği fotoğraf prompt'u — girdiler ve aksiyon yan yana. Yapı
   dosyasında bir karenin prompt'u parça parça duruyor, ve fazla karmaşıklık çoğu zaman parçaların
   toplamında görünür. Önsöz her kontrolden sonra `build_prompts`'u çağırttığı için dosya Check 1 ve 2'den
   sonra günceldir; bir kez okunan dosya açılan dosyalar kutusunda diskten her tur yeniden okunur
   (`SYSTEM_PROMPT`), yani Check 3'ün kendi düzeltmesinden sonra da güncel kalır.
2. **Parça geldiği yerde düzeltilir** *(`build_prompts.py`)*. Bir fotoğraf prompt'u: kodun kalite zinciri,
   her kişinin karakter ve kıyafet girdileri, karenin aksiyonu, mekânın girdisi. Prompt dosyası elle
   yamanmaz (`EDIT_PROMPTS`: *rebuilt rather than patched*). Aksiyon karenin kendisinin: `update_frame`
   ile ajan kendi yazar — satırı okuyan ve neyin çizilemediğini bilen odur *(Madde 201/208)*; Check 1'deki
   gibi boşaltıp `write_missing_actions`'a bırakmak, satırı okumamış bir modele aynı karmaşık sahneyi
   yeniden verir. Karakter, kıyafet ve mekân birer girdi: çizilemeyen bir kıyafet her karede çizilemez,
   bu yüzden girdi düzeltilir ve değişiklik onu adlandıran her kareye ulaşır — cümle bunu modele söyler.
3. **"Keep the moment."** Sadeleştirme karenin anlattığı anı silmemeli; tek cümle, dört kelime.
4. **Örnekler kısa:** zor bir poz, çok fazla şey, hiçbir resmin gösteremediği şey. Zayıf modelin bilinen
   üç başarısızlığı; uzun bir liste 373'ün yerini yer.
5. **Zayıf model yeniden söylenmez** — `THE_IMAGE_MODEL` söylüyor; blokta "the model" onu işaret eder.
6. **Kelimeler:** blok 74 kelime. Akış 824 → 898 (tavan 1000), Improve 482 → 556 (tavan 700). 373'e
   akışta 102 kelime kalır.
7. **Kaçınılan kelimeler** *(öteki testler)*: `pov`, `shot`, `framing`, `video`, `h3`, `weak`, `taken
   off`, `speak`, `one at a time`; alt çizgili her kelime var olan bir araç.
