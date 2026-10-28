# Madde 397 — Kutu QueenAgent'ın yeni listesini okur, uygulama turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 1 · **Parça:** 397 · v8-3a · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m397 test turu](2026-09-30-queen-editor-m397-yeni-liste-testler-design.md), `51e05cae`.

## Senaryo nerede duruyor

**Planın fotoğraf satırında** — listenin açtığı her varyantın satırında `scene` alanı. Plan
*"hangi kareler, hangi prompt'la istendi"* sorusunun cevabı *(CODE-STANDARD, Separation of
concerns)*, ve senaryo kareyle aynı anda, aynı basışla isteniyor. Yeni dosya yok, `DrivePlanStore`
değişmiyor: satırı `{**frame}` ile okuyup olduğu gibi yazıyor.

**Kart senaryosunu prompt'unun numarasıyla buluyor.** Karenin adı prompt'unun numarasını taşıyor
*(`photo_name`)*, ve aynı resmi taşıyan her kart o numarada: videonun varyantı `P0_1`, *Kopyala*'nın
ikizi `C1_P0_0` — `photo_name._parts`'ın kendi kuralı, *"a twin holds its source's picture, so it
belongs to the family of the prompt that made that picture"*. Fotoğrafı silinip videosu kalan kartın
adı da değişmiyor. `list_frames` planın satırlarından bir kez `{numara: senaryo}` çıkarıyor, ve her
kart `scene`'ini oradan alıyor; senaryosu olmayan numarada boş metin.

**Seçilmeyen iki yol.**

- *Satırı olduğu gibi geçirmek* *(kart zaten `{**base}` ile planın satırını taşıyor)*: kopya karenin
  açılışı ya bir video satırı ya bir kayıt satırı — ikisinde de senaryo yok; fotoğrafı silinen kartın
  açılışı da video satırına ya da kayda kayıyor. Dört testten dördü kırmızı kalırdı.
- *Senaryoyu her kopyanın satırına yazmak* *(`copy_frame._carry`, `queue_layer._job`,
  `regenerate`)*: dört yazıcı, ve kayıt satırı planın cevabını tekrarlardı — CODE-STANDARD'ın *"No
  file repeats another's answer"* kuralı.

**Tek istisna: yeni kelimelerle yeniden üretim.** Yeni kelimeler yeni bir numara açıyor
*(`regenerate`, madde 99)*; o numarada senaryo yok. Bu yüzden `regenerate`'in yazdığı satır,
kaynağın senaryosu varsa onu taşıyor — yeni ailenin ilk satırı onu söylüyor, ve numarayla bulma
kuralı değişmeden işliyor. Aynı kelimelerle yeniden üretimde de taşıyor: aynı numara, aynı metin;
iki dal yazmaktansa tek satır.

## Okuyucu — `prompt_list.py`

- **`parse_photo_list(text)`** → `[{"prompt": …}]` ya da `[{"prompt": …, "scene": …}]`. Bugünkü
  gövde: boş metin `Prompt listesi boş.`; `AD =` düşüyor; `ast.literal_eval`; liste ya da tuple
  değilse `Format hatası — liste okunamadı`. Sonra iki biçim:
  - hepsi metin → `{"prompt": öğe.strip()}`;
  - hepsi kayıt *(`dict`, `scene` ve `photo` ikisi de metin; fazla alan görmezden geliniyor)* →
    `{"prompt": photo.strip(), "scene": scene}`. Senaryo yazıldığı gibi kalıyor — QueenAgent de onu
    *"as it was written"* taşıyor;
  - başka her şey, karışık liste dahil → `Format hatası`.

  `prompt`'u boş girdi düşüyor *(nova-3dcg'nin "satırı kapat" sözleşmesi)*; hiçbiri kalmazsa
  `Prompt listesi boş.`.
- **`parse_prompts(text)`** → `list[str]`, Referanstan'ın kutusu. `parse_photo_list`'in okuduğunu
  alıyor, ve bir girdi senaryo taşıyorsa `Format hatası` diyor: o kutu video prompt'u istiyor,
  QueenAgent'ın `photo`'su fotoğraf etiketleri. Tek ayrıştırıcı, bir kural fazlası.
- Cümleler aynı iki sabit; yeni cümle yok.

## Plan — `start_batch.py`

- `start_batch` `parse_photo_list`'i çağırıyor.
- `plan_frames(start, entries, …)`: girdi satıra yayılıyor — `**entry` `"prompt"`'un yerinde.
  Düz listenin girdisinde yalnız `prompt` var, yani satır bugünkünün aynı; QueenAgent'ın girdisi
  `scene`'i her varyantın satırına ekliyor.

## Galeri — `list_frames.py`

- `scenes = {satır["number"]: satır["scene"] for satır in planned if satır.get("scene")}`.
- Kart: `"scene": scenes.get(number_of(fid), "")` — her kartta alan var; boş metin senaryosu yok
  demek. 401 bu alanı okuyor.

## Yeniden üretim — `regenerate.py`

Plana eklenen satıra `**({"scene": source["scene"]} if source["scene"] else {})`. Senaryosu olmayan
karenin satırı bugünkünün aynı.

## Değişmeyen

`queue_references.py` *(hâlâ `parse_prompts`)*, `copy_frame.py`, `queue_layer.py`, `DrivePlanStore`,
rotalar, ekran ve dist. Senaryoyu yazan bir kapı açılmıyor — yalnız okunur.

## Bitti sayılır

Dört test satırı yeşil; kod, spec ve plan tek commit.
