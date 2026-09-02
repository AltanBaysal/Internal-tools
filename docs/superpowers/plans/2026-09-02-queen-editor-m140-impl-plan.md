# Madde 140 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-02-queen-editor-m140-modeller-uygulama-design.md](../specs/2026-09-02-queen-editor-m140-modeller-uygulama-design.md)
**Dal:** `feat/v6`
**Kırmızı commit:** `92e0eea`
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. CONFIG hücresi — kutu ve yorum.

Üç üretici kutusunun altına boş satır, sonra:

```python
# Foto grubunun kendi modeli yukarıdaki kutuyla iniyor; buradakiler onun ÜSTÜNE ekleniyor. Her biri
# ~7 GiB, ve /content runtime ile öldüğü için her açılışta yeniden iniyor — bedeli tek seferlik
# değil. O yüzden kapalı geliyorlar: yalnız o koşuda kullanacağını işaretle. Fotoğraf kutusu
# kapalıyken hiçbiri dikkate alınmaz.
PHOTO_NOVAORANGE = False  #@param {type:"boolean"}
```

Üstteki yorumun iki satırı da düzeliyor: *"bu üç satırı"* → *"bu satırları"*, ve boyut satırı foto
için tabanı ve ek model bedelini birlikte söylüyor.

→ A ve B testleri yeşile döner.

## B. İndirme hücresi — `PHOTO_EXTRA`, `CIVITAI_PHOTO`, `PHOTO_GIB`, `SIZES`.

`CIVITAI_PHOTO`'nun **üstüne**:

```python
# Extra photo checkpoints, each behind its own CONFIG box. The group's own model is in the list
# below and is deliberately NOT one of these: the graph export names it, the app renders a frame
# planned without a model using it, and model_groups counts it as the group's requirement -- three
# places that a switch here would contradict at once.
# Illustrious-based only: the graph's lora is switched on for good and would not load onto another
# base, so a checkpoint from another family belongs in its own item, not this list (Madde 142).
# (switch, gib, version_id, filename, label)
PHOTO_EXTRA = [
    (PHOTO_NOVAORANGE, 7, 2945776, "novaOrangeXL_rexV10.safetensors", "Nova Orange XL REX v1.0"),
]
```

`CIVITAI_PHOTO`'nun kapanışı değişiyor:

```python
    (1552087, LORA, "USNR_STYLE_ILL_V1_lokr3-000024.safetensors", "USNR STYLE ILL v1.0"),
# Appended to the list itself rather than to civitai_jobs below: that line reads
# `CIVITAI_PHOTO if INSTALL_PHOTO else []`, and a group whose rows can be reached by another route
# is a group whose switch can be walked around.
] + [(vid, CKPT, fn, label) for on, _gib, vid, fn, label in PHOTO_EXTRA if on]
```

`SIZES`'ın üstüne toplam, ve `SIZES`'ın foto satırı:

```python
# The photo group is the one that varies, so its number is summed rather than written down: 8 for
# the group itself, plus whatever was ticked on top of it.
PHOTO_GIB = 8 + sum(gib for on, gib, *_rest in PHOTO_EXTRA if on)
SIZES = [(INSTALL_PHOTO, PHOTO_GIB, "fotoğraf"), (INSTALL_VIDEO, 39, "video"),
         (INSTALL_AUDIO, 9, "ses")]
```

→ C, D ve E testleri yeşile döner.

## C. Metin hücreleri — üç sayı.

- **Giriş hücresi:** `(19 custom node)` → `(20 custom node)`; ve boyut satırı foto için ek model
  bedelini de söyler.
- **Modeller başlığı:** `(~8 / ~39 / ~9 GiB)` foto tarafında değişkenliği anar; altındaki
  *"Model eklemek"* notu artık foto checkpoint'i için `PHOTO_EXTRA`'yı gösterir.

→ F testi yeşile döner.

## D. Koşuldu: **732 yeşil, 0 kırmızı** *(arka uç)*.

`python -m pytest queen-editor -q` — altı kırmızının altısı döndü, hiçbir bekçi düşmedi. Adı
geçmesi gereken üçü de yeşil kaldı: `test_an_unticked_group_costs_no_bytes` *(ekleme yerinin
seçilme sebebi)*, `test_every_file_the_panel_counts_is_fetched_by_the_notebook` ve
`test_the_notebook_says_how_many_custom_nodes_it_installs`.

**Bir ara kırmızı, ve sebebi metnin sarımıydı.** İlk koşuda beş test döndü, altıncısı kaldı: giriş
hücresinde `(20 custom` ile `node)` arasına satır sonu düşmüştü, test ise bitişik arıyor. Paragraf
yeniden sarıldı. Kayda geçiyor çünkü testin bir keskin kenarı: iddia kelimeleriyle birlikte
aranıyor, yani paragrafı yeniden saran biri sayı doğruyken kırmızı alır. Kardeş testi
*(`test_the_notebook_says_how_many_custom_nodes_it_installs`)* yalnız `(20)` aradığı için bu
soruna açık değil.

## D2. Ön yüzde bir kırmızı var, ve bu maddeden gelmiyor.

`npm test --prefix queen-editor/frontend` — **27 dosya yeşil, 1 kırmızı: 586/587.**
`PhotoDetail.test.jsx › keeps the picture and lays a box over it while a layer is made`, 5000 ms
sınırında **zaman aşımı** — iddia patlaması değil.

**Maddeyle ilgisi yok, ve bu gösteriliyor:** `git status` bu turda değişen dosyaları
`queeneditor.ipynb` ve bu turun iki belgesi olarak sayıyor; ön yüzün tek dosyası ellenmedi, ve aynı
takım kırmızı commit `92e0eea`'da 28 dosya / 587 yeşildi.

**Sebebi deponun kendi kaydında yazılı.** [vite.config.js](../../../queen-editor/frontend/vite.config.js)
`maxWorkers: "50%"` yorumunda: bir worker kendi jsdom'unu taşıyor, kalabalıkta tek başına 99 ms okuyan
bir test 5107 ms okuyor, ve zaman aşımı duvar saatini ölçtüğü için biten testi *takılmış* sayıyor.
1 Eylül'de queen-agent'ta ölçülmüş, queen-editor'e ihtiyaten uygulanmış, ve **"bu tarafta kırmızı
görülmedi"** diye not düşülmüştü. Bugün görüldü: test 5758-6475 ms okuyor, ve toplam test süresi
34 sn'lik duvar saatine karşı 136-172 sn — yani `%50` bu tarafta da yetmiyor.

**Burada düzeltilmiyor.** Ayrı bir problem, ayrı bir madde: kendi kırmızısını ve kendi ölçüsünü
istiyor, ve 140'ın commit'ine karıştırmak ikisini birden okunmaz yapardı.

## E. Yeşil commit.

`queeneditor.ipynb` ve bu turun iki belgesi.

`dist` yeniden derlenmiyor: ön yüz değişmiyor.

## Bilerek yapılmayanlar

**`model_groups.py`** — ek checkpoint foto üreticisinin şartı değil.

**Grafik, uygulama, ön yüz, `dist`.**

**Grafiğin CFG'si.** Yeni model 4.5 öneriyor, grafik 6'da sabit. Modele göre örnekleyici ayarı ayrı
bir maddenin işi; burada yalnız kayda geçiyor.

**Taban modele kutu.** Üç yerde birden şart sayılıyor.
