# Madde 324 — Üretimi ne durduruyorsa basmadan söyleniyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7-kol-b` *(Kol B)* · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.**

## Bugün ne oluyor

Referanstan'da her ret basıştan sonra geliyor. `Kuyruğa ekle` yalnız istek yoldayken, üretici
eksikken ve başka projede üretim sürerken kapalı *(`LayerPanel.jsx`)*; boş kutu, boş havuz ve WAN
oturumu basılabiliyor, ve cevap sunucudan kırmızı kartla dönüyor. Panelin havuzdan haberi yok: havuzu
yalnız ortadaki `ReferencePanel` okuyor. Üreticiler cevabı video satırında modelin **adını** veriyor
*(`list_producers.py`)*, referans okuyup okumadığını söylemiyor. Sunucunun boş havuz cümlesi
`… önce soldaki panele en az bir referans ekle.` — artık olmayan bir paneli gösteriyor
*(`queue_references.py`)*.

## Kurallar

1. **Varyant kutusunun altında, düğmenin üstünde bir satır**, yalnız Referanstan'da. Uygulamanın
   sırasıyla ve bir seferde tek cümle:
   - video üreticisi kurulu ve referans okumuyorsa:
     `Referanstan üretim için H3 gerekiyor — bu oturumda başka bir video modeli kurulu.`
   - değilse, havuz boşsa: `Havuzda referans yok — önce en az bir referans ekle.`
2. **Üretici kurulu değilken satır H3'ten söz etmiyor** — kurulum kartı söylüyor. Boş havuzu yine
   söylüyor *(tasarımın `poolRefusal`'ı)*.
3. **Herhangi bir tipten tek referans yetiyor**, ve havuz onu alınca satır o anda kalkıyor — havuz
   ortadayken eklenen referansla da.
4. **Referanstan'da `Kuyruğa ekle` kapalı:** istek yoldayken, üretici eksikken, satır bir şey
   söylerken, prompt kutusu boşken *(yalnız boşluk da boş)*; başka projede üretim sürerken bugünkü
   gibi. Kareden'in düğmesi değişmiyor.
5. **Sunucunun boş havuz cümlesi satırınkinin aynısı.**
6. **Henüz cevap vermemiş bir şey satıra girmiyor:** üreticiler ya da havuz konuşmadan satır o konuda
   sessiz, ve düğmeyi o kilitlemiyor.

**Neden ekranda, ve neden kural değil.** FOUNDATION 4 neyin açık olduğunu arayüze bırakıyor. Satır ve
kilit sunucunun kurallarının önizlemesi: kapı aynı durumları yine kendisi reddediyor
*(`queue_references.py`)*, ve satırın göremediği bir durumda — havuzun cevabı gelmeden, ya da
Drive'dan elle silinen son referansta — basış gidiyor, cevabı sunucu veriyor.

**H3'ü sunucu söylüyor.** Video satırı yeni bir alan taşıyor: `reads_references` — bu oturumun video
modeli referanstan üretebiliyor mu. Ekran modelin adını karşılaştırmıyor: "yalnız H3 referans okur"
sunucunun kuralı *(kapı `has_h3`'le reddediyor)*, ve ad ekranın göstereceği sözcük, karar anahtarı
değil — ad değiştiği gün satır bir H3 oturumuna sessizce "H3 gerekiyor" derdi.

**Havuzu panel nereden biliyor.** Ortadaki havuzun sunucudan aldığı son cevaptan — tasarımın
yorumuyla, *"The panel's missing line reads the same pool."* Panel onu `pool` diye alıyor
*(sunucunun `{references, limits}` cevabı; hiç gelmediyse yok)*. Yol haritasının kol düzeni 324'ün
havuza "kendisi sorarak" öğrendiğini yazıyor; ama havuz ortadayken eklenen bir referansı panel kendi
sorusuyla duyamaz — sorusu ancak sekme açılırken gider, ve satır eklemeyle kalkmazdı *(bitti ölçütü:
"bir referans eklenince satır kayboluyor")*. Havuzun her cevabı ekrana ulaşmalı, yani uygulama turunda
`ReferencePanel` küçük bir değişiklik alıyor — Kol A'nın dosyası, birleşmede ikinci bir çakışma yeri
olabilir. Ekran testi mekanizmaya bağlı değil: sahte bir sunucuyla koşuyor, ve yüklenen referans
sonraki her listede duruyor.

**Basınca sıra** *(varyant, prompt listesi, havuz)* bugün zaten böyle: varyantın boşluğunu ekran
basışta ilk söylüyor *(`refusalOf`)*, sunucu listeyi havuzdan önce okuyor *(`parse_prompts`, sonra
`list_references`)*. Madde ikisine de dokunmuyor; yeni test yazılmıyor.

## Yazılacak testler

### `test_producers.py`

1. **Video satırı modelin referans okuyup okumadığını söylüyor** — `h3` → `True`; `wan` ve `""` →
   `False`.

### `LayerPanel.test.jsx` — yeni blok *"what stops a run from the pool (madde 324)"*

Bloğun varsayılan üreticisi H3 satırı *(`reads_references: true`)*; her test havuzunu `pool` ile
veriyor, sunucunun cevabı biçiminde.

2. **Boş havuz, hiçbir şeye basılmadan, varyant kutusuyla düğmenin arasında söyleniyor.**
3. **Havuz tek bir referans alınca satır kalkıyor ve düğme açılıyor, tipi ne olursa olsun** — boş
   havuz ve yazılmış bir listeyle satır duruyor, düğme kapalı; havuz tek bir sesle yeniden verilince
   satır yok, düğme açık.
4. **WAN oturumunda H3 cümlesi, düğme kapalı** — havuzda referans, kutuda liste varken.
5. **Sıra: H3 boş havuzdan önce** — WAN ve boş havuz: yalnız H3 cümlesi.
6. **Üretici kurulu değilken H3 yok, boş havuz var.**
7. **Prompt kutusu boşken düğme kapalı** — H3 ve dolu havuzla: boş kutu kapalı, yalnız boşluk kapalı,
   liste açık.
8. **Satır ve yeni kilitler Referanstan'ın** — boş havuzla Referanstan satırı söylüyor; Kareden'e
   geçince satır yok, düğme açık.

### `ProjectScreen.test.jsx` — yeni blok *"what stops a run from the pool (madde 324)"*

Dosyanın başına sahte bir havuz sunucusu, `poolServer`: `listReferences` o anki havuzu veriyor,
`uploadReferences` dosyayı sıranın sonuna koyup yeni havuzu döndürüyor. Her test boş havuzla başlıyor.

9. **Ortada eklenen referans satırı kaldırıyor, yazılan liste düğmeyi açıyor** — boş havuzla
   Referanstan: satır var, düğme kapalı; Fotoğraflar'ın `Ekle`'sinden `kedi.png`: satır yok, düğme
   hâlâ kapalı *(kutu boş)*; liste yazılınca açık. Bitti ölçütünün kendisi, ve havuzdan panele uzanan
   kablonun tek testi.

**Değişen:**

- `test_reference_usecases.py` — `test_a_reference_run_with_an_empty_pool_is_refused` cümlede yalnız
  `referans` arıyordu; artık cümlenin kendisini: `Havuzda referans yok — önce en az bir referans ekle.`
- `ProjectScreen.test.jsx` — 323'ün `says the server's own sentence under the button` testi dosyanın
  varsayılan boş havuzuyla basıyordu; 324'le boş havuzda düğme kapalı. Aynı soruyu içinde `kedi.png`
  olan bir havuzla soruyor — bugün de sonra da yeşil.
- `ProjectScreen.test.jsx` — api taklidindeki `listReferences`'ın sabit boş cevabı gidiyor; boş havuzu
  her testin başında `poolServer([])` veriyor. 318'in bloğu aynı cevabı alıyor.

**Bekçiler:**

- `LayerPanel.test.jsx` — havuzu ve üreticiyi bilmeyen panelde basış gidiyor *(Kural 6)*:
  `sends a list it cannot read as it was typed`, `sends the prompts and the variants under the
  reference kind`, `writes the record first when the press goes out, then sends the work`,
  `sends nothing when the record cannot be written`. Kareden'in düğmesi ve basışın ilk sorusu:
  `stays pressable with nothing to do, and says nothing until it is pressed`, `locks the button only
  while the request is in flight`, `says the variant box is empty`, `is disabled while another
  project holds the worker`. Satır bir blok değil: `lays Referanstan out in the design's order`.
- `SidePanel.test.jsx` — `passes the reference prompt list through to the queue`: havuz verilmemiş
  sütun basışı kesmiyor.
- `ProjectScreen.test.jsx` — madde 318'in bloğu *(`Fotoğraflar 0/9`)*.
- Sunucu — `test_a_row_says_nothing_about_installing_because_the_app_does_not` *(fotoğraf satırı yeni
  alanı almıyor)*, `test_the_video_row_names_the_model_the_notebook_installed`,
  `test_a_reference_run_without_h3_is_refused`,
  `test_a_reference_run_reads_the_prompt_list_the_way_the_photo_panel_does`,
  `test_a_refused_reference_run_is_a_400_with_its_reason`.

## Birleşme

Kol A'yla çakışabilecek yerler: `queue_references.py` *(beklenen — 321 boşluk reddini siliyor)*,
`test_reference_usecases.py` *(321 boşluk testini, değişen testin hemen altından siliyor)*, ve
uygulama turunda `ReferencePanel.jsx`.

## Bitti sayılır

Dört test satırı koşulur. Kırmızı, doğru sebeple: `test_producers.py`'de 1 *(alan yok)*,
`test_reference_usecases.py`'de değişen test *(eski cümle)*, `queen-editor` vitest'te 2–9 *(satır
yok, düğme boş kutuda açık)*. 323'ün taşınan testi, pytest'lerin geri kalanı ve `queen-agent`
vitest'i yeşil.
