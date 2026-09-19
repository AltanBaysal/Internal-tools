# Madde 238 · LoRA kutusu: USNR, Slime, Boş — uygulama turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** [test turu](2026-09-18-queen-editor-m238-lora-usnr-slime-bos-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Tasarım

**Katalog** *(`domain/catalog.py`)*. Modeller LoRA taşımıyor. `LORAS` iki satır: önce USNR, sonra
Slime. USNR'nin tetiği yok. `DEFAULT_LORA` listenin ilk satırı; hem panelin doldurduğu satır hem
render'ın varsayılanı olduğu için tek bir yerden okunuyor. `NO_LORA` Boş'un değeri. `LEGACY`'de
Nova'ya düşen eski tarifler artık açıkça `usnr` diyor. Böylece varsayılan ileride değişse bile o
kareler üretildikleri gibi kalıyor.

**Liste** *(`list_models.py`)*. `list_loras` katalogdaki LoRA'ları veriyor, sonuna Boş'u ekliyor.

**Render** *(`comfy_photo_generator.py`)*. `_lora` değeri şöyle çözüyor:

- Boş değer varsayılan sayılıyor.
- `none` LoRA'sız demek.
- Başka bir değer katalogda aranıyor, bulunamazsa render duruyor *(bugünkü reddi)*.

Modeli olan bir karede yuvalar yalnız seçimle doluyor, Boş'ta boşalıyor. Modelsiz ve çıplak dosya
adlı kareler bugünkü gibi yükleyiciye dokunmuyor. Grafiğin kendi LoRA'sı USNR, yani varsayılanla
aynı.

**Kuyruk isteği** *(`start_batch.py`)*. Katalogda olmayan bir LoRA, plana bir şey yazılmadan
`InvalidLora` ile reddediliyor. Uç nokta bunu `field: "lora"` ile 400'e çeviriyor. Kurulum hâlâ
render'ın sorusu. Bu denetim uygulamanın kendi listesine bakıyor.

**Ayarlar** *(projects feature)*. Ayar dosyasının şekline `lora` giriyor: okuyan, yazan ve uç nokta.
Yanlış tipteki ya da eski dosyadaki LoRA boş okunuyor.

**Ön yüz:**

- `saveSettings` ve ProjectScreen LoRA'yı kaydediyor.
- `useModels` okunamayan bir cevapta iki listeyi de boş veriyor.
- GeneratePanel:
  - `Standart` yedeği gidiyor.
  - Kutu projenin kayıtlı LoRA'sıyla açılıyor. Boşsa sunucunun ilk satırıyla doluyor.
  - Listede artık olmayan bir kayıt kendi değeriyle seçili kalıyor, Model kutusunun kuralıyla ama notsuz. Geçerli olup olmadığını backend söylüyor.
  - Liste gelmeden kutu `yükleniyor…`, okunamayınca `liste okunamadı` diyor, iki durumda da kapalı.
- Kare detayı LoRA söylemeyen bir karede satırı çizmiyor.

**Defter.** Tek bir kod yorumu: USNR'yi *"Nova's standard"* diye anıyor. Artık her modelin
LoRA'sı olduğu için yorum bunu söyleyecek şekilde düzeltiliyor.

## Bu turda değişen

Uygulama, defterin bir yorumu ve derlenmiş `dist/`. Testlere dokunulmuyor.
