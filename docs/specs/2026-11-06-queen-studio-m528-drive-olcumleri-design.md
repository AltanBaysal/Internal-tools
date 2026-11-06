# Madde 528 · Drive'ın ölçümleri — tasarım

**Tarih:** 6 Kasım 2026 · **Madde:** [v1 yol haritası](../roadmaps/2026-11-06-queen-studio-v1-roadmap.md#v1-4),
528 · v1-4 · **Dal:** `feat/queen-studio-v1`

## Ne ve neden

[4. adımın](../research/2026-11-03-yeni-editor-v1-4-depo.md) depo tasarımı, Drive'ın belgede yazmayan
on bir davranışına dayanıyor ([Değerlendirme 14](../research/2026-11-03-yeni-editor-v1-4-depo.md#14-ölçülmemiş-varsayımlar)).
Depo maddeleri (v1-7'den v1-9'a) yazılmadan önce her biri ölçülür: bu makineden ve bir kez Colab'ın
ücretsiz katmanında, deneme hesabıyla. Dört Colab'ın hız sınırı yalnız bu makineden, dört süreçle
([kararlar, Koşudan önce 3](../roadmaps/2026-11-06-queen-studio-v1-kararlar.md#koşudan-önce-belgelerin-gözden-geçirilmesinde)).
Tutmayan varsayım düz söylenir, sayısıyla ve tasarımda neyi bozduğuyla; düzeltmeye ana agent karar
verir.

Ürün kodu yok. Betikler, ham çıktı ve sonuçların kaydı var.

## Nerede

```
queen-studio/measurements/
  drive.json                 sonuçlar: kodun ve testlerin sayılarını aldığı yer
  drive/
    common.py                istemci, nazik çağrı, istatistik, yazma
    consistency.py           1–4: okuma güncelliği, içerik + etiket, kesilen yükleme, listenin gecikmesi
    scale.py                 5, 7, 7b, 9: sayfalar, klasörü çöpe atmak ve sınırı, sürümler ve kota
    naming.py                6, 10: ayrılmış kimlikler, name contains
    durations.py             11: çağrı süreleri
    rate_limit.py            8: dört süreç
    run.py                   koşturucu
    summarize.py             ham çıktıdan drive.json
    check_reserved_ids.py    ayrılmış kimliklerin 1., 3., 7. gün bakışı
    requirements.txt         Google kütüphaneleri, bu makinenin sürümleriyle
tmp/m528/local/, tmp/m528/colab/   ham çıktı, deney başına bir JSON (git dışında)
```

**Neden `queen-studio/measurements/drive.json`:** sonraki maddeler (v1-8, v1-9) çağrı sayılarını ve
sürelerini 4. adımın tablosuyla sınar; tablonun dayandığı ölçümler de kodun okuyabileceği bir yerde,
kodun yanında durur. Belge değil veridir: `docs/` insan içindir ve hiçbir test bir `.md` okumaz
(CLAUDE.md). Her varsayımın kaydında iddiası, iki makinedeki sayıları ve `holds` vardır; `holds`
`summarize.py`'de iddianın yanında yazılı bir kuralla hesaplanır, elle yazılmaz. Türkçe özet bu
belgenin Sonuçlar bölümündedir; ikinci bir özet dosyası yok. v1-26'nın ComfyUI ölçümleri aynı
klasöre `comfy.json` olarak girebilir.

Betikler `core/`'un dışında: core onları çağırmaz, onlar core'u. ruff onları da tarar (suite'in
`test_checks.py`'si); pyright taramaz, çünkü Google'ın istemcisi türsüz ve sıkı kip her çağrıda
"bilinmeyen tür" der. Betiklerin testi yok: ölçümün kendisi Drive'a karşıdır, her deney önce küçük
sayılarla bir kez denendi.

Google kütüphaneleri `.venv`'de (v1-1) ve 5. adımın seçtiği resmî istemcidir; adaptör de onu
kullanacağı için süreler onunla ölçülür. Core'un `requirements.txt`'sine girmez: Drive adaptörü
gelince (v1-8) o maddenin işidir.

## Deneyler

4. adımın küçük deneyleri, şu farklarla:

| # | Varsayım | Ne yapıldı |
|---|---|---|
| 1 | Kimlikle okuma (md5) başka yazmadan hemen sonra güncel | A 200 kez yazar, her yazmada B'ye haber verir; B kendi bağlantısıyla hemen okur. "İki Colab" aynı makinede iki ayrı bağlantıdır; Drive ikisini ayırt etmez. A'nın `files.update` cevabındaki md5'in yerel md5'le aynı olduğu da sayıldı (4. adım "yazılan geri okunmaz" buna dayanır) |
| 2 | İçerik + etiket tek multipart'ta birlikte | Yazıcı 200 kez, sayaç içerikte ve etikette. Üç okuyucu sürekli: kimlikle bilgi (md5 ve etiket aynı cevapta), klasörün listesi (ana listenin okuduğu) ve indirme (içerik başlığında boyu ve md5'iyle, yarım kopya geçemez) |
| 3 | Var olan dosyanın yeni içeriği yükleme bitince görünür | Multipart güncelleme gövdenin %10, %50, %90'ında ve son bayttan önce kesilir (5'er kez); sonra bütün gövde gönderilip cevap okunmadan kesilir (4. adımın belirsiz yazması); resumable güncelleme ilk parçadan sonra bırakılır |
| 4 | `files.list` etiket ve md5 döner; gecikmesi | 100 yeni dosya ve 100 güncelleme; yazmadan hemen sonra, sonra 0,5 sn'de bir listelenir |
| 5 | 1000 proje çoğunlukla tek sayfa | Ana liste satırı etiketli (ad üçe bölünmüş) 1000 dosya; ana listenin istediği alanlarla `pageSize=1000`, 100 kez |
| 6 | Ayrılmış kimlikler günlerce geçerli | Bugün: ayrılmış kimlikle dosya ve klasör, aynı kimlikle ikinci oluşturma (`409`). 10 kimlik ayrıldı: 1., 3. ve 7. gün üçer tanesiyle dosya oluşturulur |
| 7 | Çok dosyalı klasör tek çağrıda çöpe | 5'in klasörü 2000 dosyaya doldurulur, yalnız klasör çöpe atılır; içindekilerin `trashed`'i 2 sn'de bir sayılır |
| 7b | `drive.file`'da klasörün altında kaç dosya olursa olsun çöpe gider (koşuda eklendi: ilk koşunun kök klasörü reddedildi, aşağıda) | Yalnız bu makineden: klasör 100'lük parçalarla 1900'den 3000'e 50'şer doldurulur, her adımda çöpe atılıp hemen geri alınır |
| 8 | Dört Colab saniye sınırına takılmaz | Bu makineden dört süreç, her biri kendi dosyasına saniyede 3 yazma, 60 sn; her yazma bir kez denenir, `403/429` sayılır. Yazma 1 KB'lık multipart: sınır istek sayısınadır, bu makinenin yükleme hızı sayıya karışmasın. Bir kez koştu; ardından kullanıcı ölçmeyi bıraktırdı (aşağıda) |
| 9 | Her güncelleme sürüm bırakır; eski sürümler kotaya sayılmaz | 0,25 MB'lık sıkışmaz dosya 500 kez; `revisions.list` ve `about.storageQuota` farkı, kota 5 dk izlenir |
| 10 | `name contains` büyük/küçük harfe bakmaz | Export adlarına benzeyen 11 klasör ("Final", "final", "FINAL (1)", "My Final Cut", Türkçe I/ı/İ/i…), 17 sorgu; listede görünür görünmez ve 60 sn sonra |
| 11 | Çağrı süreleri (0,25 / 0,6 / 0,3 sn) | 12 çağrı türü, 100 tur, türler sırayla (yavaş bir dakika hepsine düşsün); her denemenin kendi süresi, bekleme hariç. Üstüne: aynı anda 8 okuma, 5 × 20 MB resumable yükleme |

## Maliyet

Bir makinedeki tam koşu Drive'a ~8.000 çağrı yapar: oluşturmalar (~2.300), güncellemeler (~1.500),
okumalar ve listelemeler (gerisi; 2. ve 4. deneyin okuyucuları en büyük kalem). Hepsi tek kök
klasörün altında. Hız sınırı deneyi dışında her çağrı 403/429'da üstel bekler (en çok 32 sn, rastgele
kaydırmayla) ve beklemeler deney başına Drive'ın nedeniyle sayılır (`retries`). Süre ölçümünde
bekleme sayılmaz: başarılı denemenin süresi alınır.

## Ne kaybolabilir, ne sızabilir

- Token'ın yolu komut satırından gelir; hiçbir betik onu ya da ondan okunanı basmaz. Hatalar
  Drive'ın sözüyle kaydedilir; Drive'ın sözü token taşımaz. Colab'da token koşudan önce yüklenir,
  sonra VM'den silinir; oturum kapatılır.
- Her şey tek kök klasörde, 5'in ve 7b'nin büyük klasörleri dışında: onlar kökün yanında kendi
  klasörlerindedir, çünkü ilk koşunun kökü 2.000 dosyalı çöpteki klasörüyle birlikte çöpe atılamadı
  (Sonuçlar, 7). Koşu sonunda hepsi Drive'ın çöpüne gider (FOUNDATION 1: kalıcı silme yok). Koşu
  yarıda düşerse kimlikleri `tmp/m528/<makine>/root.json`'da kalır.
- Ham sonuçlar ve `drive.json` geçici dosyaya yazılıp yerine konur.
- 6. deneyin sonraki bakışları kök klasörü kullanmaz (o gün çöpte olur, içinde açılan dosya da çöpe
  düşerdi): dosya Drive'ın köküne açılır ve hemen çöpe atılır.

## Bitti sayılır

- Her varsayım ve çağrı süreleri bu makinede ve Colab'da ölçüldü; hız sınırı bu makinede.
- `drive.json` depoda; her varsayımın `holds`'u kuralıyla hesaplandı. Ayrılmış kimliklerinki
  bekliyor (`null`); bakışları `check_reserved_ids.py` yazar.
- Tutmayanlar Sonuçlar'da sayısıyla ve tasarımda neyi bozduğuyla yazılı.

## Komutlar

Depo kökünden:

```bash
queen-studio/.venv/Scripts/python queen-studio/measurements/drive/run.py --token .secrets/drive-token.json --out tmp/m528/local --host local --reserve-pending
queen-studio/.venv/Scripts/python queen-studio/measurements/drive/run.py --token .secrets/drive-token.json --out tmp/m528/local --host local rate_limit trash_limit
queen-studio/.venv/Scripts/python queen-studio/measurements/drive/summarize.py --raw tmp/m528
queen-studio/.venv/Scripts/python queen-studio/measurements/drive/check_reserved_ids.py --token .secrets/drive-token.json --day 1
```

Colab'da: CPU oturumu (`colab new -s m528`, GPU'suz), betikler ve token `colab upload` ile
`/content/m528/`'e, `run.py --host colab` VM'de arkada, sonuçlar `colab download` ile
`tmp/m528/colab/`'a; token `colab rm` ile silinir, `colab stop`.

## Sonuçlar

6 Kasım. "Yerel" bu makine (Türkiye'den), "Colab" ücretsiz katmanın CPU oturumu (us-central1).
Sayılar `queen-studio/measurements/drive.json`'da; süreler medyan (p50).

| # | Varsayım | Tuttu mu | Ölçülen |
|---|---|---|---|
| 1 | Kimlikle okuma yazmadan hemen sonra güncel | Tuttu | 200 okumada 0 eski md5, iki makinede de; `files.update`'in döndürdüğü md5 200/200 yerel md5'le aynı |
| 2 | İçerik + etiket birlikte | Tuttu | md5 ile etiket hiç ayrışmadı: yerel 2.463, Colab 4.807 okuma; yarım indirme 0 (434 / 842) |
| 3 | Yükleme bitmeden yeni içerik görünmez | Tuttu | Kesilen 20/20 multipart ve 5/5 resumable eski haliyle kaldı. Cevabı okunmayan bütün gövde yazıldı (5/5; yerel ~1,9, Colab ~1,3 sn sonra): 4. adımın belirsiz yazması |
| 4 | Liste etiket ve md5 döner; gecikme | Tuttu | Döner; 200/200 yazma ilk listelemede göründü, gecikme 0 sn, iki makinede de |
| 5 | 1000 proje tek sayfa | Tuttu | 100/100 listeleme tek ve tam sayfa; tam liste yerel 1,40, Colab 0,83 sn |
| 6 | Ayrılmış kimlik günlerce geçerli | Bekliyor | Bugün: kimlikle dosya ve klasör açılıyor, ikinci oluşturma `409` ("A file already exists with the provided ID."). 10 kimlik ayrıldı (2026-11-06T14:13:39Z); bakışlar 7, 9 ve 13 Kasım 14:13Z'de, `check_reserved_ids.py` |
| 7 | Çok dosyalı klasör tek çağrıda çöpe | Tuttu, gecikmeyle | 2.000 dosyalı klasör tek çağrı (yerel 2,6, Colab 2,0 sn); içindekiler arkada çöpe gidiyor: hepsi yerel 20, Colab 10 sn sonra |
| 7b | `drive.file`'da sınır yok | Tuttu, bir açıklanamayan retle | 3.000 dosyalı klasör 23 adımın hepsinde çöpe gitti (3–4 sn). Ama ilk yerel koşunun kökü reddedildi, aşağıda |
| 8 | Dört Colab saniye sınırına takılmaz | Tutmadı | 720 yazmada `403/429` yok, 14 `503 transientError`. Drive reddetmek yerine yavaşlattı: istenen 12/sn'ye karşı hesapta ~5,4 yazma/sn; yazma p50 2,4, p90 14,6, en çok 35 sn |
| 9 | Her güncelleme sürüm bırakır; eskiler kotaya sayılmaz | Tuttu | 500 güncellemede 101 sürüm (Drive 100'den eskisini hemen siliyor); sürümler 25 MB, kota yalnız şu anki dosya kadar arttı (250.069 B), 5 dk izlendi, iki makinede de |
| 10 | `name contains` büyük/küçük harfe bakmaz | ASCII'de tuttu | "Final"/"final"/"FINAL" üçünü de buluyor. Ama arama kelime başıdır ("inal" hiçbir şey bulmaz; "Final (1)" "Final"ı da bulur) ve Türkçe I'da tutmaz: "IŞIK" "Işık"ı bulmaz; "İz"/"iz"/"Iz" ikisini de bulur. İki makinede aynı |
| 11 | Çağrı süreleri | Yazmalarda tutmadı | Aşağıdaki tablo |

**Çağrı süreleri** (100'er; varsayılan 4. adımın Varsayımlar'ından, Colab'dan):

| Çağrı | Varsayılan | Yerel | Colab (p90) |
|---|---|---|---|
| Bilgi okuma (`files.get`) | 0,25 | 0,27 | 0,08 (0,11) |
| Küçük klasörü listelemek | 0,25 | 0,32 | 0,10 (0,14) |
| `generateIds` (1000) | 0,25 | 0,23 | 0,06 (0,07) |
| `about` | 0,25 | 0,27 | 0,08 (0,11) |
| Yalnız etiket güncellemek | 0,25 | 0,71 | **0,28** (0,36) |
| Çöpe atmak | 0,25 | 0,75 | **0,38** (0,47) |
| Kopya, 1 MB | 0,25 (export toplamından) | 1,07 | **0,58** (0,73) |
| Baş dosyası yükleme, 110 KB | 0,6 | 1,57 | **0,81** (0,97) |
| Baş dosyası yükleme, 250 KB | 0,6 | 1,58 | **0,82** (1,07) |
| Baş dosyası oluşturma, ayrılmış kimlikle | 0,6 | 1,50 | **0,79** (0,92) |
| İndirme, 250 KB | 0,3 | 0,84 | 0,27 (0,35) |
| İndirme, 1 MB | 0,3 | 0,76 | 0,28 (0,35) |
| Aynı anda 8 okuma, 100 çağrı | — | 3,2 sn toplam | 1,0 sn toplam; çağrı başı 0,08 |
| 20 MB resumable yükleme | — | 5,2 | 1,6 (2,0) |

Colab'da okumalar varsayılandan hızlı, yazmalar yavaş. Bir değişiklik (bak + yaz) ~0,08 + 0,81 ≈
0,9 sn: 4. adımın ~0,85 sn'sine yakın, ama parçaları ters. 2. deneyin 200 yazmasında p99 4,5 sn, en
çok 5,3 sn. Bu makineden her şey Colab'ın ~2 katı ve üstü.

**Tutmayanların tasarımda dokunduğu yerler** (düzeltme ana agent'ın kararı):

- **8, hız sınırı:** gerçek kullanım (Colab başına dakikada ~10 değişiklik) bunun çok altında. Ama
  hesap başına yazma ~3–6/sn'de yavaşlıyor: 1.100 dosya 4 iş parçacığıyla (~2,8/sn) açılırken de 10
  kez `403 userRateLimitExceeded` geldi. 500 fotoğraflı export'un kopyaları (4. adım: "foto 500 → ~16
  sn", 8 paralel) bu hızla ~1,5–3 dakika sürer. `503 transientError` de yeniden denenmelidir.
  Kullanıcı ölçmeyi bıraktırdı (6 Kasım: "core 403/429'da zaten bekliyor; Google yalnız dakika
  kotalarını yazıyor"); sonuç, ondan önce koştuğu için tutuldu, 20 dosyaya yayılan çeşidi koşmadı.
- **11, süreler:** yazmalar ~0,8 sn, etiket ve çöp ~0,3–0,4 sn, kopya ~0,6 sn; 4. adımın maliyet
  tablosunun bu satırları bu sayılarla düzelir. Okumalar ve indirmeler tutuyor.
- **10, ad araması:** sorgu yalnız daraltır; aynı adı kod tam karşılaştırmalıdır. Türkçe I/ı'da
  Drive bazı adları hiç döndürmez.
- **7, çöp gecikmesi:** klasörün içi 10–20 sn çöpte görünmez. Proje silmede önce baş dosyası çöpe
  gittiği için proje hemen yoktur; bu arada klasörün içi okunmaz, zararı yok.
- **7b, açıklanamayan ret:** ilk yerel koşunun kök klasörü 5 dakika boyunca `403
  appNotAuthorizedToChild` ("The user may not have granted the app … write access to all of the
  children") ile reddedildi. İçinde çöpe atılmış 2.000 dosyalı klasör ve ~350 başka öğe vardı,
  çoğu çöpte. O klasör dışarı taşınınca kök çöpe gitti; klasör de küçük bir klasörün içinde sorunsuz
  çöpe gitti. 7b 3.000 dosyada reddetmediğine göre neden dosya sayısı değil; bulunamadı. `drive.file`
  iznine özgü bir kontrol: core Colab'da kendi girişiyle gidiyorsa ona dokunmayabilir; bu makineden
  gerçek Drive'a koşan testlerin (v1-8, v1-9) proje silme testi buna çarpabilir.
- **9:** eski sürümler kotaya sayılmıyor; Değerlendirme 9'un "kotaya sayılıyorsa" düzeltmeleri
  (history bloğunu 1 MB'ta kapatmak, `revisions.delete`) gerekmiyor.

**Ölçülemeyen:** 6'nın günleri (bekliyor). 8 yalnız bu makineden, kararla.
