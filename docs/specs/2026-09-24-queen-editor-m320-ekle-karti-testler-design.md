# Madde 320 — Ekleme: sıranın kendi `Ekle` kartı, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.**

## Bugün ne oluyor

319'un kartları yalnız görünüyor; yükleme hâlâ sıraların altındaki ortak `Ekle`'den: üç tip için tek
seçici, birden çok dosya, her dosya kendi tipinin sonuna. Ret kırmızı kartı havuzun en altında.

## Kurallar

1. **Kart yalnız kendi tipinin seçicisini açıyor** *(`image/*`, `video/*`, `audio/*`)*, **tek dosya**
   alıyor. Seçicinin adı tipin sözcüğüyle: `fotoğraf ekle`, `video ekle`, `ses ekle`.
2. **Yükleme sıranın tipiyle gidiyor**, ve **tip kuralı sunucuda** *(FOUNDATION 4)*: başka tipte bir
   dosya o sıraya reddediliyor, yeni cümleyle — `<ad> <sıranın tipi> yuvasına giremez — bu dosya
   <dosyanın tipi>.` *(tasarımın örneği: `kisa-2.wav fotoğraf yuvasına giremez — bu dosya ses.`)*.
   Hiçbir şey yazılmıyor. Sıranın tipi verilmezse bugünkü gibi — her dosya kendi tipine.
3. **Sıra, tasarımın sırası:** tanınmayan dosya → yanlış sıra → süresi okunamayan → sınırlar.
4. **Yüklenirken o kart dönen işaretle `Yükleniyor…` diyor, ve hiçbir kart basılmıyor.**
5. **Ret havuzun tepesinde**, sıraların üstünde; sonraki seçim onu temizliyor. *(Silme bugün de
   temizliyor.)*
6. **Ortak `Ekle` gidiyor.**

## Yazılacak testler

### `backend/tests/test_reference_usecases.py`

1. **Başka tipte dosya seçildiği sıraya reddediliyor** — `kisa-2.wav` fotoğraf sırasına: tam cümle;
   havuza hiçbir şey yazılmıyor.
2. **Kendi tipindeki dosya sırasına giriyor.**

### `backend/tests/test_reference_routes.py`

3. **Kapı sıranın tipini formdan okuyor** — `kind=picture` ile `kisa-2.wav`: 400, tam cümle.

### `frontend/src/shared/api.test.js`

4. **Yükleme sıranın tipini formla gönderiyor** — `kind` alanı.

### `ReferencePanel.test.jsx` — yeni blok *"adding from a row's card"*

5. **Her kart yalnız kendi tipini, tek dosya seçtiriyor** — üç seçicinin `accept`'i, hiçbirinde
   `multiple` yok.
6. **Yükleme sıranın tipiyle gidiyor** — fotoğraf kartından `uploadReferences("düğün", [dosya],
   "picture")`.
7. **Yoldaki kart `Yükleniyor…` diyor ve hiçbir kart basılmıyor** — üç seçici de kapalı.
8. **Ret havuzun tepesinde, ve sonraki seçim onu temizliyor.**
9. **Ortak `Ekle` yok.**

**Değişen:** `ReferencePanel.test.jsx` — `pick` yardımcısı hangi karttan seçildiğini alıyor
*(varsayılan `fotoğraf ekle`)*; `sends the files that were picked, and draws what comes back` tek
dosyayı fotoğraf kartından seçip tipiyle bekliyor; `shows the server's own refusal` klibi video
kartından seçiyor. Sunucu testleri `add_references`'ı `row=` ile doğrudan çağırıyor — ortak `added`
yardımcısı dokunulmadan kalıyor, yoksa bu turda bilinmeyen argüman o yardımcıyı kullanan her testi
düşürürdü.

**Bekçiler:** `test_a_file_nobody_can_read_is_refused`, sınır testleri, süresi okunamayan klip —
sıranın tipi verilmediğinde bugünkü davranış.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest'te 1–3, vitest'te 4–9 ve değişen iki ekran testi
kırmızı; `queen-agent` satırları yeşil.
