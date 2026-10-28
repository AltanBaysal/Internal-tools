# Madde 292 — Kutu kimliği, implementasyon turunun planı

**Spec:** [m292 implementasyon turu](../specs/2026-09-21-queen-editor-m292-kutu-kimligi-uygulama-design.md)

Tek dosya: `backend/features/photo_generation/domain/usecases/list_frames.py`. Test dosyasına
dokunulmaz — turun testleri `6635f6d7`'de yazıldı.

## Adımlar

1. **`_words` açan katmanı öğrenir.** Üçüncü argüman `kind`, varsayılanı `layers.PHOTO`; planın
   prompt'u o anahtara yazılır.

2. **Açan iş çıkarılır.** `list_frames` içinde, galeri döngüsünden önce: plan sırasında yürünüp
   kimlik başına ilk iş bir sözlüğe konur.

3. **Döngünün filtresi değişir.** Bugünkü *"fotoğraf işi değilse atla"* yerine *"bu iş kartı açan iş
   değilse atla"* gelir — kimlik karşılaştırmasıyla (`is`), `_latest_per_frame`'in yaptığı gibi.

4. **Durum açan katmandan okunur.** `photo = cells.get(PHOTO)` satırı yerini `kind` üzerinden okunan
   hücreye bırakır; `file` ise fotoğraf hücresine bakmaya devam eder, yani o satır kalır.

5. **Modül açıklaması düzeltilir.** *"Yalnız fotoğraf yuvası bir karenin burada olup olmadığına karar
   verir"* cümlesi kutu kuralıyla değişir.

6. **Dört test satırı koşulur**, ve `queen-editor` yeşile döner.

## Beklenen yeşil

Turun beş testi geçer; `test_a_frame_that_has_a_photo_job_still_opens_with_it` ve bugünkü galeri
testlerinin hepsi geçmeye devam eder. Düşen tek bir test bile bu maddenin davranış değiştirdiği
anlamına gelir — o zaman kod değil, kural gözden geçirilir.

## Bu turda yapılmayacaklar

- Silme kuralının genelleştirilmesi *(294)*, fotoğrafsız kartın ekranda çizilmesi *(296)*.
- Frontend'e hiç dokunulmuyor: bu madde domain'de başlıyor ve bitiyor.
