# Madde 323 — Prompt listesi fotoğraf panelinin okuduğu gibi okunuyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7`, Kol B *(`feat/queen-editor-v7-kol-b`)* · **Tur:** 1/2 — yalnız testler,
kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.**

## Bugün ne oluyor

Sunucu Referanstan'ın listesini zaten fotoğraf panelinin okuyuşuyla okuyor: havuz kapısı
`parse_prompts`'u çağırıyor *(`queue_references.py`)*. Takılan ekran. `LayerPanel`'in `promptsIn`'i
yalnız JSON okuyor ve boş öğeyi listenin bozuk olduğu sayıyor; okuyamadığı listede satır
`Prompt listesi ["ilk prompt", "ikinci prompt"] biçiminde olmalı.` diyor, ve basınca istek hiç
gitmiyor — aynı cümle kırmızı kartta. Fotoğraf panelinde çalışan `PROMPTS = ['a', 'b']` burada ne
sayılıyor ne gönderilebiliyor.

## Kurallar

1. **Satır, basınca ne doğacağını sayıyor:** `2 prompt × 3 varyant = 6 kart`. Okuduğu listeler
   satırın söylediği: JSON dizisi ya da Python list/tuple, iki tırnakla da; önde isteğe bağlı
   `AD =`; boş öğeler düşüyor.
2. **Kutu boşken ya da liste okunamazken satır boş.** Bugünkü `… biçiminde olmalı.` cümlesi
   hiçbir yerde yok.
3. **Liste okunamasa da basış gidiyor**, liste yazıldığı gibi. Reddi sunucu veriyor, fotoğraf
   panelinin cümleleriyle *(`Prompt listesi boş.` · `Format hatası — liste okunamadı`)*, ve cümle
   basılan panelin kırmızı kartında duruyor.

**Sayım neden ekranda.** FOUNDATION 4 yazarken gösterilen tahmini arayüze bırakıyor — sunucunun
kuralını yansıtan bir tahmin önizlemedir, hiçbir şeyi durdurmaz. Ekranın okuyuşu bu yüzden yalnız
sayar; basışı kural 3 kesiyor: önizleme ne derse desin istek gider, karar ve cümleler
`prompt_list.py`'de, tek yerde. Sunucunun okuyup ekranın okuyamadığı bir listede *(örneğin üç
tırnaklı, çok satırlı öğeler)* satır boş kalır ama basış yine gider. Her tuşta sunucuya sormak
seçilmedi: FOUNDATION'ın zaten arayüze koyduğu bir satır için yeni bir kapı ve her tuşta bir istek.

**Boş kutunun basışı** bu maddede sunucuya gidiyor ve `Prompt listesi boş.` dönüyor; 324 düğmeyi
kutu boşken kapatıyor *(tasarım)*. Bunun testi burada yazılmıyor — 324 onu hemen tersine çevirirdi.

## Yazılacak testler

### `LayerPanel.test.jsx` — *"producing from the reference pool"* bloğu

1. **Önünde adıyla, tek tırnaklı bir Python listesi okunuyor** — `PROMPTS = ['a', 'b']`:
   `2 prompt × 1 varyant = 2 kart`.
2. **Tuple, iki tırnak karışık okunuyor** — `("gotik kız", 'dans')`: `2 prompt × 1 varyant = 2 kart`.
3. **Boş öğeler sayıya girmiyor** — `["gotik kız", "", "  ", "dans"]`:
   `2 prompt × 1 varyant = 2 kart`.

### `ProjectScreen.test.jsx` — yeni blok *"a prompt list the server cannot read (madde 323)"*

4. **Okunamayan listenin basışında sunucunun cümlesi görünüyor** — `gotik kız` yazılıp basılıyor:
   `produceFromReferences("liste-a", "gotik kız", 1)`; sunucu `Format hatası — liste okunamadı`
   diye reddediyor ve cümle ekranda. API taklidine `produceFromReferences` ekleniyor.

**Değişen:** `LayerPanel.test.jsx` —

- `says what is wrong with a list it cannot read, instead of a count` eski cümleyi satırda
  bekliyordu. Yerine *"says nothing under the button while the box is empty or its list cannot be
  read"*: boş kutuda ve `gotik kız`'da ne sayı ne `biçiminde olmalı` ne de basılmadan
  `Format hatası`.
- `sends nothing when there are no prompts to send` boş kutunun basışını ekranın kendisinin
  reddetmesini bekliyordu. Yerine *"sends a list it cannot read as it was typed"*: `gotik kız`
  basılınca `onQueue(null, 1, "reference", "gotik kız")`, ve eski cümle yok.

**Bekçiler:** `counts the cards the press would make` *(JSON, 6 kart)*,
`sends the prompts and the variants under the reference kind`, `lays Referanstan out in the
design's order` *(kutunun başlığı `Prompt listesi`)*, `shows a refusal where the press was made`;
sunucuda `test_prompt_list.py` *(okuyuş ve iki cümle)* ve
`test_a_reference_run_reads_the_prompt_list_the_way_the_photo_panel_does` *(havuz kapısı aynı
okuyuşu kullanıyor)*.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` vitest'te 1–4 ve değişen iki test kırmızı, doğru sebeple:
satır sayı yerine eski cümleyi söylüyor, ve basış ekranda kesiliyor. İki pytest satırı ve
`queen-agent` vitest'i yeşil.
