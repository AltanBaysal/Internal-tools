# Madde 312 — Yüksek hız ayarı, indirme özeti ve hücre süreleri, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Ayar makinenin RAM'ine bakmadan her koşuda açık *(kullanıcı — "200 GB
RAM'li cihaz, yine açarız, sıkıntı yok")*; karşılaştırma koşusu kullanıcının, iş bittikten sonra.

## Bugün ne oluyor

`hf_fetch` HF'nin indiricisini `hf_xet`'in varsayılan ayarıyla çağırıyor. Her indirme kendi satırını
basıyor — kaynak, boyut, süre, hız — ama satırlar ilerleme çubuklarının arasında dağınık, toplam süre
hiçbir yerde yazmıyor, ve hiçbir hücre ne kadar sürdüğünü söylemiyor. İndirme fonksiyonları hiçbir
şey döndürmüyor.

## Kural

**(1) HF'nin indiricisi yüksek hız ayarıyla alınıyor.** `HF_XET_HIGH_PERFORMANCE=1`: HF'nin tarifiyle
`hf_xet` makinenin bağlantısını doldurmaya ve bütün çekirdekleri kullanmaya çalışıyor. HF'nin
belgesine göre `huggingface_hub` değişkenlerini **import edildiği an** bir kez okuyor — ayar, indirici
kütüphaneden alındığı anda açık olmalı, ortamda önceden ne yazarsa yazsın.

**(2) Her indirme özet için kendi satırını geri veriyor**: `(etiket, bu koşuda inen bayt, saniye)`.
`hf_fetch`, `fetch` ve `civitai_fetch` aynı şeyi döndürüyor; yerinde duran dosya `None` döndürüyor,
çünkü inmedi. `civitai_fetch` hangi yoldan indiyse — aynadan ya da Civitai'den — onun satırını
veriyor; Civitai'den inişin ardından gelen yükleme satıra girmiyor.

**(3) Modeller hücresi indirme özetiyle bitiyor** — `download_summary(satırlar)`: bu koşuda inen her
dosya boyutu, süresi (`1 dk 40 sn`) ve hızıyla alt alta, en altta **Toplam**: boyutların toplamı,
sürelerin toplamı, ortalama hız. Hiçbir şey inmediyse tek satır: bu koşuda inen dosya yok. Hücre
satırları döngülerde `landed` listesine topluyor ve tabloyu en sonda basıyor.

**(4) Her kod hücresi kendi süresiyle bitiyor** — `⏱️ Hücre 1 dk 50 sn sürdü`. IPython her hücrenin
başında ve sonunda birer kanca çağırıyor; sayaç ikisini kaydediyor. **Sayaç CONFIG'in en başında,
`# === Cell timer ===` başlığıyla** — ilk kod hücresi, çünkü Drive ve klon hücrelerinin süresi de
isteniyor ve `colab/` klondan önce yok. Bölüm yalnız `time` ve IPython'u kullanıyor; test onu
başlığından bir sonraki başlığa kadar kesip tek başına çalıştırıyor. CONFIG yeniden çalışınca eski
kancalar sökülüp yenileri takılıyor — hücre başına bir satır.

**(5) Link satırı hücrenin o ana kadarki süresini söylüyor.** Son hücre hiç bitmiyor — canlı log
akıyor — o yüzden süresi linkin hemen üstünde: `Link 14 sn'de hazır`. Sayaç bunu `cell_elapsed()` ile
veriyor: hücre başladığından beri geçen süre, satırdaki biçimle.

## Yazılacak testler

### `test_colab_downloads.py` — koşularak

1. **İndirici yüksek hız ayarıyla alınıyor** — ortamda `HF_XET_HIGH_PERFORMANCE=0` varken bile,
   `hf_hub_download` kütüphaneden alındığı an değişken `1`.
2. **İnen dosya kendi satırını veriyor** — `hf_fetch` → etiket, dosyanın baytı, sıfırdan büyük süre.
3. **Yerinde duran dosya tabloya girmiyor** — biri yerinde biri inen iki `hf_fetch` ve yerinde duran
   bir `fetch`: tabloda yalnız inen var.
4. **Devam eden indirmenin satırı yalnız bu koşuda ineni sayıyor** — 100 baytlık `.part`'a 900 bayt
   eklenince satır 900.
5. **Civitai dosyası hangi yoldan indiyse onun satırını veriyor** — aynadan inen de, Civitai'den inip
   aynaya yüklenen de.
6. **Özet her inişi ve toplamı yazıyor** — `60.0MB, 20 sn, 3.0 MB/s` ve `2.0GB, 1 dk 40 sn,
   20.5 MB/s`, sırayla; altında `Toplam 2.1GB, 2 dk 0 sn, 17.6 MB/s`; başlık `İndirme özeti`.
7. **Hiçbir şey inmediyse özet bunu söylüyor** — `inen dosya yok`, `Toplam` yok.

### `test_notebook_installs_the_producer_groups.py` — defter, okunarak

8. **HF dosyaları `hf_fetch` ile iniyor ve satırları tutuluyor** — `hf_jobs` döngüsü
   `landed.append(hf_fetch(`.
9. **Civitai dosyaları aynadan geçiyor ve satırları tutuluyor** — `civitai_jobs` döngüsü
   `landed.append(civitai_fetch(HF_MIRROR, `.
10. **Modeller hücresi indirme özetiyle bitiyor** — `landed = []` döngülerden önce, açık adresli
    döngü de satırını tutuyor, `download_summary(landed)` Civitai döngüsünden sonra, ve ad
    `colab.downloads`'tan import ediliyor.

### `test_notebook_times_its_cells.py` — yeni; sayaç çalıştırılarak, gerisi okunarak

Sayaç, bu takımın çalıştırdığı tek defter kodu: klondan önce açık olması gerektiği için `colab/`'da
duramıyor. IPython'un olay yöneticisi ve saat sahte.

11. **Her hücre süresiyle bitiyor** — 110,4 sn süren hücre `Hücre 1 dk 50 sn sürdü`, 8,2 sn süren
    `Hücre 8 sn sürdü`; ikisi de `⏱` ile başlıyor.
12. **CONFIG yeniden çalışınca tek sayaç kalıyor** — bölüm iki kez çalışınca hücre başına bir satır.
13. **Sayaç defterin ilk çalıştırdığı şey** — ilk kod hücresi `# === Cell timer ===` ile başlıyor.
14. **Hücre o ana kadarki süresini sorabiliyor** — başlayalı 14,3 sn olan hücrede `cell_elapsed()`
    `14 sn`.
15. **Link satırı hücrenin süresini linkin üstünde söylüyor** — Flask hücresinde `cell_elapsed()`
    ile `hazır` aynı satırda, `🔗 Queen Editor`'dan önce.

**Değişen:**

| Test | Ne oluyor |
|---|---|
| `test_huggingface_files_come_down_through_hf_fetch` | döngü satırı `landed.append(hf_fetch(` — 8 |
| `test_civitai_files_come_down_through_the_mirror` | döngü satırı `landed.append(civitai_fetch(HF_MIRROR, ` — 9 |

**Bekçiler, bugün de yeşil:** 310 ve 311'in indirme testleri — satırlar ve dönüşler konsol satırlarını
değiştirmiyor; `test_every_name_the_notebook_imports_from_its_code_exists` — defter
`download_summary`'yi import etmeye başlayınca o adı da o tutar;
`test_the_notebook_defines_none_of_the_code_it_imports`; ve `test_notebook_stays_readable.py` —
sayaç defterde duruyor, tavan 29.000 karakter.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest kırmızı — yalnız 1–15.
