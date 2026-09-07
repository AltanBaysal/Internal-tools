# Madde 171 · test turu — `create_file` ve `edit_file` `.json`'a dokunamaz

**Kaynağı:** [v7 yol haritası, Madde 171](../plans/2026-09-05-queenagent-v7-roadmap.md).
Bu tur yalnız testleri yazar.

---

## Neden şimdi, ve neden 167'den önce değil

Kapı ancak **alternatifi hazırken** kapanabilir. Bugün elde `start_scenario` *(167)* ve dokuz harita
aracı *(168–170)* var: model bir senaryoyu doğurabiliyor, kadrosunu kurabiliyor, düzeltebiliyor ve
silebiliyor — hiçbirinde JSON yazmadan.

**Arşivin sırası bunu tersine dizmişti** ve aradaki boşluk mola noktasıydı. Bu koşuda önce araçlar,
sonra kapı: kapandığında modelin elinde yapacak bir şey var.

## İstisna yok

Arşivde bozuk bir JSON'u `edit_file` onarabiliyordu. **Kullanıcı kararı (5 Eylül): istisna yok.**

Gerekçesi: araçlar bozuk bir dosyayı zaten açamıyor *(`_opened` *not valid JSON* diyor)*, yani bozuk
dosya **elle düzenlemeden** geliyor — modelin yazdığından değil. Onu onarmayı da modele bırakmak,
kullanıcının kendi eliyle bozduğu bir dosyayı modelin tahminine açmak olur. Model *"dosya bozuk, şu
satırda"* der, kullanıcı düzeltir.

Bunun bir sonucu var ve bilerek kabul ediliyor: **bozuk bir yapı dosyası uygulamanın içinden
onarılamıyor.**

## Cümle

> *bar-scene.json* is a structure file; it is not written or changed as text. Use start_scenario to
> open one, and the add_, update_ and remove_ tools to change it.

`create_file`'ın reddi gibi **çıkışı da söylüyor**: yalnız *"olmaz"* demek bir sonraki hamleyi
tahmine bırakır, ve modeli buraya getiren zaten tahmindi.

## Kapının ölçüsü uzantı, ve neden

`start_scenario` adı ne olursa olsun `.json` yazıyor *(`scenario_name`)*. Yani doğuran araç ile
kapanan kapı **aynı uzantı üstünde** buluşuyor — 167'nin spec'inde bu bir gerekçe olarak yazılmıştı,
burada ölçülüyor.

Büyük harf de kapalı: `BAR.JSON` aynı dosyadır ve Windows'ta gerçekten aynı dosyadır.

---

## Testler — `test_tools.py`

| Test | İddiası |
|---|---|
| `test_create_file_refuses_a_structure_file` | Cümle, ve **dosya doğmuyor** |
| `test_edit_file_refuses_a_structure_file` | Aynı cümle, ve **dosya değişmiyor** |
| `test_the_door_is_shut_whatever_the_case_of_the_extension` | `BAR.JSON` de kapalı |
| `test_the_door_is_shut_even_on_a_broken_structure_file` | İstisna yok — kullanıcı kararı, ve testin yorumu sebebini taşıyor |
| `test_create_file_still_writes_a_document` | `.md` el değmemiş |
| `test_edit_file_still_changes_a_document` | `.md` el değmemiş |
| `test_the_tool_that_opens_a_scenario_lands_where_the_door_is` | `start_scenario`'nun yazdığı ad `.json`, yani kapının arkasında — 167'nin gerekçesi burada ölçülüyor |

`write_plan` **kapsam dışı**: adı `plan_name` ile `.md` oluyor, `.json` yazması mümkün değil.

---

## Bu turda yapılmayanlar

- **Kod açılmıyor.**
- **Şema aracı duruyor** — 172. Bugün modele hâlâ *"yapı dosyasını yaz"* diyen bir metin var ve
  artık yazamıyor; o pencere Dilim 1'in sonunda kapanıyor, denemeden önce.
- **Skill metinleri duruyor** — 178.

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **Koşan kırmızı: 5.** Kapıyı çiviyen beş test. İki tanesi bilerek yeşil doğdu —
   `test_create_file_still_writes_a_document` ve `test_edit_file_still_changes_a_document`, çünkü
   `.md` yolu bugün de çalışıyor ve uygulama turunda da çalışması gereken şey o. Kapıyı ölçen
   testler kırmızı, kapının **dokunmaması gerekeni** ölçenler yeşil: bir maddede ikisi de yazılır.
3. Öteki üç takım rakamlarını korur.
4. Kırmızı commit'lenir.
