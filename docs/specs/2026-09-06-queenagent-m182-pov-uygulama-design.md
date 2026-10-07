# Madde 182 · uygulama turu — POV ayrı bir karakter

**Kaynağı:** [test turu spec'i](2026-09-06-queenagent-m182-pov-testler-design.md).
Commit `cc9d49c` 4 kırmızı bıraktı. Koşunun son maddesi.

---

## Üç cümle, üç metin, sıfır kod

**`START_A_SCENARIO`, 2. adım.** Karakteri kuran yere bir cümle: her karakterin yanına `pov_` sürümü
— kısa, sayısız, kıyafetsiz. **Orada**, çünkü ihtiyaç doğduğu an düzeltme turunun ortası, ve modeli
o anda haritalara geri göndermek onu en yüklü olduğu yerde ikinci bir işe koşmak demek.

**`GENERATE_PROMPTS_PLUS`.** Bir cümle: POV çekilen bir karenin kadrosu o kişiyi değil `pov_`
girdisini adlandırır. *"Şunu POV yap"* bu skill'in turunda geliyor; öteki metinde durursa düzeltme
anında görünmez.

**`SDXL_PROMPT_RULES`.** Sayım kuralının hemen ardına istisna: kadraja tam girmeyen bir girdi sayı
taşımaz. Buraya, çünkü **sayının nerede duracağına karar veren metin bu** — istisnayı başka yere
yazmak, kuralı bir yerde kurup başka yerde bozmak olurdu.

Bu metin `add_character`, `add_outfit` ve `add_location`'ın açıklamalarına ekleniyor, yani cümle
oralarda da okunuyor — ve orada da doğru: `pov_kyle`'ı yazan araç `add_character`.

## Kelime tavanı — ve ödenen bedel

Tavan gerçekten kırmızı verdi: ilk yazımda `START_A_SCENARIO` **493** kelimeydi. Kural işledi, cümle
kısaldı, ve *"bir cümle ancak bir cümle silinerek girer"* lafta kalmadı — silinen şu oldu:

> Tags are taken as they are; a description becomes tags;

**Neden bu.** `add_character`'ın kendi parametre metni zaten *"The character as tags: how many
people this entry draws, their age, body, hair and face"* diyor. Akış metnindeki cümle onun
kopyasıydı, ve bir kopya bayatlayacak olan taraftır. Hiçbir test onu tutmuyordu; tuttukları
*"placeholder"* ve *"never stop the flow"*, ikisi de yerinde.

Metin şimdi **tam 450**. Bir sonraki madde bu metne dokunacaksa boşluk yok — tavanın istediği de bu.

## İkinci çarpışma: `shot` yasak bir kelime

`test_no_instruction_calls_a_frame_a_shot` skill metinlerinde *"shot"*'ı süpürüyor — Madde 94'ten
kalma, karenin adı *"shot"* değil diye. İlk yazımda iki cümlede de geçiyordu *("frames shot from
their own eyes", "whoever is in shot")*. İkisi de *"a frame through their own eyes"* ve *"whoever the
picture holds"* oldu. Kural doğru; POV'u anlatmanın *"shot"* demeden bir yolu var.

## Kod niye açılmıyor

`add_character` `pov_kyle` adını bugün de kabul ediyor, kadro bugün de onu adlandırabiliyor,
derleyici de bugün de o girdiyi yazıyor. Eklenen tek şey **ne zaman hangisinin kullanılacağı**, ve o
bir kural — kuralın yeri metin.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **836 yeşil.** 4 kırmızının hepsi dönmeli, nöbetçi ve kelime tavanı yeşil kalmalı.
3. Öteki üç takım: **589 · 739 · 591.** `dist` derlenmiyor — üç madde de frontend'e dokunmadı.

## Koşu kapandı

**180, 181, 182 — üç madde, altı tur.** Deneme 3 ve 4'ün getirdiği: araya kare, eylem satırının içi,
ve kadraja tam girmeyen karakter. Yalnız ilki kod.

Merge'den önce: `queenagent.ipynb` ve `test_notebook.py`'nin `BRANCH`'i `main`'e döner. Dal `v7`'ye
birleşir, `v7` de kendi sırasında `main`'e.
