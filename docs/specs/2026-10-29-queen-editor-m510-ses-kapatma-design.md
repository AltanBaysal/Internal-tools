# Madde 510 · Videonun sesi kare sayfasından kapatılabilir — tasarım

**Tarih:** 29 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-9),
510 · v11-9 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kabul koşulu (maddeden)

- Videonun izlendiği kare sayfasında, sesi olan videonun sağ üstünde bir ses ikonu var. Basınca o
  videonun sesi kapanıyor, bir daha basınca açılıyor.
- Sesi kapalı video kare sayfasında sessiz oynuyor ve export'ta sessiz çıkıyor; öteki videolar sesli.
  Sessiz, hiç ses yok demek: H3 videosunun kendi sesi de girmiyor.
- Export ekranı, bugünkü "N videonun sesi yok" uyarısının yanında "N videonun sesi kapalı" diyor.
- Ses projede durmaya devam ediyor; yeniden açılınca geri geliyor.

Kararlar maddede yazılı. Kısaca:

- hangi ses: MMAudio'nun sesi;
- yeri: kare sayfası, galerinin kartı değil (*"abi card a değil detay sayfaına gelecek"*);
- kalıcı: yeniden açılana kadar kapalı;
- kare sayfasında da sessiz (*"hayır kare sayfasındada kapatılır es"*);
- export ekranında ayrı satır (*"Mantıklı"*);
- sessiz, hiç ses yok demek.

Ekrandaki sürüm V11 kalır.

## Bugün

- **Export** (`run_export._write`): her karenin videosu `exporter.piece(video, ses, hedef)` ile kesilir.
  `_audio_of` karenin MMAudio sesini verir, ses yoksa ya da kırmızıysa `None`.
  - Ses varsa ffmpeg videonun görüntüsünü ve katmanın sesini alır.
  - `None`'da dosya olduğu gibi kopyalanır (`-c copy`), yani H3'ün kendi sesi de gelir.
  - Birleşik export'ta sesi olmayan parçaya sessizlik yazılır (`_evened_out`).
- **Kare sayfası** (`PhotoDetail` → `LayerPlayer`): Video sekmesi videoyu kendi sesiyle oynatır. Ses
  sekmesi videoyu susturup MMAudio'nun wav'ını yanında çalar.
- **Export ekranı:** sesi olmayan videoları `summary.silent` ile sayar: *⚠ N videonun sesi yok*.

## Ne yapılır

### Nerede saklanır

Yeni bir dosya: projenin klasöründe `muted.json`, `{"frames": ["P0_0", …]}`.

- **Neden ayrı dosya:** "hangi karenin sesi kapalı" yeni bir soru, ve başka bir anda yazılıyor (ikona
  basınca). CODE-STANDARD, *Separation of concerns*: yeni soruya yeni dosya. Ayarlar, plan, kayıt ve
  sıra dosyaları değişmez.
- **Karenin kimliğiyle tutulur,** dosya adıyla değil. Kopya kare kaynağının ses dosyasını paylaşabilir
  (Kopyala, `carry_all`), ve kullanıcı tek bir videonun sesini kapatır. Kimlikler hiçbir zaman yeniden
  kullanılmaz (`copy_frame.next_id`), bu yüzden silinmiş bir karenin listede kalan kimliği yeni bir
  kareye geçmez.
- **Sesi kapalı sayılmak için karenin sesi olmalı:** listede olup MMAudio sesi olmayan (ya da sesi
  kırmızı olan) kare kapalı sayılmaz. İkon da yalnız sesi olan videoda çıkar, ve export ile kare
  sayfası aynı kuralı okur.
- **"Karenin sesi var mı" sunucuda tek yerde, `domain/mute.py`'de:**
  - `holds_sound(frame)`: galeri satırından. `silenced`, export'un ses seçimi (`_audio_of`) ve
    özetin `silent` sayısı bunu sorar.
  - `require_sound(slots, frame)`: aynı soru, kaydın hücresinden, basış için.

  Ekrandaki karşılığı yalnız bir önizlemedir (`PhotoDetail`).

### Sunucu

- **`data/mute_store.py`, `DriveMuteStore`:** dosyanın adını ve şeklini bilen tek yer.
  - `read(project)`: kimlik listesi; dosya yoksa `[]`. Okunamayan ya da şekli bozuk dosya **boş
    sayılmaz**: `OSError("<proje>/muted.json okunamıyor: …")`. Okuyanlardan biri export: boş saymak,
    kapatılmış videoları sesli çıkarırdı. Bir değişiklik de dosyayı geri yazdığı için, boş saymak
    kapatılmış öteki seslerin hepsini açardı.
  - `put(project, frame, on)`: listeyi okur, kimliği ekler ya da çıkarır, yazar (Storage'ın geçici
    dosya + `os.replace` kaydı) ve yeni listeyi döner. Geri okumaz. Bir `threading.Lock` altında
    yapılır: aynı anda gelen iki basış birbirinin yazdığını silmesin. Zaten olan durum yeniden
    istenirse liste değişmez ve hiçbir şey yazılmaz.
- **`domain/mute.py`:**
  - `holds_sound(frame)`: galeri satırının katmanlarında ses var ve kırmızı değil.
  - `silenced(frame, muted)`: `holds_sound` ve karenin kimliği listede.
  - `require_sound(slots, frame)`: kaydın o karedeki ses hücresinin son satırı `done` değilse
    `NoSound("Bu karenin sesi yok: <kare>")`.
  - `check(on)`: yalnız `True` ya da `False`. Başka bir değer `InvalidMute("Ses kapalı ya da açık
    olmalı.")` olur.
  - `NoSound`: kapatılmak istenen karenin sesi yok.
- **`domain/usecases/mute.py`:**
  - `get_muted(mutes, project)`: proje yoksa `ProjectMissing`, varsa liste.
  - `set_muted(mutes, record, project, frame, on)`:
    1. önce değer bakılır (ucuz ret önce gelir), sonra proje;
    2. kapatmada `mute.require_sound(record.slots(project), frame)`. Sesi olmayan karede hiçbir
       şey yazılmaz.
    3. Açmak her zaman kabul edilir: listede kalmış bir kimlik de böyle temizlenebilir.

  `domain/ports.py`'ye `MuteStore` eklenir.
- **`presentation/mute_routes.py`, `make_mute_blueprint`:**

  | İstek | Cevap |
  |---|---|
  | `GET /api/projects/<proje>/muted` | `{"frames": […]}` |
  | `PUT /api/projects/<proje>/frames/<kare>/muted`, gövde `{"muted": true\|false}` | `{"frames": […]}`, yeni liste |
  | geçersiz değer | 400 |
  | kapatmada sesi olmayan kare | 400 |
  | olmayan proje | 404 `{"error": "Proje yok: <proje>"}` |
  | okunamayan dosya | 503 (`OSError`, `web/app.py`'nin tek işleyicisi) |

  PUT bir durumu söyler, tersine çevirmez: iki kez gelen aynı istek aynı sonucu bırakır. URL'deki kare
  kimliği yola dönüşmez, yalnız JSON'a yazılır; kapatmada kayıtta sesi olan bir kare olmalıdır.
- **`run_export`:**
  - `start_export` ve `run_export` yeni bir isimli argüman alır, `mutes` (zorunlu: unutulan bağlantı
    sessizce "hiçbiri kapalı değil" olmasın).
  - Liste bir kez, export'un klasörü açılmadan önce okunur. Okunamazsa geride temizlenecek bir şey
    kalmaz.
  - `silenced` olan karenin videosu `exporter.silent(video, hedef)` ile kesilir: görüntü kopyalanır,
    ses hiç alınmaz (`-c copy -an`). Öteki kareler bugünkü gibi `exporter.piece` ile.
  - Ayrı export'ta parça sessiz bir video olur. Birleşik export'ta öteki sesi olmayan parçalar gibi
    `_evened_out` ona sessizlik yazar, bu yüzden birleşmenin sesi kaymaz.
- **`export_summary`:**
  - O da `mutes` alır ve `muted` sayısını ekler: videosu export'a girecek ve `silenced` olan kareler.
  - `silent` aynı şeyi sayar (sesi olmayanlar), artık `holds_sound`'la. İki sayı ayrık: kapatılan
    sesi olan bir kare `silent`'e girmez.
- **`main.py`:**
  - `_mutes = DriveMuteStore(_storage)`;
  - `start_export` ve `export_summary`'ye `mutes=_mutes`;
  - kapı `get_muted` ve `set_muted` ile bağlanıp blueprint listesine eklenir.

### Ekran

- **`shared/api.js`:**
  - `getMuted(project)` → kimlik listesi;
  - `saveMuted(project, frame, muted)` → yeni liste.
- **`features/photo_generation/useMuted.js`, `useMuted(project)`:** `{ muted, mute }` döner.
  - `muted` sunucudan okunan liste; okunana kadar ya da okunamazsa `null`.
  - `mute(frame, on)` listeyi hemen değiştirir, sonra yazar.
  - Her cevap yalnız kendi karesi için konuşur: o karenin listede olup olmadığı cevaptan alınır,
    öteki kareler olduğu gibi kalır. O kareye sonradan bir basış daha yapıldıysa cevap hiç
    uygulanmaz.
  - Neden kare başına: kare 1'de basılır, okla kare 2'ye geçilir, orada basılır, ve sunucu önce kare
    2'yi yazar. Kare 2'nin cevabı kare 1'i henüz bilmez. Bütün liste olarak alınsaydı kare 1 ekranda
    açık görünürdü, sunucuda kapalıyken.
  - Reddedilen basış yalnız kendi karesini basıştan önceki haline döndürür ve söz `mute`'un reddiyle
    çağırana gider, başka karede basılmış olsa da. Aynı karede sonraki bir basışın geçersiz kıldığı
    basış hiçbir şey söylemez.
- **`LayerPlayer`:** iki yeni prop.
  - `silent`: videoyu ve wav'ı susturur (`muted`). Wav ve dalga çizgisi yerinde kalır, ses projede
    durur.
  - `onMute`: verilirse oynatıcının sağ üstünde bir ikon düğmesi çıkar, oynat düğmesinin koyu
    zemininde.
    - Açıkken hoparlör, adı **Sesi kapat**; kapalıyken üstü çizili hoparlör, adı **Sesi aç**.
    - Basış sahnenin oynat/duraklat tıklamasına geçmez.
    - Çizimler `glyphs.jsx`'te: `SpeakerGlyph`, `SpeakerOffGlyph`.
- **`PhotoDetail`:**
  - Karenin sesi varsa (katmanlarında ses, kırmızı değil) ve liste okunduysa oynatıcıya `onMute`
    verilir. Video ve Ses sekmelerinin ikisinde de, çünkü ikisi de aynı videoyu oynatıyor.
  - `silent` listeden okunur. İkisi de `silenced`'ın kuralının ekrandaki önizlemesidir: kararı
    export'ta sunucu verir.
  - Basış reddedilirse yan sütunda öteki retlerin kartı çıkar: başlık **Ses kapatılamadı** ya da **Ses
    açılamadı**, altında sunucunun sözü. Kart başka kareye geçince gider.
- **`ExportScreen`:** *⚠ N videonun sesi kapalı*, `summary.muted` sıfırdan büyükse, "sesi yok"
  satırının hemen altında.

## Maliyet

Her biri proje, sohbet ve dosya sayısından bağımsız, O(1):

| İş | Ne yapar |
|---|---|
| Kare sayfasının açılışı | bir `GET`, bir okuma. Oklarla kareden kareye geçmek istek açmaz: sayfa takılı kalır, liste onunla. |
| İkona basış | bir `PUT`. Sunucuda: projenin var olduğuna bir bakış, kapatmada kaydın `slots`'u (`FileCache`'le, değişmediyse yalnız bir damga sorgusu), `muted.json`'u bir okuma ve bir yazma (Storage'ın bağlantı ve yer bakışıyla). Geri okuma yok. |
| Export | `muted.json`'u bir kez okur. |
| Export özeti | `muted.json`'u bir kez okur. |
| Galerinin 2 sn'lik sorgusu (`list_frames`) | değişmez: listeyi okumaz. |

## Ne kaybolabilir, ne bozulabilir

- **Ses silinmez:** dosyaya ve kayıt satırına dokunulmaz. Açınca geri gelir.
- **Yazma bütün ya da yok:** Storage'ın geçici dosyası ve `os.replace`'i. Çöken bir yazma eski listeyi
  bırakır.
- **Okunamayan dosya** üstüne yazılmaz ve export'u sesli çıkarmaz: hata, işletim sisteminin ya da
  ayrıştırıcının sözüyle ekrana gelir.
- **Aynı anda iki basış:** store'un kilidi oku-değiştir-yaz'ı sıraya koyar. Ekranda her cevap yalnız
  kendi karesini, ve yalnız o karenin son basışıysa değiştirir.
- Kapatma isteği export sürerken gelirse o export listeyi başta okumuştur. Değişiklik bir sonraki
  export'a girer.
- Hata metni bir sır taşımaz: dosya yolu ve ayrıştırıcının sözü.

## Sınırlar

- Galerinin kartları değişmez; ikon yalnız kare sayfasında.
- Kopyala ile doğan ikiz, kaynağının sesi kapalı olsa da açık başlar: kapatılan, o karenin sesi.
- Ses silinip aynı kareye yeniden üretilirse kapalı kalır; ikon bunu gösterir.
- Liste okunana kadar (kare sayfasının açılışında bir istek süresi) ikon çizilmez ve oynatıcı sesli
  başlar. Video kendiliğinden oynamaz, Oynat'a basılınca başlar.
- `muted.json` okunamazsa kare sayfasında ikon çizilmez. Export ve özeti de hatayla durur: dosya elle
  düzeltilmeli.
- Galerinin seçim çubuğu sesi kapatmaz; madde tek tek videoyu istiyor.
- Basışın reddi, cevap gelmeden oklarla başka kareye geçildiyse kartını o karede gösterir. Sayfanın
  öteki retleri de (Yeniden üret, katmanı sil) böyle. Düzeltmesi
  [BACKLOG](../../queen-editor/BACKLOG.md)'de: *"Kare sayfasında geç gelen bir ret başka karede
  görünüyor"*.

## Ne zaman bitti

- **Store:**
  - dosya yoksa `[]`;
  - `put` ekliyor, çıkarıyor, aynı durumu yeniden yazmıyor;
  - okunamayan ya da şekli bozuk dosyada `read` ve `put` `OSError` veriyor ve dosya olduğu gibi kalıyor;
  - aynı anda iki `put` ikisini de bırakıyor.
- **Kapı:**
  - `GET` başta `{"frames": []}`;
  - sesi olan karede `PUT true` listeye ekliyor ve yeni listeyi dönüyor; yeni bir istemci aynısını
    okuyor;
  - `PUT false` çıkarıyor, sesi olmayan karede de;
  - sesi olmayan ya da sesi kırmızı karede `PUT true` 400 ve dosya yazılmıyor;
  - `true`/`false` dışı değer 400;
  - olmayan proje 404.
- **Export:**
  - kapalı karenin parçası `silent`'le kesiliyor, ötekiler sesleriyle `piece`'le;
  - listede olup sesi olmayan kare bugünkü gibi `piece(video, None, …)`;
  - birleşik export'ta sessiz parça yerinde;
  - liste export başına bir kez okunuyor;
  - `FfmpegVideoExporter.silent` görüntüyü kopyalayıp sesi atan komutu çalıştırıyor.
- **Özet:** `muted` kapalı ve sesi olan videoları sayıyor; `silent` onları saymıyor.
- **`main.py`:** export ve özet `_mutes`'u alıyor; `GET /api/projects/<yok>/muted` 404.
- **Ekran:**
  - sesi olan karede Video ve Ses sekmelerinde **Sesi kapat** düğmesi var; sesi olmayan ya da sesi
    kırmızı karede yok;
  - basınca `saveMuted(proje, kare, true)` gidiyor, düğme **Sesi aç** oluyor, video ve wav susuyor;
  - yeniden basınca `false` gidiyor ve ses geri geliyor;
  - açılışta liste okunur, kapalı kare sessiz ve **Sesi aç** ile açılır;
  - reddedilen basışta düğme eski haline dönüyor ve **Ses kapatılamadı** kartı sunucunun sözüyle
    çıkıyor;
  - iki karede arka arkaya basılıp sunucu önce ikinciyi yazınca ikisi de kapalı kalıyor; birincinin
    reddi yalnız birinciyi geri alıyor ve söyleniyor;
  - düğmeye basmak videoyu oynatmıyor;
  - export ekranında *⚠ 2 videonun sesi kapalı*, sıfırda satır yok.

## Yalnız Colab'da görülecek

- Gerçek bir H3 + MMAudio videosunun sesi kapatılınca kare sayfasında sessiz oynaması.
- Ayrı ve birleşik export'ta o videonun sessiz, ötekilerin sesli çıkması.
- Colab'ı kapatıp açınca sesin hâlâ kapalı olması.
