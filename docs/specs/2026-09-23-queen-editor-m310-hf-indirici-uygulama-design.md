# Madde 310 — HF indiricisi, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m310 test turu](2026-09-23-queen-editor-m310-hf-indirici-testler-design.md),
`2944861c` ile kırmızı commit'lendi *(ilk hâli `bdc683be`)*.

**Kullanıcıdan gereken:** yok.

## `queen-editor/colab/` — defterin kendi kodu

Üç dosya: boş bir `__init__.py`, `console.py`, `downloads.py`.

**`console.py`** — her hücrenin konuştuğu ve kabuk çağırdığı dört fonksiyon: `log`, `human`,
`head_text`, `run`. Defterin yardımcılar hücresinden **olduğu gibi** taşınıyor.

**`downloads.py`** — indirme ve doğrulama:

- `check_safetensors`, `check_binary`, `strip_unreferenced_tail` — defterden olduğu gibi.
- **Tek bir yargı:** tabanı olan dosya *(`.pth`, `.pt`)* boyuyla ve ilk baytlarıyla, safetensors
  kuyruğu kesilip başlığıyla. Defterde bu, iki ayrı yerde bir lambda ve bir iç fonksiyondu; artık
  `fetch` ile `hf_fetch` aynı yargıyı çağırıyor, ve çağıran lambda değil **`floor=`** veriyor.
- **`fetch(url, target_dir, filename, label, *, parallel, headers=None, floor=None)`** — defterdeki
  `fetch`, bir değişiklikle: başarı satırı **sunucuyu, bu koşuda inen baytı, süreyi ve hızı**
  basıyor. `.part`'tan devam edilirse önceki baytlar sayılmıyor.
- **`hf_fetch(repo, path, target_dir, filename, label, *, floor=None)`** — yeni.
  `huggingface_hub.hf_hub_download` dosyayı `STAGE` *(`/content/hf_stage`)* altına indiriyor, dosya
  yargılanıyor, ve hedefine **hedefteki adıyla** `os.replace` ile taşınıyor. Ara klasörün sebebi:
  indirici `local_dir`'e repodaki yolu ve kendi `.cache`'ini yazıyor, ikisi de ComfyUI'nin model
  klasörlerine girmesin; aynı diskte taşımak kopya değil. Hedefte dosya varsa yargılanıp geçiliyor.
  İndirici hata verirse `RuntimeError` etiketle ve HF'nin kendi cümlesiyle. `huggingface_hub`
  fonksiyonun içinde import ediliyor: Colab'da kurulu geliyor, bu makinede şart değil.
- `civitai_url`, `cookie_header(cookie)`, `civitai_probe(version_id, label, cookie)` — defterden;
  çerez artık defterin global'inden okunmuyor, argüman olarak geliyor.

Bozuk dosya her yolda aynı: `RuntimeError`, başını gösteren bir mesaj, ve **silinmiyor**
*(NOTEBOOK-STANDARD § 3)*. Süre `time.perf_counter()` ile — Windows'ta `time.time()`'ın adımı
milisaniyeleri yutuyor, ve hız ona bölünüyor.

**Paralellik `hf_xet`'in varsayılanı.** `HF_XET_HIGH_PERFORMANCE` açılmıyor: HF onu en az 64 GB
RAM'li makineler için yazıyor, Colab'ın T4'ü ~12 GB taşıyor. Hız her dosya için konsolda; düşük
çıkarsa ilk kaldıraç bu ayarlar, ölçüyle.

## Defter

- **Sistem hücresi** — sonuna kendi başlığıyla `!pip install -q -U hf_xet`. Custom node'ların
  gereksinimlerinden sonra, yani ardından kurulan hiçbir şey onu değiştirmiyor. `huggingface_hub`'a
  dokunulmuyor: Colab'ın sürümü başka paketlerin sabitlediği sürüm olabilir, ve `hf_xet` için 0.30
  üstü yetiyor.
- **Yardımcılar hücresi** — tanımlar gidiyor, yerine: önceki koşunun `colab` modülleri
  `sys.modules`'tan düşürülüyor, klon yola konuyor, iki import satırı. Klon hücresi her koşuda repoyu
  silip yeniden klonluyor; modül düşürülmezse yeni kodu klonlayıp eskisini koşar.
- **Modeller hücresi** — tanımlar gidiyor, listeler kalıyor. HF listeleri `HF_PHOTO`, `HF_VIDEO`,
  `HF_H3`, `HF_AUDIO`: satır `(repo, yol, klasör, dosya adı, etiket, taban)`. `OPEN_PHOTO`'da yalnız
  SAM. `HF` sabiti gidiyor, `WAN22`/`WAN21` repo adına dönüyor. Sıra: yoklama, HF, adresle inenler,
  Civitai.

Kod hücrelerinde yorum yok, yalnız bölüm başlıkları *(madde 239)*.

## Belge — CODE-STANDARD

- **Yeni bölüm, `colab/`**: defterin kendi kodu. Defter onu klondan import ediyor; uygulama onu
  hiç import etmiyor ve o uygulamadan hiçbir şey import etmiyor *(FOUNDATION 9: uygulama
  indirmez)*. Neden hücre değil modül: hücre pytest'te koşmuyor, ve defterin boyut tavanı var.
- **"Setup cells … copied verbatim" satırı**: model indirmeleri artık `colab/`'da, kendi testleriyle;
  custom node'lar ve ComfyUI hücreleri hâlâ kopya.
- **Tests bölümü**: `colab/` ağı sahteleyerek koşuyor, dosyalar gerçek.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil.
