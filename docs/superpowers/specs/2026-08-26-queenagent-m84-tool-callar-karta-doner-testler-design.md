# Madde 84 — Tool call'lar karta döner ve tek kapının arkasına girer · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 4, Madde 84 ·
**Üstüne geldiği:** [Madde 78](2026-08-26-queenagent-m78-tool-satiri-uygulama-design.md) — satırın
bugünkü çizimi.
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod yazılmaz, ve tur kırmızı
commit'lenir.

---

## Bugün nasıl duruyor

```
⏺ list_files
  ⎿ No files
⏺ read_file(aylin.json)
  ⎿ 45 lines
Here it is.
```

Mono, 11.5px, gri, kenarlıksız, aralarında 2px. 78 bunu bilerek yaptı ve gerekçesi stil dosyasında
yazılı: *"olmuş bir adım bir kayıttır, basılacak bir şey değil"*.

Gerekçe doğru, sonucu değil. **Bir şeyin kayıt olması silik olmasını gerektirmiyor.** Ekranda bu
satırlar cevabın üstünde eziliyor, ve on altı raunda kadar dönen bir turda yirmi tanesi göz
gezdirilen bir gri blok oluyor.

## Ne olacak

**Her çağrı bir kart**, ve kartlar tek bir kapının arkasında:

```
kapalı, cevap akarken           kapalı, cevap bittiğinde        açık
┌──────────────────────────┐    ┌──────────────────────────┐    ┌──────────────────────────┐
│ ⏺ read_file(aylin.json) ⌄│    │ ⏺ 5 steps               ⌄│    │ ⏺ 5 steps               ⌃│
└──────────────────────────┘    └──────────────────────────┘    └──────────────────────────┘
                                                                ┌──────────────────────────┐
                                                                │ ⏺ list_files    No files │
                                                                └──────────────────────────┘
                                                                ┌──────────────────────────┐
                                                                │ ⏺ read_file(…)  45 lines │
                                                                └──────────────────────────┘
```

Dört durum, iki eksen:

| | **Kapalı** | **Açık** |
|---|---|---|
| **Cevap akarken** | son çağrının kartı | tutamak `5 steps` + hepsi |
| **Cevap bittiğinde** | `5 steps` | tutamak `5 steps` + hepsi |

**İkisi kodda zaten ayrı yerler.** Akan kutu canlı akıştan çiziliyor, bitmiş cevap kendi kaydından —
yani "bitince kapansın" diye bir geçiş yazmaya gerek yok. Akan kutu doğası gereği çalışıyor, kayıt
doğası gereği bitmiş.

## Kararı verilmiş

*(kullanıcı kararı, 26 Ağustos)*

- **Tam ağırlık.** Kart, deponun kendi dosya kartıdır: yüzey, 1px çizgi, 12px köşe, 340px sınır.
  Yeni bir görsel dil icat edilmiyor.
- **Tutamak da bir kart.** Sessiz bir metin satırı değil; aynı kart, üstünde `⌄`.
- **Kapalıyken akan turda son çağrı, bitmiş turda sayı.** Biten bir turda *"ne yaptı"* sorusunun
  cevabı bir sayıdır; son adım tek başına *"tek yaptığı bu"* gibi okunur.

## Kararlar

**Basılan kart bir kapı, basılmayan kart bir kayıt.** Tutamak `<button>` ve `cursor: pointer`
taşıyor; çağrı kartları `<div>` ve hiçbir imleç taşımıyor, hover'da kenarlığı oynamıyor. 78'in
gerekçesi böyle korunuyor — vurgu birincil eylemi işaretler, ve olmuş bir adım basılacak bir şey
değil. Değişen şey gerekçe değil, sessizliğin gerekli olduğu varsayımı.

**`⎿` düşüyor.** O işaret *"üstündekinin sonucu"* demekti. Kartın sınırı artık aynı şeyi söylüyor:
bir kartın içindeki her şey tek bir çağrıya ait. Sonuç ikinci satır olmaktan çıkıp kartın sağ ucuna
geçiyor — dosya kartındaki nota denk düşen yer.

**Rozet yok.** Dosya kartındaki 30×30 kare bir uzantı taşıyor *(`md`, `json`)*. Bir çağrının
uzantısı yok, ve içine tek bir işaret koymak kutuyu boş gösterir.

**Parantez duruyor.** 78'in kararı: konusu olmayan bir çağrının parantezi de yok, çünkü orada duran
boş bir çift, olmayan bir şeyi varmış gibi gösterir.

**Açık/kapalı diske yazılmaz.** Bir bakış tercihi, sohbet hakkında bir olgu değil. Her mesaj kendi
durumunu tutuyor ve sayfa yenilenince kapalıya dönüyor. Yeni gelen cevap da kapalı doğuyor — mesajın
anahtarı yeni, yani durumu da yeni.

**Tek çağrı `1 step`.** Çoğul eki sayıya bakıyor. `1 steps` yazan bir arayüz, sayıyı hiç okumamış
gibi görünür.

**Hiç çağrı yoksa hiçbir şey çizilmiyor** — bugünkü davranış, aynen.

## Kırmızıya dönecek testler

**`ChatScreen.test.jsx` — on iki:**

| # | Test | Bugün | Yarın |
|---|---|---|---|
| 1 | kayıt kapının arkasında | iki `.tool-call` çizili | sıfır; ortada `2 steps` kartı var |
| 2 | **yeni** — açınca hepsi listeleniyor | basılacak bir şey yok | iki `.tool-call` |
| 3 | **yeni** — tekrar basınca kapanıyor | aynı | sıfıra dönüyor |
| 4 | çağrı aracı ve parantezini yazıyor | satır açıkta | kart açıldıktan sonra aynı metin |
| 5 | konusu olmayan çağrının parantezi yok | satır açıkta | kart açıldıktan sonra aynı metin |
| 6 | sonucu kartın üstünde | `⎿ No files` | `No files` |
| 7 | söyleyecek şeyi olmayan çağrı | satır açıkta | kart açıldıktan sonra ikinci alan yok |
| 8 | akarken kapalı kart ne yaptığını yazıyor | iki satır birden | son çağrı, ve `2 steps` yok |
| 9 | **yeni** — çağrı kartı kapı değil | — | `.tool-call` bir `DIV` |
| 10 | **yeni** — tutamak açık mı kapalı mı söylüyor | — | `aria-expanded` `false` → `true` |
| 11 | **yeni** — akan tur açılınca tutamak sayıya dönüyor | — | `2 steps` |
| 12 | **yeni** — tek çağrı `1 step` | — | `⏺ 1 step` |

**`workspace.css.test.js` — iki:**

| # | Ne tutuyor |
|---|---|
| 13 | **yeni** — çağrı kartı deponun kart iskeletini giyiyor: `12px` köşe, `1px solid var(--line)`, `340px` sınır |
| 14 | **yeni** — çağrı kartında `cursor` yok, tutamakta `cursor: pointer` var |

Toplam **on dört kırmızı**. Altısı var olan testin yeniden yazılması, sekizi yeni.

## Dokunulmayan yeşiller

| Ne | Neyi kanıtlıyor |
|---|---|
| `ChatScreen.test.jsx` — `an answer that called nothing draws no list at all` | Çağrısız cevabın üstünde hiçbir şey yok |
| `ChatScreen.test.jsx` — damga, `Stopped`, dosya kartları | 83, 81 ve 66 aynen duruyor |
| `test_stream_answer.py` ve kayıt testleri | Neyin kaydedildiği değişmiyor |
| `workspace.css.test.js` — `.file-card` testleri | Ödünç alınan iskelet yerinde |

## Kapsam dışı

- **Ne kaydedildiği.** 66 ve 78 ne yazıyorsa o. Bu madde yalnız çizime ve açılıp kapanmaya dokunuyor.
- **Arka uç.** Tek satır değişmiyor.
- **Escape.** Açık liste bir katman değil, sohbetin içinde duran bir kart yığını; Escape'in sırasına
  girmiyor.
- **Açık/kapalının hatırlanması.** Sayfa yenilenince kapalı. Diske de tarayıcıya da yazılmıyor.
- **Türkçe metin.** Arayüz İngilizce *(CLAUDE.md)*.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur** — birlikte koşturulduğunda vitest bu makinede zaman aşımına düşüyor.

Arka uçta değişiklik beklenmiyor: bugünkü **2 failed, 430 passed** aynen kalır, ve o iki kırmızı
defterin `feat/queenagent-v5`'te duran dalı.

Ön yüzde bugün **497 passed**. Sekiz yeni testle toplam **505**, ve **14 failed, 491 passed**
beklenir.

`dist` bu turda derlenmiyor: kaynak değişmiyor, yalnız testler yazılıyor.
