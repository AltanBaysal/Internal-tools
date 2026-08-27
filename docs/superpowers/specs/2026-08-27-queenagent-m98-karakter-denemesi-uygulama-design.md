# Madde 98 — Karakter tek başına denenir · **uygulama turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 6, Madde 98 ·
**Turun birincisi:** [test turu](2026-08-27-queenagent-m98-karakter-denemesi-testler-design.md) —
on dört kırmızı commit'lendi *(`cea56ca`)*.
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder.

---

## Kurucu: `build_character_prompts`

`build_prompts`'un yanına, aynı dosyaya. Yapı ile bir karakter adı alıyor, ve dosyanın her kıyafeti
için bir prompt döndürüyor: kalite, kimlik, kıyafet.

Kıyafet haritası boşsa tek satır: kalite ve kimlik. Kişi sayısı **yazılmıyor** — sayı karenin
alanı, ve burada kare yok.

Birleştirmeyi yapan `_tags`, yani boş kalite ya da boş kıyafet aynı sessizlikle düşüyor. Kurucu
kendi başına bir sıra icat etmiyor: bir karakterin bloğu neyse o.

## Bilinmeyen ad

Karakter haritada yoksa `BadStructure`, ve cümle bilinen adları sayıyor. `_looked_up`'ın cümlesiyle
aynı kalıp, **kare numarası olmadan** — burada kare yok, ve olmayan bir numarayı yazmak uydurmak
olurdu.

Toplayıp sonra atmak yok: tek bir ad soruluyor, ve yanlışsa cevap hemen geliyor.

## Ad: `character_prompts_name`

Kaynak ile karakter birleşiyor — `bar-scene.json` artı `aylin` → `bar-scene-aylin.py`. Böylece iki
karakter yan yana denenebiliyor ve ikisi de sahnenin kendi listesinden ayrı duruyor.

Karakter adı modelden geliyor, yani temizlenmesi gerekiyor. Temizleme `naming.py`'ye giriyor:

- **Neden orada:** o dosyanın işi *"bir şeyi bir yere koyarken adı ne olur"*, ve iki kopya ilk
  değişiklikte ayrışır — dosyanın kendi başlığı bunu söylüyor.
- **Neden `safe_name` değil:** `safe_name` bir **dosya adı** temizliyor ve noktayı koruyor, çünkü
  uzantı orada. Bu ise bir adı başka bir adın içine katlıyor; nokta da tire oluyor. İki kural
  kardeş, aynı değil.

## Araç

`build_character_prompts`, iki alan: yapı dosyasının adı ve karakter. İkisi de zorunlu — hangisini
deneyeceğini kodun tahmin etmesi gereken bir şey yok.

`WRITES_FILES`'a **giriyor**: dosya doğuruyor, sohbette kart açıyor. Sonucu kaç prompt yazdığını
söylüyor.

Türetilmiş bir dosya, yani üstüne yazılıyor — numaralanmıyor. `build_prompts` de böyle yapıyor, ve
sebebi aynı: yeniden kurmak işin kendisi.

## Kip

Yalnız edit. Yazan bir araç.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `build_prompts` | Sahne listesi aynı yoldan çıkıyor |
| `render_module`, `prompts_name` | Çıktının biçimi ortak, sahnenin adı değişmiyor |
| `safe_name` | Dosya adı kuralı; kardeşi geldi diye değişmiyor |
| Skill metni | Aracı anlatan cümle **Madde 101**'in işi; bugün akış skill'i yok |
| Ön yüz | `dist` derlenmiyor |

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
```

On dört kırmızı yeşile döner. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.
