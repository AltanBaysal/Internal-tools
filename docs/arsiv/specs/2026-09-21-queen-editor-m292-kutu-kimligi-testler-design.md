# Madde 292 — Kutu kimliği, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, takım kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok. Madde 21 Eylül'de konuşuldu, kararları yol haritasının satırında.

## Ne değişiyor

**Bugün kart bir fotoğraf işidir.** Galeri planı okurken yalnız `photo` tipindeki işleri satır
sayıyor; öteki tipler o kartın katmanı sayılıyor ve satır açmıyor
*([list_frames.py:94-99](../../../queen-editor/backend/features/photo_generation/domain/usecases/list_frames.py#L94-L99))*.
Kartın **durumu** fotoğraf yuvasının durumu, **adı** da fotoğrafının adı. Sonucu: videoyla doğan bir
kart galeride hiç görünmez — plan onu tutar, ekran tutmaz.

**Olacak: kart, onu açan katmandan doğar.** Bir kimlik plana hangi işle girdiyse satırını o iş açar,
ve kartın durumu o katmandan okunur. Fotoğraf özel bir katman olmaktan çıkar; bugünkü kartlar
fotoğrafla açıldıkları için davranışları **hiç değişmez**.

**Kayıt katmanı zaten kutu.** Kaydın birimi `(kart, yuva)` çifti
*([layers.py](../../../queen-editor/backend/features/photo_generation/domain/layers.py))*, ve
`record.slots()` bunu öyle döndürüyor. Yani veri modeli değişmiyor; değişen şey galerinin
fotoğraf varsayımı.

## Kararlar

**1. Kartı açan iş, planda o kimlikle görünen ilk iştir.** Plan zaten yazıldığı sırada okunuyor ve
sırası koşma sırasının kendisi *(`queue.open_jobs`)*. İkinci bir alan — "bu kartı hangi katman açtı"
— yazmıyoruz: planın sırası zaten bunu söylüyor, ve aynı şeyi iki yerde tutmak ikisinin ayrılabildiği
gün demektir *(CODE-STANDARD, "No file repeats another's answer as a flag")*.

**2. `file` alanı bugünkü anlamını koruyor.** Kartın fotoğrafı varsa onun dosyası, yoksa kimliğin
verdiği ad *(`photo_file(fid)`)*. Bu alan ekranda seçimin ve sıranın anahtarı; kimliğin saf bir
fonksiyonu olduğu için fotoğrafsız kartta da bir ada sahip olur, ve seçim, sıralama, silme hiç
değişmez. **Kartın çizdiği resim bu maddenin işi değil:** fotoğraf yuvasını videonun ilk karesiyle
dolduran madde 296.

**3. Kartın galeriden düşme kuralı, bu turda açan katmana uygulanır.** Bugün silinmiş ya da kuyruktan
çekilmiş bir fotoğraf kartı galeriden düşürüyor; aynı kural artık kartı açan katmana bakar.
**Genelleştirilmesi 294'ün işi** — "son katman gidince kutu gider" kuralı orada yazılır. Bu madde
yalnız *hangi katmanın okunduğunu* değiştirir, kuralın kendisini değil.

**4. Planlanmış prompt, açan katmanın kendi anahtarına yazılır.** Bugün planın `prompt` alanı kartın
`prompts["photo"]`'suna düşüyor *(`_words`)*; videoyla açılan kartta aynı alan
`prompts["video"]`'ya düşer. Kayıttan gelen prompt'lar bugünkü gibi kalır.

**5. Planın bilmediği fotoğraflar bugünkü gibi galerinin.** İkinci döngü *(kayıtta olup planda
olmayan satırlar)* olduğu yerde kalıyor: planın kalıcı olmasından önceki projeler hâlâ okunuyor.

## Testler — bu turda yazılacaklar

Hepsi `backend/tests/test_photo_usecases.py`'ın galeri bölümüne, oradaki sahte port'larla. Ne ComfyUI
ne Drive ne GPU *(CODE-STANDARD, Tests)*.

1. **`test_a_frame_planned_only_as_video_is_in_the_gallery`** — planda yalnız `video` tipinde bir iş
   olan kimlik galeride bir satır olarak görünüyor.
2. **`test_a_video_born_frames_status_comes_from_its_video`** — o kartın videosu kayıtta `done` ise
   kartın durumu `done`; hiç satırı yoksa `pending`.
3. **`test_a_video_born_frame_keeps_its_name`** — fotoğrafı olmayan kartın `file` alanı kimliğinin
   verdiği ad, yani seçim ve sıralama çalışmaya devam ediyor.
4. **`test_a_frame_that_has_a_photo_job_still_opens_with_it`** — hem fotoğraf hem video işi olan kart
   bugünkü gibi fotoğrafıyla açılıyor: durumu fotoğrafından geliyor, ve videosu ikinci bir satır
   **açmıyor**.
5. **`test_a_video_born_frame_leaves_the_gallery_when_its_video_is_deleted`** — açan katman silinince
   kart galeriden düşüyor *(karar 3)*.
6. **`test_a_video_born_frames_planned_prompt_is_the_videos`** — planın prompt'u
   `prompts["video"]`'da *(karar 4)*.

Bugünkü galeri testlerinin hiçbiri değişmiyor; değişselerdi bu madde davranış değiştiriyor olurdu.

## Bitti sayılır — bu tur

Altı test yazılmış, takım koşulmuş ve **kırmızı görülmüş**, ve kırmızı hâliyle commit'lenmiş.
`skip`/`xfail` yok. Dört test satırı da koşulur: iki Python, iki npm — ötekilerin yeşil kalması
bu turun da şartı.
