# Adlandırma düzeltmesi — `AT_MOST`, `_STILL`, `_NOT_AS_TEXT`

**Tarih:** 4 Eylül 2026 · **Branch:** `feat/v7` · **Kaynak:** [v7 yol haritası, adlandırma
düzeltmesi](../plans/2026-09-03-v7-roadmap.md)

Kullanıcı *"diğer isimlendirme hatalarını da çözelim"* dedi *(4 Eylül)*. Kural `CRAFT` ve
`WRITING`'in kuralı: **bir adın, doğduğu konuşmaya ihtiyacı varsa o ad sonraki okuyucuda düşer.**

## Üç ad

| Bugün | Yarın | Neden |
|---|---|---|
| `AT_MOST = 100` | `MOST_FRAMES_PER_CALL` | *"En fazla"* neyin en fazlası? Yanında aynı belirsizlikte ikinci bir sabit duruyordu *(`AT_ONCE`, Madde 165'te kalktı)*, ve ikisi tek yorumu paylaşınca hangisinin hangi cümleye ait olduğu ancak okunarak anlaşılıyordu. Yeni ad üçünü de söylüyor: kare, çağrı başına, tavan. |
| `_STILL` | `_STILL_USED_IN` | Bir sözlük, değerleri cümlenin ortası: *"is still in frames"*, *"is still worn in frames"*, *"is still the place in frames"*. `_STILL[which]` okurken elde kalan tek kelime *"hâlâ"* — hâlâ ne? |
| `_NOT_AS_TEXT` | `_REFUSED_AS_TEXT` | Bir bayrak gibi okunuyor *(`if _NOT_AS_TEXT:`)* ama `.format()` ile basılan bir ret cümlesi. Yeni ad ne olduğunu söylüyor. |

**Metinlere dokunulmuyor.** Yalnız adlar. Yorumların adı anan yeri yok — üçü de ne yaptıklarını
anlatıyor, adlarını değil.

## Tek tur, ve sebebi

**Bu üç adı hiçbir test anmıyor.** `AT_MOST`, `_STILL` ve `_NOT_AS_TEXT` için `queen-agent/backend/
tests` altında tek bir `import` ya da geçiş yok: davranışları ölçen testler cümlenin parçasına
*(`"as text" in said`)* ya da sayının sonucuna *(105 sahneden 100'ü yazıldı)* bakıyor, sabite değil.

`CRAFT` ve `WRITING` iki tur koştu çünkü onları **testler `import` ediyordu** — yeni ad yokken
`ImportError`, on üç kırmızı. Burada öyle bir yüzey yok, ve olmayan bir yüzey için test yazmak
**yalnız yeni yazımı tekrar eden** üç test demek olurdu: suite'i güvenli değil, gürültülü yapar.

Yerine geçen ölçü zaten elde ve daha sıkı: **bir çağrı yeri atlanırsa modül `import` edilemez** ve
`test_tools.py`'nin tamamı toplanma anında kırmızıya döner. Bir yeniden adlandırmanın testi budur.

Emsal: Madde 160 ve 4 Eylül'ün belge taşıması — ikisi de tek tur, ikisinin de sebebi yazılı.

## Doğrulama

1. `python -m pytest queen-agent -q` → **785 yeşil + defterin 2 kırmızısı.** Bir yeniden adlandırma
   test eklemez ve silmez; sayı değişirse bir şey yanlış gitmiştir.
2. Dört sabit test satırı, sırayla, birebir. Ön yüz açılmıyor, `dist` derlenmiyor.
3. `Grep` ile `AT_MOST`, `_STILL`, `_NOT_AS_TEXT`: `queen-agent/` altında sıfır — `_STILL_USED_IN`
   ile `_REFUSED_AS_TEXT` hariç, çünkü ikisi eskisini içeriyor.
4. **Eski spec ve planlar dokunulmaz.** m155'in ve m157'nin belgeleri `AT_MOST` ve `_STILL` diyorsa
   o günün kaydıdır — emsali elde: m159'un spec'i hâlâ `CRAFT` diyor.
