# Madde 444 · Copy başarıda komple yeşil — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
444 (eski adı v10-6) · **Dal:** `feat/queenagent-v10` · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Tasarım:** `queen-design`'ın `queen-agent-v4` dalı, madde 219 — `projects/queen-agent/kit.css`'in
Copy kuralları (`.ghost[data-said]`, üç Copy'nin `min-width`'i, `.reader__copy:disabled`), `kit/`
sayfası, `BEHAVIOUR.md`'nin *"`?copy=copied` or `failed`"*, *"`copy` hides unless `file` is `read` or
`failed-later`"* ve kenar çubuğunun *"`chats` (`listed`, `failed`)"* satırları, `DESIGN-STANDARD.md`'nin
renk tablosu.

## Ne, neden

Kullanıcı, 1 Ekim: *"bir cpyu basın cpied kırmızı geliyor buton komple yşeil olsun yleişi görmek
sitiyorum"*. 5 Ekim, bütün Copy düğmelerine mi diye sorulunca: *"evet olur"*; *"Could not copy"*
bugünkü gibi mi kalsın diye sorulunca: *"olur"*; yeşilin tonu için: *"tasarımcaya yaptırtırırız"*.

Bugün başarılı bir kopyalamadan sonra düğme 2,5 saniye *"Copied"* diyor, ama yazı uygulamanın vurgu
rengi `--accent` (`#b5623c`, kiremit kırmızısı) ile yazılıyor. Başarı, hata gibi okunuyor. Kural üç
yerde ayrı ayrı yazılmış: `workspace.css`'in `.sidebar__copy[data-said="yes"]`,
`.reader__copy[data-said="yes"]` ve `.empty__copy[data-said="yes"]`'i.

**Olacak:** kopyalama başarılı olunca düğmenin tamamı yeşile döner — yüz `#e0ebd6`, kenar `#6f8a5f`,
söz `#536747` —, 2,5 saniye sonra bugünkü hâline. *"Could not copy"* düğmede kırmızı söz kalır.

## Kodda bakıldı

- **Tek bileşen:** üç Copy de [CopyButton.jsx](../../queen-agent/frontend/src/features/workspace/CopyButton.jsx)
  — kenar çubuğunun okunamayan sohbet listesi (`sidebar__copy`), açık dosyanın başlığı
  (`reader__copy`), okunamayan proje listesi (`empty__copy`, All projects'te ve isimlendirme
  ekranında). Hepsi `ghost` sınıfını ve sonucu `data-said="yes"` / `"no"` olarak taşıyor. 2,5 saniye
  bugün de var (`SAID_MS`).
- **Genişlik:** yalnız `.reader__copy` en az 116 px. Kenar çubuğundaki ve proje listesindeki Copy'nin
  en azı yok: *"Could not copy"* gelince düğme genişliyor, yanındaki ve altındaki kayıyor. Tasarımda
  üçü de en az 116 (`kit.css`: *"so Could not copy takes Copy's place and nothing beside it moves"*).
  Uygulama da tasarım da `box-sizing: border-box`, yani 116 düğmenin dış genişliği.
- **Soluk ama yeşil:** düğme `disabled={!text}`; basılamaz, ama 2,5 saniyelik söz sürerken metin
  boşalırsa söz ve `data-said` kalıyor. Dosya başlığında olur: bir dosyada Copy'ye basıp hemen başka
  bir dosya açılınca yeni dosya okunurken `file` boş, düğme soluk — ve yeşil olurdu. Tasarım: *"a
  dimmed Copy never turns green"*. Yeni dosya 2,5 saniye içinde gelirse de söz kalıyor: `FilePanel`
  bileşeni anahtarsız çiziyor, ve hiç kopyalanmamış dosyanın düğmesi *"Copied"* diyor.
- **Renkler:** uygulamanın renk değişkenleri `shared/app.css`'in `:root`'unda (*"Colours … are defined
  here and nowhere else"*), aileler hâlinde: `--accent` ve iki hover'ı, `--destructive` ve
  `-hover`/`-line`/`-soft`'u. Yeşil bugün değişken değil: `#6f8a5f` (`.file-card__saved`, *"✓ saved to
  project"*) ve `#536747` (`.msg__stamp-cached`) `workspace.css`'te düz yazılı. Tasarım bunları
  "uygulamanın tek yeşili" diye anıyor, ve Copy'nin yeşili aynı iki tondan yapılıyor.

## Olacak

### 1 · Yeşil, `app.css`'te bir aile *(tasarım 219)*

Yeşil üç yerde kullanılacak — kaydedildi işareti, cached sayısı, Copy —, ve `#e0ebd6` yeni. Kırmızı
gibi bir aile olur, `:root`'ta:

- `--success: #6f8a5f` — *"✓ saved to project"*, ve başarılı Copy'nin kenarı;
- `--success-dark: #536747` — cached sayısı, başarılı Copy'nin sözü ve pointer altındaki kenarı;
- `--success-soft: #e0ebd6` — başarılı Copy'nin yüzü.

`.file-card__saved` ve `.msg__stamp-cached` aynı renkleri değişkenden okur; görünüşleri değişmez.
Aynı renk iki biçimde yazılı kalmaz.

### 2 · Tek kural: `.ghost[data-said]` *(tasarım 219)*

Üç sınıfın altı `data-said` kuralı silinir, yerine tasarımdaki gibi tek kural gelir. Yeşilin hover'ı
`.ghost:hover`'dan ağır, yani pointer altında yeşil kenar bej kenarı yener:

- `.ghost[data-said="yes"]` — yüz `--success-soft`, kenar `--success`, söz `--success-dark`;
- `.ghost[data-said="yes"]:hover` — kenar `--success-dark`;
- `.ghost[data-said="no"]` — söz `--destructive`, bugünkü gibi.

`data-said`'i yalnız `CopyButton` yazıyor, yani kural yalnız Copy'yi tutar; Refresh `ghost` olsa da
etkilenmez.

### 3 · Üç Copy de en az 116 px *(tasarım 219)*

`.reader__copy`'nin `min-width: 116px`'i `.reader__copy, .sidebar__copy, .empty__copy` diye üçünü
birden tutar. *"Copied"* ve *"Could not copy"* Copy'nin yerine yazılır, yanındaki ve altındaki
kaymaz.

### 4 · Söz, kopyalanan metnin; soluk Copy hiç yeşil olmaz *(tasarım 219)*

`CopyButton` sözünü, basıldığı metinle birlikte tutar (`{ word, text }`), ve sözü ve `data-said`'i
yalnız o metin hâlâ düğmenin metniyken gösterir. Metin boşalınca — düğme soluk — ya da başka bir
metin gelince düğme *"Copy"* der ve `data-said` taşımaz. Zamanlayıcı bugünkü gibi sürer ve sözü
kendisi siler.

### 5 · Kenar çubuğunun *"Couldn't load chats."* hali — uygulamayla karşılaştırma

Tasarım bu hâli ilk kez çizdi; uygulamada Madde 386'dan beri var. Aynı olanlar: listenin yerinde
`Couldn't load chats.` (13 px, `#8a5237`), altında *Try again* ve Copy, 8 aralıklı, dar sütunda Copy
alta kayar; Copy hatanın kendi sözünü panoya koyar; katlanınca hiçbiri çizilmez.

Farklar:

- **Copy'nin genişliği:** tasarımda en az 116, uygulamada yok — 3'te, bu maddede.
- **Copy'nin başarı rengi:** 2'de, bu maddede.
- ***Search chats* soluk ve basılamaz:** tasarımda liste okunamayınca arama kutusu `disabled` ve
  soluk (`opacity: 0.4`); uygulamada açık kalıyor (arama zaten hiçbir şey göstermiyor, Enter bir şey
  açmıyor). Bu Copy'nin görünüşü değil.
- **Aralık:** tasarımda cümleyle düğmeler arası 12 px ve altta boşluk yok (`.sidebar__error`'ın
  `padding: 10px 12px 0`'ı, `.sidebar__actions`'ın `padding: 12px 12px 0`'ı); uygulamada 10 px ve altta
  10 px (`.sidebar__failure`'ın `padding: 10px 12px`'i, `.sidebar__actions`'ın `margin-top: 10px`'i).
  Bu da Copy'nin görünüşü değil.

Son iki fark bu maddenin dışında, ve 444'te yapılmaz *(koordinatör, 9 Ekim — seçenek 1)*: ikisi
`queen-agent/BACKLOG.md`'ye girer, ve sonraki bir maddede ele alınır.

## Sınırlar

- *"Copied"*, *"Could not copy"* sözleri ve 2,5 saniye değişmez.
- Refresh ve öteki `ghost` düğmeler değişmez.
- Kenar çubuğunda *Search chats*'in soluklaşması ve hata hâlinin aralığı yapılmaz (5'te).
- Arka uç değişmez. queen-editor'e dokunulmaz.

## Değişen dosyalar

- `frontend/src/shared/app.css` — yeşil aile.
- `frontend/src/features/workspace/workspace.css` — `.ghost[data-said]`, üç Copy'nin `min-width`'i,
  silinen altı kural, iki yeşilin değişkene geçmesi.
- `frontend/src/features/workspace/CopyButton.jsx` — söz kopyalanan metne bağlı.
- Testler: `CopyButton.test.jsx` (yeni), `app.css.test.js`, `workspace.css.test.js`.
- `frontend/dist` yeniden derlenir.

## Testler

**Bileşen (`CopyButton.test.jsx`, yeni):** üç yer aynı bileşeni kullandığı için davranış bir yerde
tutulur.

- Başarılı kopyalamadan sonra düğme *"Copied"* der ve `data-said="yes"` taşır.
- Başarısız kopyalamadan sonra *"Could not copy"* ve `data-said="no"`.
- 2,5 saniye sonra *"Copy"*, `data-said` yok.
- Söz sürerken metin boşalırsa düğme soluk, *"Copy"* der, `data-said` taşımaz.
- Metin yokken düğme soluk ve `data-said` taşımaz.
- Söz sürerken başka bir metin gelirse düğme basılabilir, *"Copy"* der, `data-said` taşımaz.

**CSS (`app.css.test.js`, `workspace.css.test.js`)**, kilit testleri (jsdom stil yüklemez):

- `:root` yeşil aileyi taşır: `--success: #6f8a5f`, `--success-dark: #536747`,
  `--success-soft: #e0ebd6`.
- `.ghost[data-said="yes"]` yüzü, kenarı ve sözü aileden okur; hover'da kenar `--success-dark`.
  `.ghost[data-said="no"]` yalnız sözü `--destructive` boyar.
- Hiçbir kural Copy'nin başarısını `--accent`'le boyamaz: sınıf başına `data-said` kuralı kalmaz.
- Üç Copy de `min-width: 116px`.
- `.file-card__saved` `--success`, `.msg__stamp-cached` `--success-dark` okur.

## Bitti sayılır

- Yukarıdaki testler yeşil, dört suite yeşil, `dist` yeniden derlenmiş.
- Kullanıcının denemesinde: üç Copy'nin her biri başarılı kopyalamada tamamen yeşile dönüyor ve 2,5
  saniye sonra eski hâline geliyor; kopyalanamazsa *"Could not copy"* kırmızı yazıyla; sözü değişince
  düğmenin genişliği değişmiyor; dosya okunurken soluk Copy yeşil olmuyor, ve başka bir dosya
  açılınca onun Copy'si *"Copied"* demiyor.
