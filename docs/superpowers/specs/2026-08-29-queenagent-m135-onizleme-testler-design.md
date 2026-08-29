# Madde 135 · Tur 1 (test) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 135
**Dal:** `feat/queenagent-m123-skill-rewrite`.

## Sorun

Sekizinci denemede `build_character_prompts`'un hemen ardından bir `read_file` geldi. **Suç
modelin değil:** aracın cevabı *"Wrote 1 prompts to ...-lara.py."* diyor ve kurduğu promptu
taşımıyor. Model önizlemeyi kullanıcıya göstermek zorunda, ve gösterilecek şey cevapta olmayınca
dosyayı okumaktan başka yolu yok.

Madde 98 bu aracı **bir bakış** diye tanımladı — *"kullanıcı bir karakteri sahneye girmeden görmek
istiyor"*. Bakılacak şeyi döndürmeyen bir bakış, her seferinde fazladan bir raunt demek.

Cümlede bir de sayı hatası var: `len(prompts)` ham basılıyor, yani tek promptta *"1 prompts"*
yazıyor. `counted()` tam bunun için var ve `outcome` onu zaten kullanıyor.

## Yol

Araç kurduğu promptları cevabında verir. Dosya yine yazılıyor — kart yine çıkıyor, kullanıcı yine
projede buluyor — değişen yalnız modelin onları görmek için okumak zorunda olmaması.

## Kurallar

- **`build_prompts` bunu almaz.** Madde 130 promptların geri basılmamasını söylüyor, ve 25 promptu
  cevaba koymak tam da onu davet ederdi. Ayrım işin kendisinde: **önizleme bakılmak için var,
  kurulan liste dosyada durmak için.** Bu bir istisna değil, iki farklı iş.
- **Boyut sınırı yok.** Bir karakterin kıyafet sayısı kadar prompt çıkıyor, ve o sayı senaryo
  yazarının elinde. Sınır koymak bakılamayan bir bakış üretirdi.
- **Kart ve dosya değişmiyor.** `written` yine dönüyor, `outcome` yine `counted`.
- **Tekil düzelir:** *"1 prompts"* → *"1 prompt"*, `counted()` ile.

## Bu turun testleri

`test_tools.py`:

- `test_a_character_preview_hands_back_the_prompts_it_built` — **kırmızı**
- `test_a_character_preview_counts_one_prompt_as_one` — **kırmızı**
- `test_the_scene_builder_still_does_not_hand_back_its_prompts` — bekçi, ve maddenin sınırı
- `test_a_character_preview_still_writes_its_file` — bekçi

## Ayakta kalması gerekenler

98'in aracı ve çıktı biçimi, 110'un kalite zinciri, 130'un kapanış kuralı, `_build`'ın üç reddi,
ve kartın dosyayı adıyla söylemesi.

## Bilerek yapılmayanlar

`build_prompts`'un cevabı. `_build`'ın kendi *"Wrote N prompts"* cümlesindeki aynı tekil hatası bu
maddenin kapsamı dışında — görüldü ve raporlandı, ve düzeltilmesi ayrı bir karar.
