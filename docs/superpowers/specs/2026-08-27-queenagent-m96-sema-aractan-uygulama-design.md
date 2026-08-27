# Madde 96 — Şema ve kural kitabı araçtan gelir · **uygulama turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 6, Madde 96 ·
**Turun birincisi:** [test turu](2026-08-27-queenagent-m96-sema-aractan-testler-design.md) —
otuz kırmızı commit'lendi *(`2981d55`)*.
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder.

---

## Yeni dosya: `schema.py`

Alanın içinde, `skills.py`'nin komşusu. Üç şey tutuyor:

- **`STRUCTURE`** — yapı dosyasının biçimi: örnek JSON, hangi haritanın ne tuttuğu, `people`'ın
  nerede durduğu, ilk ismin promptu açtığı.
- **`RULEBOOK`** — altı madde. `skills.py`'den olduğu gibi taşınıyor, altıncısı ekleniyor.
- **`SCHEMA`** — ikisi tek metin: biçim, sonra *"kurmadan önce şu kurallara karşı tut"*, sonra
  kural kitabı. Aracın döndürdüğü şey bu.

Neden ayrı bir dosya: `skills.py` bir skill'in ne dediğini tutuyor, bu ise **yapı dosyasının**
ne olduğunu. İkisi ayrı sorular, ve ikinci soruyu Madde 101'in akış skill'i de soracak.

## `skills.py` küçülüyor

`GENERATE_PROMPTS_PLUS` şema bloğunu ve kural kitabını kaybediyor, yerine bir paragraf alıyor:
yazmadan önce `read_schema` çağır, biçim burada tekrarlanmıyor.

Kalan her şey duruyor — iskeleti önce yazmak, kareleri beşerli eklemek, promptu elle kurmamak,
ve `build_prompts`'ı çağırmak. `RULEBOOK` sabiti dosyadan tamamen çıkıyor.

## Örnekteki `1girl` düşüyor

Bugünkü şema örneği karakteri `"aylin": "1girl, long teal hair, ..."` diye gösteriyor. Sayı artık
karenin alanı *(K6)*, ve kural kitabının altıncı maddesi tam olarak bunu ihlal sayıyor — örnek
kendi kuralını çiğneyemez. Kimlikten sayı düşüyor, kareye `"people": "1girl"` giriyor.

Kalite örneğine **dokunulmuyor**. Araştırma Pony'nin üç skor etiketi istediğini söylüyor ve
bugünkü örnek eksik, ama o ayrı bir karar; bu madde metni taşıyor, içeriğini tartışmıyor.

## `read_schema`

- **Parametresiz.** Tek bir biçim var; hangisi diye sormak tek cevabı olan bir soru olurdu.
- Sonucu tek kelime: `Schema`. Metnin kendisi modele gidiyor, karta düşen şey ne olduğunun adı —
  okuma aracının satır sayısı söylemesiyle aynı kural.
- `WRITES_FILES`'a **girmiyor**: dosya doğurmuyor, sohbette kart açmıyor.

## Kip

`READS`'e katılıyor, yani üç kipte de elde. Okuyan, hiçbir şeyi değiştirmeyen bir araç; kipin
esirgemek için bir sebebi yok.

## Tur sayısı

`MAX_ROUNDS` on altı kalıyor. Zincire bir okuma ekleniyor — listele, şemayı oku, iskeleti yaz,
kareleri parti parti ekle, kendini denetle, kur — ve on altı bunu hâlâ taşıyor.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `build_prompts` | Madde 95'te bitti; bu madde yalnız metni taşıyor |
| `prompt.py` taban yönergesi | Ortak davranışın yeri orası, yapı dosyasının biçimi değil |
| Ön yüz | Araç listesi modele gidiyor, seçiciye değil — `dist` derlenmiyor |
| `WRITES_FILES` | Okuyan bir araç oraya girmiyor |

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
```

Otuz kırmızı yeşile döner. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.
