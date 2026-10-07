# Madde 241 · MiniMax defterine üç içerik LoRA'sı — uygulama turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** yok *(kullanıcı kararı — sebebi maddede)*

## Kullanıcıdan gereken

Hiçbir şey. Linkleri verdi, sürümleri seçti, `CIVITAI_COOKIE` güncel. Colab'daki deneme 213'ün
keşfinin parçası ve kullanıcının.

## Tasarım

**Hangi dosyalar.** Kullanıcının verdiği sayfaların en yeni sürümleri; Civitai'nin birincil dosyası,
Civitai'nin kendi adıyla:

| Sürüm | Dosya |
|---|---|
| Mystic XXX v4.0 · 3266628 | `MysticXXX_MMH3-V4.safetensors` |
| Motion Booster V0.2 · 3228867 | `H3_Motion_BoosterV2.safetensors` |
| VBVR Pro · 3306139 | `H3_VBVR_Pro_attn_only.safetensors` |

Grafik bu LoRA'ları adlandırmıyor: `DaSiWa_LTX2LoraLoader`'ın on yuvası boş geliyor ve kullanıcı
UI'da seçiyor. O yüzden dosyayı grafiğin istediği bir ada çevirmeye gerek yok. Turbo LoRA
*(3206543)* inmiyor.

**`manual.ipynb`, hücre 8 (Modeller):**
- Hedef klasörlere `models/loras/` eklenir.
- DaSiWa'nın hemen altına bir `CIVITAI_LORAS` listesi girer: `(sürüm, dosya, etiket)`, üç satır.
- Probe adımı DaSiWa'dan sonra üç LoRA'yı da yoklar; cookie ölmüşse 21 GB'a başlamadan durulur.
- İndirme adımı DaSiWa'dan sonra üçünü indirir: mevcut `fetch`, curl, cookie başlığı. Yeni bir
  indirme yolu yok.
- Sondaki özet `loras/` klasörünü de listeler.

**Hücre 0, 2 ve 7:** toplam **~40,1 GB** olur. Hücre 7'nin tablosuna `loras/` satırı girer, ve
LoRA'ları grafiğin adlandırmadığını söyleyen bir cümle.

**`indirilecekler.md` § 7:** tablo seçilen sürümlere geçer. Sayfalarda yazanlar LoRA başına kısa
maddeler olarak girer: tetik kelime, önerilen ağırlık, prompt'un nasıl yazılacağı, uyarılar.
Kaynakları: kullanıcının yapıştırdığı sayfa metinleri ve Civitai API'si.

**`instructions.md`:** runtime değişince yeniden inen boyut 39,7 → 40,1 GB.

## Doğrulama

Test yok. Diff okunur: hücre 8'de yalnız LoRA satırları eklenmiş, var olan satırlar aynı. Asıl
doğrulama Colab'da: hücre 4'ün özeti `loras/` altında üç dosyayı listeler, ve LoRA yığınının
listesinde üçü de görünür — 213'ün denemesinde kullanıcı görür.

## Bu turda değişen

`collab-toolbox/video_experiments/minimax-h3/`: `manual.ipynb`, `indirilecekler.md`,
`instructions.md`. Ve yol haritasında 241'in işareti.
