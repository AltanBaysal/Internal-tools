# Madde 421 — Queen AI'ın H3 metninde uzunluk yok, test turu

**Koşu:** Queen Editor v9 — `roadmaps/2026-10-05-queen-editor-v9-roadmap.md` · **Dal:**
`feat/queen-editor-v9` · **Parça:** 421 · v9-1a · **Tur:** 1/2 — yalnız testler.
**Commit'lenmez:** çıktıyı değiştirdiği için 422'yle birlikte kullanıcının VS Code'daki Changes'inde
okunur, ve onayıyla commit'lenir *(yol haritası, Dalga 5)*.

**Kullanıcıdan gereken — yok.** Madde 5 Ekim'de hizalandı; kararı yol haritasının *Maddelerin
kararları → v9-1* bölümünde, kullanıcının sözleriyle.

## Kullanıcının sözü

*"bence videoda uzunluk belirtemyelim h3 te olur mu bu kritik bir bilg idğeil gerekirse geri
getirirz"* *(5 Ekim)*. Videonun uzunluğunu yalnız projenin seçimi belirler *(422)*.

## Bugün ne oluyor

[prompt_writer.py](../../queen-editor/backend/features/photo_generation/data/prompt_writer.py)'nin
`H3_VIDEO_INSTRUCTION`'ı uzunluğu iki yerde söylüyor:

- *Context*'te: `- H3 makes a video of four seconds, with sound, from a photo.`
- *Rules*'ta: `… from the first frame to the end of the video. Write only what fits in four seconds.`

## Kurallar

1. **H3 metni hiçbir uzunluk söylemez** — hangi modda sorulursa sorulsun (düz, loop, bağlı): Queen
   AI'a giden sistem mesajında sayıyla söylenmiş bir saniye yok (*four seconds*, *8 seconds*,
   *four-second* …), ve *seconds* sözü hiç yok. Mesajın bütünü sınanır — talimat, modun kuralı ve
   suffix —, ki uzunluk hiçbir parçadan geri gelemesin.
2. **Başka bir şey değişmez:** iki cümle uzunluğu bırakır, geri kalanı aynen durur:
   - `- H3 makes a video, with sound, from a photo.` — yalnız *of four seconds* düşer;
   - `- Then write what moves and how, in order, from the first frame to the end of the video.` —
     satır burada biter; *Write only what fits in four seconds.* düşer, yerine bir şey gelmez.

   Metnin öteki cümlelerini bugünkü testler zaten tutuyor, ve aynen yeşil kalırlar.

**Değişmeyen:** WAN'ın metni, sesin metni, `LOOP_RULE`, `LINKED_RULE`, suffix, yazarların imzası ve
Queen AI'a ne gösterdikleri; grafik ve üretilen video *(uzunluk 422'de)*.

**İki türlü okunabilen yer, ve seçilen:** *"one to four sentences"* (ses manzarasının cümle sayısı) bir
uzunluk değil, ve kalır. Test bu yüzden *four* sözünü değil, saniye söyleyen sayıyı yakalar. *"the
second photo"* (`LINKED_RULE`) sıra sözü, ve sayıyla gelmediği için yakalanmaz.

## Yazılacak testler

### `backend/tests/test_video_prompt_writer.py` — H3 testlerinin arasına, `_h3()`'ten sonra

Sabit: saniye söyleyen bir uzunluğu yakalayan desen — rakamla ya da İngilizce sayı sözüyle (*one* …
*twelve*) yazılmış bir sayı, ardından boşluk ya da tire, ardından *second* / *seconds* / *sec* /
*secs*; ya da tek başına *seconds* sözü. Büyük-küçük harfe bakmaz.

1. **H3 metni hiçbir modda uzunluk söylemez** — üç mod (`standard`, `loop`, `linked`) için yazar
   bir kez sorulur, ve her sistem mesajında desen bir şey bulamaz. Bulursa ne bulduğunu söyler.
2. **Uzunluk düşen iki cümlenin geri kalanı yerinde** — talimatta
   `- H3 makes a video, with sound, from a photo.\n` ve
   `from the first frame to the end of the video.\n` birebir var.

## Kırmızı beklenen

- 1: desen *four seconds*'ı iki yerde bulur (üç modda da).
- 2: `- H3 makes a video, with sound, from a photo.` bugün yok; *end of the video.* satırı bugün
  *Write only …* ile sürüyor.
- Öteki her şey yeşil.

## Bilinçli olarak yapılmayan

- Uzunluğun kendisi, projenin ayarı ve grafik — 422; export'un toplamı — 423; ekran — 424.
- WAN'ın metni: uzunluk söylemiyor, ve WAN değişmez.
- Metnin tamamını bir kopyayla tutmak: öteki cümleleri bugünkü testler tek tek tutuyor; bütün bir
  kopya metnin her düzeltmesinde ikinci bir yeri değiştirtirdi.
