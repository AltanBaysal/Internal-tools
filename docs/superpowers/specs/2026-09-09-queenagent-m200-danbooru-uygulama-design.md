# Madde 200 · uygulama turu — etiketler Danbooru sözlüğüyle

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 200, ve
[test turu](2026-09-09-queenagent-m200-danbooru-testler-design.md) — 6 kırmızı.

---

## Metnin biçimi, ve `superpowers:writing-skills`'in bu metne söylediği

Rehberin *"Match the Form to the Failure"* bölümü doğrudan buraya oturuyor. Buradaki hata **kuralı
çiğnemek değil, çıktının şekli**: model etiket yerine tarif yazıyor. O tür bir hata için yasak
listesi ölçülmüş biçimde **geri tepiyor** — rakip bir dürtü varken model *"bunu yazma"* ile pazarlık
ediyor. Karşılığı **pozitif tarif**: etiketin ne olduğunu söyle, ne olmadığını değil.

Bu yüzden yeni ilk paragraf *"cümle yazma"* diye açılmıyor; **bir etiket nedir** diye açılıyor, ve
örneği tam da o şekilde veriyor. *"Nuance clause"* yok: istisna yazılmıyor, çünkü bir istisna
pazarlığı yeniden açıyor.

Yasak cümleler *(kalite etiketi yok, `or` yok)* yerinde kalıyor — onlar şekil değil **disiplin**
hatası, ve rehber orada yasağın doğru biçim olduğunu söylüyor.

## Ne yazılacak

### `SDXL_PROMPT_RULES`'un ilk paragrafı

Bugün *"kısa, virgülle ayrılmış parçalar"* diyen paragraf, sözlüğü adıyla anan bir tarife dönüyor:
etiket, **Danbooru'nun sahip olduğu etiket**; boşlukla yazılır; her biri **tek şey** taşır ve
sözlüğün böldüğü gibi bölünür; sözlükte karşılığı olmayan şey aynı şekilde birkaç düz kelimeyle
yazılır. Örnek de atomik: `looking at viewer, sitting, couch, window`.

Yoğunluk cümlesi *(bir artikel etiket değildir)* kalıyor — bugünkü nöbetçi onu adıyla tutuyor, ve
zayıf modelin ilk kaybettiği şey o.

### İki örnek metin

- `ADD_CHARACTER_TAGS`: `1girl, mature female, long hair, black hair, green eyes, narrow waist`.
- `ADD_LOCATION_TAGS`: `bedroom, indoors, curtains, sunlight, window`.

### `ADD_OUTFIT_TAGS` neden değişmiyor

Bugün `white nightgown, lace trim, bare shoulders` yazıyor, ve bu zaten o sözlüğün yazımı — sitede
giysi etiketleri tam olarak **renk + parça** *(`white dress`, `white shirt`)* biçiminde. Yol
haritasının *"üç metin"* dediği yerde iki metin değişiyor, ve sebebi bu: değiştirilecek bir şey
yok. Doğru olan metni sırf listede sayıldığı için ellemek, kaydı doğru tutmak için metni bozmaktır.

### Modülün yorumu

Sözlüğün **neden** o sözlük olduğu koda bakarak görülmüyor: anime SDXL checkpoint'leri Danbooru
görsellerini o sitenin etiket dizisi caption olarak eğitildi. Yorumun işi tam bu.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, sırayla, birebir: **939 · 648 · 739 · 591**. Ön yüz derlenmiyor — bu madde
`dist`'e dokunmuyor.
