# Madde 311 — HF aynası, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m311 test turu](2026-09-23-queen-editor-m311-hf-aynasi-testler-design.md),
`c20ea6d2` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok — ayna ve token hazır.

## `colab/downloads.py`

**`civitai_fetch(mirror, version_id, target_dir, filename, label, cookie)`**, dört adım:

1. **Ayna:** `hf_fetch(mirror, f"{version_id}/{filename}", …)`. İnerse — ya da dosya zaten
   yerindeyse — iş bitti.
2. **Düşüş:** `hf_fetch`'in `RuntimeError`'ı olduğu gibi konsola basılıyor *(uyarı olarak)*. Bu
   yol hem "dosya aynada yok"u hem "inerken bozuldu"yu taşıyor, çünkü ikisi de aynı cümleyle
   çıkıyor: HF'nin kendi cümlesi.
3. **Çerez ve yoklama:** çerez yoksa ya da 200 karakterden kısaysa `RuntimeError`, dosyayı ve
   çerezin nereden alınacağını söyleyerek — CONFIG'deki eski cümle buraya taşınıyor. Sonra
   `civitai_probe`, sonra `fetch` — bugünkü gibi `curl`, çerezle.
4. **Yükleme:** `HfApi().upload_file` ile aynaya, `<sürüm>/<ad>` yoluna. Başarısı bir satır *(boyut,
   süre, hız)*; reddi bir uyarı, HF'nin cümlesiyle, ve koşu sürüyor.

`huggingface_hub` yine fonksiyonun içinde import ediliyor. Token'ı `huggingface_hub` Colab
Secrets'tan kendisi okuyor; kodda token yok.

**Aynadaki bozuk kopya kendini onarıyor:** `hf_fetch` bozuk dosyayı reddedince düşüş Civitai'den
indiriyor ve yükleme aynadaki kopyanın üstüne yazıyor.

## Defter

- **CONFIG:** `HF_MIRROR = "Test468735/queen-editor-models"`, `DRIVE_FOLDER`'ın altında. Çerez
  assert'i gidiyor; çerez okunmaya devam ediyor. Özet satırlarına aynanın adı ekleniyor.
- **Yardımcılar:** import satırı `fetch, hf_fetch, civitai_fetch` — defter Civitai'nin öteki
  fonksiyonlarını artık kendisi çağırmıyor.
- **Modeller:** `# === Gated probe ===` bölümü gidiyor — yoklama her düşüşün önünde. Civitai
  döngüsü `civitai_fetch(HF_MIRROR, vid, d, fn, label, COOKIE_VALUE)`.
- **Giriş hücresi:** Secrets satırı `HF_TOKEN`'ı adlandırıyor, ve çerezin yalnız aynada olmayan
  dosya için gerektiğini söylüyor.

## README

Secrets tablosuna `HF_TOKEN` satırı *(fine-grained, yalnız o repo, okuma ve yazma)*; `CIVITAI_COOKIE`
satırı yalnız aynada olmayan dosya için gerektiğini söylüyor.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil.
