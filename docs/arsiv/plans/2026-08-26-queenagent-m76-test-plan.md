# Madde 76 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-26-queenagent-m76-tuketim-istenir-testler-design.md](../specs/2026-08-26-queenagent-m76-tuketim-istenir-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Yeni ad yok

68 `Usage`'ı doğurdu ve o duruyor. Bu tur var olan iki fonksiyonun davranışına dokunuyor —
`XaiClient._request` ve `_spoken` — yani içe aktarılamayan bir ad yüzünden toplama hatası riski
yok. Adların turda doğması kuralı burada boşta.

## Dosyalar

`backend/tests/test_xai_client.py` · `backend/tests/test_stream_answer.py`

Ön yüze dokunulmuyor: ekran zaten çiziyor, eksik olan sayının kendisiydi.

## Testler

### `test_xai_client.py` — üç test

Var olan `_Lines`, `_delta_line` ve `_client` yardımcıları kullanılır.

**Akan istek sayıyı istiyor.** Gövde `stream_options` taşıyor ve içindeki `include_usage` doğru.
Bugün alan hiç yok, yani kırmızı.

**Akmayan istek istemiyor.** `complete`'in gövdesinde `stream_options` yok. **Doğduğu anda yeşil**
— bir bekçi. İkinci tur alanı `_request`'in ortak gövdesine koyarsa kırmızıya döner, ve o hata
akmayan bir uç noktada 400 sebebi olurdu.

**Kapanış karesi cevabı düşürmüyor.** `{"choices": [], "usage": {...}}` biçiminde bir kare okunuyor.
Beklenen: yalnız tüketim parçası, hiç metin parçası yok. Bugün `_spoken` `choices[0]` diyor, yani
`IndexError` — kırmızı, ve **hatanın kendisi maddenin sessiz yarısı**: o kare cevabın tamamını
düşürürdü, sadece sayıyı değil.

### `test_stream_answer.py` — bir test ve bir yorum düzeltmesi

**Sayı gelmeden durdurulan cevap sıfır taşıyor.** Var olan `StopsAfter` ile kurgulanır: akış
konuşuyor, durdurma düşüyor, kapanış karesine hiç ulaşılmıyor. **Doğduğu anda yeşil** — bugünkü kod
zaten böyle davranıyor. Bekçi değil, **kayıt**: gerçek bir akışta durdurulan cevabın tüketiminin
bilinmediğini söyleyen tek yer bu.

**`test_a_stopped_answer_still_says_what_it_spent`'in yorumu düzeltilir.** Testin kendisi ve
iddiası aynı kalıyor. Değişen gerekçe: "sayı her parçada geliyor, o yüzden kesilen cevap da
söyler" cümlesi yanlıştı. Doğrusu, kapanış karesiyle durdurmanın arasına düşen dar bir an var, ve
o ana denk gelen ölçüm saklanıyor. Test silinmiyor — silmek, doğru çalışan bir davranışı korumasız
bırakırdı.

## Beklenen kırmızı

**Arka uçta 2 yeni kırmızı, 2 yeni yeşil.** Ön yüzde değişiklik yok.

| Test | Durum |
|---|---|
| Akan istek `stream_options` taşıyor | 🔴 alan hiç yok |
| Kapanış karesi cevabı düşürmüyor | 🔴 `IndexError` |
| Akmayan istek `stream_options` taşımıyor | 🟢 bekçi |
| Sayı gelmeden durdurulan cevap sıfır taşıyor | 🟢 kayıt |

**Defterin iki kırmızısı ayrı.** `test_the_notebook_clones_main` ve
`test_the_notebook_ships_pointing_at_no_feature_branch` bugün kullanıcının isteğiyle kırmızı —
defter `feat/queenagent-v5`'i gösteriyor. Bu maddeyle ilgileri yok; toplam sayılırken düşülür.

**Beklenen toplam:** `4 failed, 430 passed` — dört kırmızının ikisi bu madde, ikisi defter.

**Var olan hiçbir test bu yüzden düşmemeli.** İmza değişmiyor, tip değişmiyor. Düşen olursa
mekanik değil gerçek bir kırılmadır.

## Bu turda yapılmayan

`_request`'in `stream_options` alması · `_spoken`'ın boş `choices`'ı tolere etmesi · üç yanlış
yorumun düzeltilmesi (`_spent`'in docstring'i, `ports.py`'nin `Engine.stream` belgesi,
`stream_answer`'ın toplama yorumu) — hepsi ikinci tur. `dist` derlenmez: ön yüz değişmiyor.
