# Madde 421 — Queen AI'ın H3 metninde uzunluk yok, uygulama turu

**Koşu:** Queen Editor v9 — `roadmaps/2026-10-05-queen-editor-v9-roadmap.md` · **Dal:**
`feat/queen-editor-v9` · **Parça:** 421 · v9-1a · **Tur:** 2/2 — kod.
**Üstüne kurulduğu:** [m421 test turu](2026-10-06-queen-editor-m421-h3-uzunluk-yok-testler-design.md).
**Commit'lenmez:** 422'yle birlikte kullanıcının Changes'inde okunur, ve onayıyla commit'lenir.

## Ne değişir

Yalnız [prompt_writer.py](../../../queen-editor/backend/features/photo_generation/data/prompt_writer.py):

1. **`H3_VIDEO_INSTRUCTION`'da iki yer** — uzunluk düşer, kelimelerin geri kalanı aynen:
   - `- H3 makes a video of four seconds, with sound, from a photo.` →
     `- H3 makes a video, with sound, from a photo.`
   - `… from the first frame to the end of the video. Write only what fits in four seconds.` →
     `… from the first frame to the end of the video.`
2. **`LOOP_RULE`'un üstündeki yorum** — *"which reads as a pulse every four seconds"* diyor. 422'den
   sonra H3 videosu 4, 8 ya da 12 saniye, WAN'ınki 5: yorum artık doğru değil. *"which reads as a
   pulse each time the clip starts again"* olur. Kural metninin kendisi değişmez (uzunluk
   söylemiyor).

Başka hiçbir şey değişmez: WAN'ın ve sesin metni, `LOOP_RULE`, `LINKED_RULE`, suffix, yazarlar,
`H3_VIDEO_INSTRUCTION`'ın üstündeki yorum (uzunluktan söz etmiyor).

## Neden böyle

- Kullanıcı uzunluğun metinde hiç geçmemesini istedi *(v9-1 — "videoda uzunluk belirtemyelim")*, ve
  videonun uzunluğunu artık projenin seçimi belirliyor *(422)*: metin uzunluk söyleseydi, 8 ya da 12
  saniyelik bir videoda yanlış olurdu.
- *Write only what fits …* cümlesinin yerine bir şey konmaz: *"from the first frame to the end of the
  video"* hangi uzunlukta olursa olsun doğru, ve kullanıcı *"kritik bir bilgi değil"* dedi.

## Doğrulama

Dört satır. Test turunun iki kırmızısı yeşile döner; `test_video_prompt_writer.py`'nin öteki
testleri (cümleleri tek tek tutanlar) aynen yeşil; öteki her şey yeşil.
