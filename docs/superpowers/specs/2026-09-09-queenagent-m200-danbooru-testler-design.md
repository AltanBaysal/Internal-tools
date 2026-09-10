# Madde 200 · test turu — etiketler Danbooru sözlüğüyle

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 200.

---

## Bugün ne oluyor

`SDXL_PROMPT_RULES` etiketlerin **şeklini** söylüyor — kısa, virgülle ayrılmış, cümle değil — ama
**hangi sözlükten** olduğunu hiç söylemiyor. Örnekler de yarı serbest: `woman in her mid 20s`,
`cozy bedroom, morning light through curtains`. İçlerinde `1girl` gibi gerçek Danbooru etiketleri
var, ama kural onları bir sözlüğün parçası olarak değil, kendi verdiği örnekler olarak taşıyor.

Modelin iyi bir etiket yazması bugün **tesadüf**: kural onu istemiyor.

## Ne kurulacak

Kural sözlüğü adıyla anıyor, ve dört şeyi söylüyor:

- **Etiket, sözlüğün sahip olduğu etikettir** — tarif değil. `looking at viewer` eğitimde geçen
  stringin ta kendisi; aynı şeyin serbest tarifi hiç geçmedi.
- **Boşlukla yazılır, alt çizgiyle değil.** Sitede `looking_at_viewer`, bu modellerde boşluklu.
  *(Deponun `pov_` adlandırması etiket değil, harita girdisinin adı — ona dokunulmuyor.)*
- **Etiket atomiktir:** `long hair, black hair`, tek bir `long black hair` değil. Sözlükte ikisi ayrı
  ayrı var ve birleşiği yok; birleşik yazılan şey yine sözlük dışına düşüyor.
- **Sözlükte karşılığı olmayan şey** kısa düz kelimelerle yazılır — orada da cümle kurulmuyor.

Karakter ve mekân parametrelerinin örnek metinleri de aynı dile çevriliyor.

### Değişmeyen ne varsa yerinde kalıyor

Sayının karakter girdisine ait olması, `pov_` girdisinin sayı taşımaması, kıyafetin ayrı girdi
olması, mekânda kimsenin bulunmaması, kalite etiketi yasağı, ve `or` yasağı. Bu madde **sözlüğü**
söylüyor, kuralları yeniden yazmıyor — o testlerin hepsi yeşil kalmalı.

## Testler

### `test_tools.py`

1. **kural sözlüğü adıyla anıyor** — `SDXL_PROMPT_RULES` içinde `danbooru`, ve etiketin bir tarif
   değil sözlüğün etiketi olduğunu söyleyen cümle.
2. **boşluk, alt çizgi değil** — kural alt çizgiden söz ediyor, çünkü model sitedeki yazımı
   kendiliğinden getirir.
3. **etiket atomik** — kural `long hair, black hair` örneğini taşıyor ve `long black hair`'i
   taşımıyor.
4. **karşılığı olmayan şey** — kural sözlükte olmayan bir şeyin nasıl yazılacağını söylüyor.
5. **karakter örneği o dilde** — `ADD_CHARACTER_TAGS` `long hair` ile `black hair`'i ayrı taşıyor,
   `long black hair` ve `woman in her mid 20s` geçmiyor.
6. **mekân örneği o dilde** — `ADD_LOCATION_TAGS` `indoors` taşıyor, `morning light through
   curtains` taşımıyor.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. Arka uçta **6 kırmızı**: bugünkü metinlerde ne sözlüğün
adı var, ne alt çizgi kuralı, ne atomik örnek — ve iki örnek metin hâlâ serbest cümle taşıyor. Ön
yüz ve `queen-editor` kımıldamıyor: **648 · 739 · 591** yerinde.
