# Madde 515 · Ses düğmesi her videoda — tasarım

**Tarih:** 29 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-14),
515 · v11-14 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Plan:**
[2026-10-29-queen-editor-m515-ses-dugmesi-her-videoda-plan.md](../plans/2026-10-29-queen-editor-m515-ses-dugmesi-her-videoda-plan.md)
· **Kurallar:** queen-editor [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md) · **Üstüne kurulduğu:** 510
([spec](2026-10-29-queen-editor-m510-ses-kapatma-design.md))

## Kabul koşulu (maddeden)

Kare sayfasında 510'un ses düğmesi, MMAudio sesi olsun olmasın her videoda var. Basınca video kare
sayfasında sessiz oynuyor ve export'ta tamamen sessiz çıkıyor: H3'ün kendi sesi de, varsa eski MMAudio
sesi de girmiyor. Bir daha basınca ikisi de geri geliyor.

Kullanıcı, 29 Ekim — düğme her videoda çıksın ve H3'ün kendi sesini kapatsın mı sorusuna: *"evet
lütfen"*. Kullanıcının ilk mesajındaki "m3" büyük ihtimalle H3'tü; 510 onu MMAudio sanılarak kuruldu, ve
514'ten sonra düğme yeni hiçbir videoda çıkmazdı.

510'un geri kalanı değişmez: `muted.json` ve store'u, kapının istekleri ve cevapları, açmanın her zaman
kabul edilmesi, `exporter.silent` (`-c copy -an`), kare sayfasında hemen değişen düğme ve reddin kartı,
export ekranının *"⚠ N videonun sesi kapalı"* satırı. 511–514'e dokunulmaz. Ekrandaki sürüm V11 kalır.

## Bugün

"Ne kapatılabilir" sorusunun cevabı 510'da "MMAudio sesi olan, kırmızı olmayan kare":

- **Sunucu** (`domain/mute.py`): `holds_sound(frame)` galeri satırından, `require_sound(slots, frame)`
  kaydın ses hücresinden sorar. `silenced(frame, muted)` = `holds_sound` ve kimlik listede.
  - Export (`run_export._write`) `silenced` karede `exporter.silent`, öteki karede `exporter.piece`.
  - Özet (`export_summary`) `muted`'ı `silenced` ile sayar.
  - Basış (`usecases/mute.set_muted`) kapatmada `require_sound` ister; yoksa 400 *"Bu karenin sesi
    yok: <kare>"*.
- **Ekran** (`PhotoDetail`): `sounded` (katmanlarda ses, kırmızı değil) düğmeyi verir; `silent` =
  `sounded` ve kimlik listede.

Yani H3'ün kendi sesiyle gelen, MMAudio sesi olmayan bir videoda düğme yok, ve listede kimliği olsa
bile export onu sesli çıkarır.

## Ne yapılır

Kural: **videosu inmiş kare kapatılabilir** — galeri satırında `layers.video` var ve `failed`'da
`video` yok; kayıtta o karenin video hücresinin son satırı `done`. Ses katmanı artık sorulmaz.

### Sunucu

- **`domain/mute.py`** — kuralın sunucudaki tek yeri:
  - `require_video(slots, frame)`: kaydın o karedeki video hücresinin son satırı `done` değilse
    `NoVideo("Bu karenin videosu yok: <kare>")`. `require_sound`'un yerine.
  - `NoVideo`, `NoSound`'un yerine.
  - `holds_sound` ve `silenced` çıkar. Galeri satırından "videosu inmiş mi" sorusunu export zaten
    soruyor: `export_summary.exportable` yalnız videosu inmiş kareleri verir, ve export ile özet yalnız
    onları okur. Onların içinde "sesi kapalı mı" yalnız `frame["id"] in muted`. İkinci bir
    "videosu var mı" sorusu aynı cevabın ikinci kopyası olurdu.
  - `check`, `InvalidMute` değişmez.
- **`usecases/mute.set_muted`**: kapatmada `mute.require_video(record.slots(project), frame)`. Sırası,
  açmanın her zaman kabulü ve hiçbir şey yazmadan ret aynı.
- **`presentation/mute_routes.py`**: `NoSound` yerine `NoVideo`, yine 400.
- **`run_export`**:
  - `_write`: `frame["id"] in muted` ise `exporter.silent`, değilse `exporter.piece`. Ses katmanı olmayan
    işaretli kare de artık `silent`'le kesilir: H3'ün kendi sesi girmez.
  - `_audio_of`: "videonun üstüne hangi ses konur" sorusu export'un kendi sorusu; `holds_sound`'un tek
    okuyucusu kalmıştı, kontrol 510'dan önceki gibi `_audio_of`'un içine döner (katmanlarda ses var ve
    kırmızı değil). Davranışı aynı.
- **`export_summary`**: `muted` = `exportable` karelerden kimliği listede olanlar. Ses katmanı sorulmaz.

### Ekran

- **`PhotoDetail`**: `sounded` yerine `landed` = `stateOf("video") === "done"` — sayfanın her katman için
  zaten kullandığı kural, sunucununkiyle aynı (`layers.video` var, kırmızı değil, sırada değil). Kuralın
  ekrandaki tek önizlemesi; `silent` = `landed` ve kimlik listede, `onMute` = `landed` ve liste okundu.
  Video ve Ses sekmelerinin ikisinde de, 510'daki gibi.
- **`LayerPlayer`**, **`useMuted`**, **`ExportScreen`** değişmez. `LayerPlayer` sesi olmayan videoyu da
  `silent` ile zaten susturuyor (`muted={Boolean(audioUrl) || silent}`); yalnız yorumu "sesi olan"
  yerine "kapatılabilen" der.

## Maliyet

Her biri proje, sohbet ve dosya sayısından bağımsız, 510'la aynı; yeni istek, okuma ya da yazma yok:

| İş | Ne yapar |
|---|---|
| Kare sayfasının açılışı | bir `GET`, bir okuma (`muted.json`). Kareden kareye geçmek istek açmaz. |
| Düğmeye basış | bir `PUT`: projeye bir bakış, kapatmada kaydın `slots`'u (`FileCache`'le, değişmediyse yalnız bir damga sorgusu), `muted.json`'u bir okuma ve bir yazma. Geri okuma yok. |
| Export | `muted.json`'u bir kez okur. Kare başına ek bir şey yok: üyelik bellekte bakılır. |
| Export özeti | `muted.json`'u bir kez okur. |

## Ne kaybolabilir, ne bozulabilir

- Ses dosyalarına ve kayıt satırlarına dokunulmaz. Açınca H3'ün sesi de eski MMAudio sesi de geri gelir.
- `muted.json`'un yazılışı, okunamayan dosyanın boş sayılmaması ve iki basışın kilidi 510'un store'u;
  değişmez.
- **510'dan kalmış işaret:** 510'un kuralında ses katmanı olmayan karede işaret sayılmıyordu. Böyle bir
  işaret (ses silinmiş, kimlik listede kalmış) artık sayılır: video sessiz oynar ve sessiz çıkar. Düğme
  **Sesi aç** olarak görünür ve export ekranı onu *"sesi kapalı"* satırında sayar; kullanıcı görür ve
  tek basışla açar.

## Sınırlar

- İşaret karenin kimliğiyle durur (510). Video silinip aynı kareye yeniden üretilirse yeni video
  kapalı başlar; düğme bunu **Sesi aç** olarak gösterir. Silme işareti kaldırmaz: silme yolu bu maddede
  değişmiyor.
- Videosu kırmızı ya da sırada olan karede düğme yok ve kapatma reddedilir; açma her zaman kabul.
- Kopyala ile doğan ikiz açık başlar (510).
- Galerinin kartları ve seçim çubuğu değişmez.

## Ne zaman bitti

- **Kapı:**
  - ses katmanı olmayan, videosu inmiş karede `PUT true` 200 ve listede;
  - eski sesi olan karede de 200;
  - videosu olmayan karede ve videosu kırmızı karede `PUT true` 400 *"Bu karenin videosu yok: <kare>"*,
    dosya yazılmıyor;
  - `PUT false` her durumda kabul (510).
- **Export:**
  - ses katmanı olmayan işaretli video `silent`'le kesiliyor;
  - eski sesi olan işaretli video da `silent`'le;
  - işaretsiz videolar bugünkü gibi `piece`'le, sesleri ya da `None` ile.
- **Özet:** `muted`, ses katmanı olmayan işaretli videoyu sayıyor; videosu inmemiş karedeki işareti
  saymıyor.
- **Ekran:**
  - ses katmanı olmayan videonun Video sekmesinde **Sesi kapat** var; basınca `saveMuted(proje, kare,
    true)`, düğme **Sesi aç**, video susuyor; yeniden basınca `false`;
  - eski sesi kırmızı olan videoda da düğme var;
  - eski sesi olan karede Video ve Ses sekmelerinde düğme, 510'daki gibi;
  - videosu kırmızı karede düğme yok;
  - açılışta listede olan sessiz video kapalı başlar.
- `dist` yeniden derlendi; iki queen-editor takımı yeşil.

## Yalnız Colab'da görülecek

- Gerçek bir H3 videosunun (MMAudio sesi olmadan) sesi kapatılınca kare sayfasında sessiz oynaması.
- Ayrı ve birleşik export'ta o videonun sessiz, ötekilerin H3 sesiyle çıkması.
