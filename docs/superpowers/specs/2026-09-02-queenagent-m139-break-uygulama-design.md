# Madde 139 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-09-02-queenagent-m139-break-testler-design.md](2026-09-02-queenagent-m139-break-testler-design.md)
**Kırmızı commit:** `70d5542` — 4 kırmızı, 658 yeşil; ön yüz 570 yeşil.
**Dal:** `feat/v6`

## Ne yeşile dönecek

Dört test. İkisi ana karakterden sonrakinin ` BREAK ` ile ayrılmasını, biri üçüncü karakterin de
ayrılmasını, sonuncusu `BREAK`'in virgül komşuluğuna hiç girmemesini bekliyor.

## Tek dosya: `build_prompts.py`

Bugün `build_prompts` bütün parçaları tek bir listeye topluyor ve sonunda tek bir `_tags` çağrısından
geçiriyor. Değişen: **liste yerine blok listesi**, ve blokların ` BREAK ` ile birleşmesi.

```
[quality, people, ana karakter + kıyafeti, mekân, action, camera]   ← bir blok
[ikinci karakter + kıyafeti]                                        ← ikinci blok
[üçüncü karakter + kıyafeti]                                        ← üçüncü blok
```

Her blok kendi `_tags`'inden geçiyor — yani virgüller blok **içinde** kalıyor — ve bloklar
` BREAK ` ile ekleniyor. `BREAK` böylece hiçbir zaman bir virgülün yanına düşmüyor.

**Sıra değişmiyor.** Blokların içeriği ve dizilişi bugünkünün aynısı; değişen yalnız aralarına ne
girdiği. Sırayı indeksle ölçen üç bekçi bu yüzden yeşil kalıyor.

## Boş blok `BREAK` doğurmaz

`_tags` boş bir bloktan boş string döndürüyor, ve boş bir parça birleştirmeye girerse prompt
` BREAK ` ile biter ya da iki ayraç yan yana gelir. Birleştirme boş blokları **atarak** yapılıyor.

Bunun bugün gerçekleşen tek yolu: bir karakterin adı haritada yoksa `_looked_up` boş string döndürüp
hatayı `misses`'a yazıyor. O durumda zaten `BadStructure` fırlatılıyor ve prompt hiç dönmüyor — ama
birleştirme buna güvenmiyor, çünkü güvenmek için bir sebep yok ve atmanın bedeli bir koşul.

## `build_character_prompts` değişmiyor

Tek karakteri tek başına deneyen yol. Orada ikinci blok hiç doğmuyor, yani ayıracak bir şey de yok.
Bekçisi yazıldı.

## Değişmeyenler

- **`_tags`, `_block`, `_worn`, `_looked_up`** — dördü de olduğu gibi. Madde birleştirmenin
  **üstünde** duruyor, içinde değil.
- **Sıra** — Madde 95'in düzeni: ana karakter başta, geri kalan `camera`'dan sonra.
- **Hata toplama** — her kaçak tek seferde bildiriliyor, ve kirli bir yapı hiç prompt üretmiyor.
- **`render_module`, `prompts_name`, `character_prompts_name`** — çıktının biçimi ve adı.

## Bilinen sonuç: kalite zinciri yalnız ilk blokta

Bloklar ayrı kodlandığı için ikinci ve üçüncü karakterin parçası kalite etiketlerini görmüyor.
A1111 tarafında `BREAK`'in olağan davranışı bu ve bilerek kabul ediliyor — zincirin işi karenin
genel görünüşünü kurmak, ve o ilk blokta kuruluyor.

Kayda geçiyor çünkü ileride *"ikinci karakter neden daha sönük"* diye sorulursa cevabın yarısı
burada.

## Skill metni ve şema bu turda ellenmiyor

Prompt+ metni promptun neye benzediğini anlatıyor. `BREAK`'in oraya yazılıp yazılmayacağı ayrı bir
soru: metin **modelin ne yazacağını** anlatıyor, ve `BREAK`'i model yazmıyor — kod yerleştiriyor,
tıpkı sıra gibi. Yani metnin bugünkü hâli yanlış değil, eksik olup olmadığı ayrı bir maddenin işi.

## Colab'da görülecek

Takım yeşil, promptun `BREAK` taşıdığını söyler. Ekranda ne yaptığını söyleyen şey koşunun kapanış
denemesi: QueenAgent iki karakterli bir kareden prompt üretir, `PROMPTS = [...]` queen-editor'e
yapıştırılır, ve 138'in düğümü onu böler. Elle yazılan `BREAK` ile üretilen `BREAK` arasında fark
olmamalı — aynı metin, aynı yol.
