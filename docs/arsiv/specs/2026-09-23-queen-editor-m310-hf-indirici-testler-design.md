# Madde 310 — HF'deki modeller HF'nin kendi indiricisiyle, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok. Dosyalar herkese açık repolarda; deneme koşunun sonunda, Colab'da
*(kullanıcı, 23 Eylül — "sen kodun bitince test ederim çalışıyor mu diye")*.

## Bu tur ikinci kez yazıldı

İlk hâli `bdc683be` ile kırmızı commit'lendi: indirme kodu defterde kalıyordu ve testler hücrelerin
**metnine** bakıyordu. Uygulama turunda defter **30.278** karakter oldu — tavan 29.000 *(madde 239)*.
Kullanıcı üç yol arasından **kodu defterden çıkarmayı** seçti *(23 Eylül — "iş büyüsün sıkıntı
yok")*: indirme kodu repoda bir modüle taşınıyor, defter onu klondan import ediyor, ve kod metin
okunarak değil **koşularak** sınanıyor.

## Bugün ne oluyor

Defterin indirme hücresi HF dosyalarını **adresleriyle** tutuyor ve iki yoldan indiriyor: H3'ün dört
dosyası `curl` ile **tek bağlantıda**, fotoğrafın ikisi, WAN'ın beşi ve sesin biri `aria2c` ile. Tek
bağlantının sebebi yazılı: Xet'in imzalı adresleri paralel parçalı isteğe 403 veriyor
*([NOTEBOOK-STANDARD § 3](../../../collab-toolbox/NOTEBOOK-STANDARD.md))*. İki yol da HF'nin
**köprüsünden** geçiyor, ve köprü düz indirmeyi çoğu zaman **8,7 MB/s**'de kesiyor
*([xet-core #821](https://github.com/huggingface/xet-core/issues/821))*. Konsol her dosya için
"iniyor" ve "indirildi" diyor; süreyi ve hızı söylemiyor.

İndirme kodu defterin hücrelerinde: yardımcılar hücresinde `log`, `run`, `human`, `head_text`,
`check_safetensors`; modeller hücresinde `check_binary`, `strip_unreferenced_tail`, `fetch` ve
Civitai'nin üç fonksiyonu. Hiçbiri koşularak sınanmıyor — hücre pytest'te çalışmıyor.

## Kural

**HF'deki her dosya repo adı ve repodaki yoluyla anılıyor, ve HF'nin kendi indiricisiyle iniyor** —
`huggingface_hub.hf_hub_download`, arkasında `hf_xet`. Bu yol köprüden geçmiyor: dosyanın Xet
parçalarını depodan **paralel** çekiyor, bağlantı sayısını kendisi ayarlıyor. Paralellik dosyanın
içinde; dosyalar sırayla iniyor, konsolda her satır tek bir dosyayı anlatıyor.

**Doğrulama aynı kalıyor:** safetensors'ın sahipsiz kuyruğu kesiliyor, sonra dosya yargılanıyor. H3
için şart: HF'den gelen int4 metin kodlayıcı damgalı iniyor.

**Konsol her indirilen dosya için bir satır basıyor:** nereden geldiğini *(`HF`, ya da adresin
sunucusu)*, süresini ve hızını *(MB/s)* *(kullanıcı, 23 Eylül — "ama lütfen console basılsın tamam
mı?")*. Hız **bu koşuda inen baytlardan**: yarım kalmış bir indirmeden devam edilirse önceki baytlar
sayılmıyor.

**Kod defterden çıkıyor.** `queen-editor/colab/` defterin kendi kodu: `console.py` *(`log`, `run`,
`human`, `head_text`)* ve `downloads.py` *(doğrulama, `fetch`, `hf_fetch`, Civitai'nin fonksiyonları)*.
Defter yardımcılar hücresinde klonu yola koyup ikisinden import ediyor. **Listeler ve adresler
defterde kalıyor** — adreslerin yeri defter *([FOUNDATION 9](../../../queen-editor/FOUNDATION.md))*.

**Kapsam dışı:** SAM *(`dl.fbaipublicfiles.com`, HF değil; `aria2c`'de kalıyor)*, Civitai dosyaları
*(311)*, MMAudio kütüphanesinin kendi ağırlıkları *(adresleri kütüphanenin içinde; repo onları hep
adressiz tuttu, `url: None`)*.

## Yazılacak testler

### `test_colab_downloads.py` — yeni, modül koşularak

Ağ sahte: `huggingface_hub` `sys.modules`'a sahte bir modülle konuyor, `curl`/`aria2c` de `run`'ın
yerine geçen bir sahteyle. Dosyalar gerçek — küçük, geçerli bir safetensors test içinde yazılıyor.

1. **HF dosyası HF'nin kendi indiricisiyle iniyor** — `hf_hub_download` repo ve yolla, ara klasöre
   çağrılıyor; dosya hedefine, **hedefteki adıyla** konuyor.
2. **HF dosyasının damgası yargılanmadan kesiliyor** — damgalı inen dosya hedefte temiz duruyor.
3. **HF indirmesi kaynağını ve hızını basıyor** — satırda `HF` ve `MB/s`.
4. **Yerinde duran dosya yeniden inmiyor** — indirici hiç çağrılmıyor, konsol "zaten var" diyor.
5. **HF'nin hatası kendi sözüyle çıkıyor** — indiricinin hatası etiketle birlikte `RuntimeError`'da.
6. **Bozuk inen dosya koşuyu durduruyor ve silinmiyor** — hedefe konmuyor, ara klasörde kalıyor
   *(NOTEBOOK-STANDARD § 3)*.
7. **Tabanı olan dosya boyuyla yargılanıyor, safetensors diye değil** — `.pt` / `.pth` dosyaları.
8. **Adresle inen dosya sunucusunu ve hızını basıyor** — satırda `civitai.red` ve `MB/s`.
9. **Adresle inen dosyanın da damgası kesiliyor.**
10. **Yarım kalandan devam eden indirme yalnız bu koşuda ineni sayıyor.**
11. **Kapılı dosya `curl` ile iniyor, çerez geride kalıyor** — Civitai dosyayı deposuna yönlendiriyor
    ve depo çerezle gelen isteğe 403 veriyor; `aria2c` çerezi taşıyor, `curl` sunucu değişince
    bırakıyor.
12. **Civitai `civitai.red` üstünden soruluyor** — çerez orada aynı köken.

### `test_notebook_installs_the_producer_groups.py` — defterle kodun dikişi

13. **`test_no_huggingface_file_is_fetched_by_its_address`** — `bdc683be`'den, olduğu gibi.
14. **`test_an_unticked_group_costs_no_bytes`** — `bdc683be`'deki güncel tablosuyla.
15. **Defterin import ettiği her ad modülde var** — import satırları okunuyor, modül gerçekten import
    ediliyor. Colab'da `ImportError` olacak şey burada kırmızı oluyor.
16. **Defter kodu klondan buluyor** — yardımcılar hücresi klonu yola import'tan **önce** koyuyor.
17. **Yeniden koşu, yeni klonlanan kodu import ediyor** — klon hücresi her koşuda repoyu silip yeniden
    klonluyor, ama Python import ettiği modülü çekirdek yaşadıkça tutuyor; hücre onu bırakmazsa yeni
    kodu klonlayıp eskisini koşar.
18. **Defter import ettiği kodu kendisi tanımlamıyor** — bir hücrede kalan kopya test edilenin
    üstüne biner.
19. **HF dosyaları `hf_fetch` ile iniyor, ve defter `hf_xet`'i kuruyor.**
20. **Kapılı dosyalar her şeyden önce yoklanıyor** — modeller hücresinde `civitai_probe` ilk
    indirmeden önce.

**Silinen testler, ve yerlerini alanlar:**

| Silinen | Yerini alan |
|---|---|
| `test_the_gated_files_are_fetched_the_way_that_works` | 11, 12, 20 |
| `test_the_quantizer_stamp_is_cut_before_a_file_is_judged` | 2, 9 |
| `test_huggingface_files_come_down_through_hugging_face_s_own_downloader` *(metin)* | 1, 19 |
| `test_the_quantizer_stamp_is_cut_before_a_huggingface_file_is_judged` *(metin)* | 2 |
| `test_every_download_prints_where_it_came_from_and_how_fast` *(metin)* | 3, 8 |

**Bekçiler, bugün de yeşil:** her dosyanın adı defterde *(panelin grubu, H3'ün grubu)*, defterin
boyut tavanı.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest kırmızı — 1–20'nin hepsi *(13 ve 14 `bdc683be`'den
beri kırmızı)*. Başka hiçbir test kıpırdamıyor; bekçiler yeşil.
