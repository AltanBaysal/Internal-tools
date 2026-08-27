# Madde 98 — Karakter tek başına denenir · **test turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 6, Madde 98 ·
**Kararı:** [karar defteri](../../2026-08-27-queenagent-skill-kararlari.md) K36 ·
**Şartı:** Madde 95 — aynı kurucuyu paylaşıyor *(`1e11e78`)*
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder.

---

## Bugün ne oluyor

Kullanıcı bir karakteri sahneye sokmadan görmek istiyor — *"bakayım nasıl çıkıyor"*. Bugünkü tek
yol, o karakteri ve tek bir kareyi taşıyan ayrı bir yapı dosyası yazdırıp onu kurmak. Üç adım, ve
geriye ortalıkta duran bir deneme dosyası kalıyor.

## Ne olur

İkinci bir kurucu: bir yapı dosyası ile bir karakter adı alıyor, ve o karakterin **her kıyafeti
için bir prompt** üretiyor. Düz bir liste, `PROMPTS` biçiminde, yapıştırılmaya hazır.

```
quality, KARAKTER, kıyafet
```

Kıyafetler dosyanın `outfits` haritasının sırasıyla geliyor. Kıyafeti olmayan bir dosya tek satır
veriyor: kalite artı kimlik.

## İçinde model yok

Kod etiketleri birleştiriyor, `build_prompts` ne yapıyorsa o *(K36)*. Karakter denemede nasıl
görünüyorsa sahnede de öyle görünüyor, çünkü ikisini kuran aynı kurallar.

**Kişi sayısı yazılmıyor.** Sayı karenin alanı ve burada kare yok; kodun uyduracağı bir şey de
değil *(K8)*. Denemenin çıktısı kimliğin kendisi.

## Çıktı kendi dosyasına yazılıyor

Kaynağın adı ile karakterin adı birleşiyor: `bar-scene.json` ile `aylin` → `bar-scene-aylin.py`.
Sahnenin kendi listesi `bar-scene.py`'de duruyor ve karışmıyor. Aynı karakter yeniden denendiğinde
kendi dosyasının üstüne yazılıyor — türetilmiş dosya, numaralanmıyor.

## Bilinmeyen ad

Yapı dosyasında olmayan bir karakter istenirse cevap sözlerle geliyor ve **bilinen adları
sayıyor** — `build_prompts`'un eksik ad cümlesiyle aynı kural. Hiçbir dosya yazılmıyor.

Fark bir tek: bu cümlede kare numarası yok, çünkü ortada kare yok.

## Hangi kipte

Yalnız edit. Dosya yazan bir araç, ve yazma araçlarının bugünkü evi orası.

## Kırmızıya dönecek testler

**`test_build_prompts.py` — altı**

1. Her kıyafet için bir prompt, `outfits` haritasının sırasıyla.
2. Kıyafeti olmayan dosya tek satır veriyor: kalite artı kimlik.
3. Kalitesi olmayan dosya yine kuruyor, atlanan alan kuralı burada da geçerli.
4. Bilinmeyen karakter reddediliyor, ve cümle bilinen adları sayıyor.
5. Çıktının adı kaynağı ve karakteri birlikte söylüyor.
6. Uzantısız ya da kirli bir kaynak adı da temiz bir `.py` veriyor.

**`test_tools.py` — dört**

7. Araç modele tanıtılanlar arasında — küme testi sekizinci adı bekliyor.
8. Çağrı dosyayı yazıyor ve doğan dosyayı bildiriyor.
9. Bilinmeyen karakter dosya doğurmuyor, cevap sözlerle geliyor.
10. Sonucu kaç prompt yazıldığını söylüyor.

**`test_modes.py` — bir**

11. Edit kipi bu aracı veriyor; ask ile plan vermiyor.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `build_prompts` | Sahne listesi aynı yoldan çıkmaya devam ediyor |
| `render_module` | Çıktının biçimi ortak; iki kurucu da onu kullanıyor |
| `prompts_name` | Sahne listesinin adı değişmiyor |
| Şema metni | Aracı anlatan yer skill metni; şema dosyanın biçimini anlatıyor |
| Ön yüz | `dist` derlenmiyor |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
```

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.
