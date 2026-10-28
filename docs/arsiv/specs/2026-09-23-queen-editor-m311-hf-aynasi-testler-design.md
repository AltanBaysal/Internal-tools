# Madde 311 — Civitai'deki modeller önce kullanıcının HF reposunda, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — hazır** *(23 Eylül)*: HF hesabı *(`Test468735`)*, private repo
*(`Test468735/queen-editor-models`)*, ve yalnız o repoya okuma ve yazma izni olan fine-grained bir
token, Colab Secrets'ta `HF_TOKEN` adıyla *(kullanıcı — "ekledim")*. `huggingface_hub` Colab'da
bu adı kendiliğinden okuyor.

## Bugün ne oluyor

310'dan sonra Civitai dosyaları *(fotoğraf, WAN, H3 — hepsi ~66 GB)* hâlâ adresle, `curl` ile ve
tek bağlantıda iniyor; en büyüğü H3'ün 21 GB'lık checkpoint'i. CONFIG, fotoğraf ya da video
seçildiyse çerezi **baştan** istiyor, ve modeller hücresi her Civitai dosyasını indirmelerden önce
1 KB'lık bir istekle yokluyor.

## Kural

**Her Civitai dosyası önce kullanıcının HF reposunda — aynada — aranıyor.** Aynadaki yolu
`<Civitai sürüm no>/<dosya adı>`: hangi Civitai sürümünden geldiği yolundan okunuyor, ve iki dosya
aynı adı taşısa bile çakışmıyor. Aynada varsa `hf_fetch` ile, 310'daki gibi paralel iniyor.

**Aynadan alınamazsa** — dosya yoksa ya da inerken hata verirse — konsol HF'nin kendi cümlesini
basıyor, ve dosya bugünkü gibi Civitai'den iniyor *(kullanıcı — "yoksa console'a bassın ve asıl
nasıl indiriyorsa öyle indirsin")*. Civitai'den inmeden önce çerez var mı bakılıyor ve dosya
yoklanıyor. **Sonra aynı koşuda aynaya yükleniyor** *(kullanıcı — "1")*: bir dosyanın yalnız ilk
inişi yavaş.

**Yükleme başarısız olursa** konsol HF'nin cümlesini basıyor ve koşu sürüyor: dosya zaten indi,
kullanılabilir; aynaya sonraki koşu yeniden dener. Yüklemenin başarısı da bir satır — boyut, süre,
hız.

**Çerez yalnız Civitai'ye düşen dosya için isteniyor.** CONFIG artık çerezi baştan istemiyor; her
şey aynadaysa defter çerezsiz açılıyor. Aynada olmayan bir dosya çerezsiz kalırsa koşu **Civitai'ye
hiç gitmeden** duruyor, ve cümle hangi dosya için neyin eksik olduğunu söylüyor.

**Ayna CONFIG'de, tek yerde adlanıyor** — `HF_MIRROR`. Adresler defterde *(FOUNDATION 9)*, ve bir
repoyu adlandırmak CONFIG'in işi, `DRIVE_FOLDER` gibi.

## Yazılacak testler

### `test_colab_downloads.py` — `civitai_fetch`, koşularak

Ağ sahte: `huggingface_hub` yerine tuttuğu dosyalarla bir ayna *(tutmadığı yola HF'nin cümlesiyle
cevap veriyor)* ve yüklemeleri kaydeden bir `HfApi`; `curl`, 310'daki sahteyle; yoklama da bir
sahteyle.

1. **Aynadaki dosya HF'den iniyor** — Civitai'ye hiç gidilmiyor, yükleme yok, ve **çerez
   gerekmiyor**.
2. **Aynada olmayan dosya Civitai'den iniyor ve sebebi konsolda** — HF'nin cümlesi basılıyor,
   dosya `curl` ile ve çerezle geliyor.
3. **Civitai'den inen dosya aynaya çıkıyor** — `<sürüm>/<ad>` yoluyla, doğru repoya; konsolda
   yüklendiği yazıyor.
4. **Yüklenemeyen dosya uyarıyla kalıyor** — hata yok, HF'nin cümlesi konsolda, dosya yerinde.
5. **Çerezsiz düşüş Civitai'ye gitmeden duruyor** — cümle çerezi ve dosyayı adlandırıyor; ne
   yoklama ne indirme.
6. **Düşüş inmeden önce yoklanıyor** — yoklama `curl`'den önce.

### `test_notebook_installs_the_producer_groups.py` — defter

7. **Civitai dosyaları aynadan geçerek iniyor** — modeller hücresinde `civitai_jobs` döngüsü
   `civitai_fetch(HF_MIRROR, …)` çağırıyor.
8. **Ayna CONFIG'de bir kez adlanıyor.**
9. **CONFIG çerezi baştan istemiyor.**

**Değişen ve silinen:**

| Test | Ne oluyor | Yerini alan |
|---|---|---|
| `test_the_cookie_is_only_demanded_by_the_groups_that_are_gated` | siliniyor — çerez artık CONFIG'de değil, düşüşte isteniyor | 5, 9 |
| `test_the_gated_files_are_probed_before_anything_comes_down` | siliniyor — yoklama her düşüşün önünde | 6 |

**Bekçiler, bugün de yeşil:** 310'un bütün testleri; aralarında
`test_every_name_the_notebook_imports_from_its_code_exists` — defter `civitai_fetch`'i import etmeye
başlayınca o adı da o tutar.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest kırmızı — yalnız 1–9.
