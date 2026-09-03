# Madde 161 — `set_` yeniden adlandırır · **uygulama turu**

**Tarih:** 4 Eylül 2026 · **Branch:** `feat/v7` · **Test turu:**
[m161 yeniden adlandırma testler design](2026-09-04-queenagent-m161-yeniden-adlandirma-testler-design.md) ·
**Kırmızı commit:** `test(m161)`

30 test kırmızı. Bu belge onları yeşile çeviren kodu anlatır.

## `_set_entry` `_opened`'a geçer

Bugün kendi önsözünü taşıyor. Yeniden adlandırma **kareleri yazmak** zorunda, yani `frames` listesi
artık gerçek bir şart — `_remove_entry`'nin 157'de aynı sebeple yaptığı geçişin aynısı. Üç önsöz
yerine bir tane.

## Sıra, ve her adımın neden orada olduğu

```
_opened  →  boş name  →  var mı?  →  (yoksa: new_name ret / eksik alan ret / ekle)
                                  →  (varsa: hiç alan yok ret → new_name kontrolleri → yaz)
```

`new_name` kontrolleri **yazmadan önce** biter: boş, aynı, dolu. Üçü de reddedince dosyaya hiç
dokunulmuyor — bu modülün her yerindeki kural.

## `_renamed(structure, which, old, new)`

Anahtarı taşıyan ve kareleri takip ettiren fonksiyon. Kaç karenin takip ettiğini döndürür.

**Harita yeniden kuruluyor, `pop` + atama değil.** Python bir anahtarı ilk yazıldığı yerde tutar;
`entries[new] = entries.pop(old)` yeni adı **sona** atar. Karakter haritasında sıra bir kayıt sırası,
ama **karenin** `characters` haritasında sıra **liderdir** — `build_prompts` ilk yazılanı promptun
başına koyuyor. Aynı disiplin `_renumber`'da da var: sözlük yeniden kuruluyor çünkü bir alanın yeri
bir anlam taşıyor.

Kareyi gezerken üç şekil birden okunuyor, `_worn`'un okuduklarının aynısı:

| Şekil | Nerede | Ne yapılıyor |
| --- | --- | --- |
| `{"aylin": ["gecelik"]}` | karakter anahtarı, kıyafet listesi | anahtar yerinde değişir; liste elemanı konumunda değişir |
| `["aylin", "lara"]` | eski liste biçimi | eleman değişir |
| `{"aylin": "gecelik"}` | tek string kıyafet | string değişir |

`locations` için yalnız `frame["location"]`.

**Sayım `_frames_naming` ile yapılmıyor:** o eski adı arar ve iş bittiğinde eski ad kalmamıştır.
Değişiklik yapılırken sayılıyor, tek geçişte.

## `_set_entry`'nin gövdesi

**Yeni bir ad:** `kind` *(karakterde)* ve `tags` zorunlu; biri eksikse ret ve girdi doğmaz.
`new_name` verilmişse ret — çağrı bir şeyi taşımak istiyor ve o şey yok.

**Var olan bir ad:** `new_name`, `kind`, `tags`'ten hiçbiri gelmemişse ret. Gelen ne varsa iner:

- `kind` verilmişse `KINDS`'ta olmalı. Girdi düz metinse harita biçimine geçer ve eski metin `tags`
  olur.
- `tags` verilmişse yazılır. Girdi düz metinse **düz metin kalır** — boş bir `kind` yazmak, hiçbir
  şey söylemeyen bir alan yazmaktır, ve `_kind` onu zaten yok sayardı.
- `new_name` verilmişse `_renamed` koşar.

**`kind`/`tags`'in "verilmiş" sayılması `in args` ile**, `args.get()` ile değil: boş string bir
değerdir ve modelin bir etiketi silmesinin tek yolu odur. `None` gönderilirse verilmemiş sayılır.

## Cevaplar

| Durum | Cümle | Outcome |
| --- | --- | --- |
| Ekleme | `Added lara to characters.` | `Added` |
| Değiştirme | `Changed aylin in characters; 2 frames name it.` | `Changed` |
| Yeniden adlandırma | `Renamed aylin to ayla in characters; 2 frames followed.` | `Renamed` |
| İkisi birden | `Renamed … and changed its tags; 2 frames followed.` | `Renamed` |

## Araç tanımları

Üçünde de `required` **`["file", "name"]`**, ve `new_name` parametresi. Açıklamalar iki cümle
kazanıyor: verilmeyen alanın durduğu, ve `new_name`'in kareleri de taşıdığı. `SDXL_PROMPT_RULES`
yerinde.

## Bu turda dokunulmayanlar

- **`skills.py`.** İki metin de `set_`'leri adıyla anıyor ve ne yaptıklarını araç açıklaması
  söylüyor. Metne cümle ancak bir cümle silinerek girer *(Madde 123)*.
- **`build_prompts`.** Okuduğu şekiller değişmiyor.
- **`remove_` ve `update_frame`.** Dokunulmuyor.

## Nasıl yeşil olacak

30 kırmızının hepsi kapanır. Notebook'un iki kırmızısı yerinde kalır.
