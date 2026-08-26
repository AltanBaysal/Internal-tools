# Madde 68 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-26-queenagent-m68-tuketim-uygulama-design.md](../specs/2026-08-26-queenagent-m68-tuketim-uygulama-design.md)
**Kırmızı testler:** `8892452` — arka uçta 10, ön yüzde 2.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Sıra

Sayının yolu boyunca, kaynaktan ekrana. Her adım kendinden öncekine yaslanıyor, o yüzden sıra
keyfî değil.

### 1. `services/xai/client.py` — kare iki şey söyleyebilir hâle gelir

`_delta` üçe bölünür: `_parsed` satırı kareye çevirir (bozuk kare kuralı olduğu gibi taşınır),
`_spoken` `delta`'dan metni ya da çağrıyı okur, `_spent` `usage`'dan üç sayıyı okuyup xAI'nin
adlarından bizimkilere çevirir — `prompt_tokens` → `sent`, `prompt_tokens_details.cached_tokens` →
`cached`, `completion_tokens` → `answered`.

`stream` her kareye ikisini de sorar ve **önce sözü, sonra sayıyı** verir.

*Yeşile döner:* `test_xai_client.py`'nin üç kırmızısı.

### 2. `domain/ports.py` — üçüncü parça tipi yazılır

`Engine.stream`'in docstring'i `{"usage": {...}}`'ı da anlatır. Artık doğru olduğu için şimdi.

*Yeşile döner:* hiçbiri — bu bir belge, ve testi yok.

### 3. `domain/usecases/stream_answer.py` — toplama

Tur içinde `round_spent` en sonuncuyu tutar. Turun döngüsü bittiğinde — **durdurma kontrolünden
önce** — üçü toplama eklenir. Toplam `append_message`'a geçer.

*Yeşile döner:* `test_stream_answer.py`'nin dört kırmızısı. `append_message` bir parametre daha
alacağı için o da bu adımda açılır; varsayılanı var, yani var olan çağrılar dokunulmadan çalışır.

### 4. `data/file_chat_store.py` — diske

Sıfır olmayan `usage` üç anahtarla yazılır; okuma üç alanı tek tek ister, `**` ile değil.

*Yeşile döner:* `test_file_chat_store.py`'nin bir kırmızısı.

### 5. `presentation/routes.py` — tele

`_chat_json`'daki mesaj her zaman `usage` taşır, sıfırken de.

*Yeşile döner:* `test_chats_api.py`'nin iki kırmızısı.

### 6. `ChatScreen.jsx` + `workspace.css` — ekrana

`shorten(count)` bin ve üstünü bir ondalıkla `k`'ya indirir. `TokenCount` `sent + answered`'ı
toplar, sıfırsa hiçbir şey çizmez, değilse `.token-count` satırını cevabın **en altına** koyar —
dosya kartlarından sonra, çünkü kartlar cevabın ürünü, sayı ise cevap hakkında bir not.

CSS 66'nın `.tool-call`'undan türer: mono, `var(--muted)`, 11.5px, vurgusuz.

*Yeşile döner:* `ChatScreen.test.jsx`'in iki kırmızısı.

### 7. `dist` derlenir

`npm run build --prefix queen-agent/frontend`. Kaynakla **aynı commit'e** girer — FOUNDATION'ın
3. kararı ve `test_dist_is_committed.py`.

## Beklenen yeşil

Arka uçta **430**, ön yüzde **489**. Kırmızıların hepsi bu maddenin kendi testleri olduğu için
başka bir dosyanın düşmesi beklenmiyor; düşerse bu bir bulgudur ve plana yazılır.

## Bilerek yapılmayanlar

- **`Usage`'a `total` özelliği eklenmiyor.** Toplamı isteyen tek yer ekran, ve orada zaten iki
  sayının toplamı yazılıyor. Bir özellik, ikinci bir çağıran çıktığında kazanılır.
- **`complete` yoluna tüketim eklenmiyor.** Bu uygulamada hiçbir cevap o yoldan geçmiyor.
- **Sohbet özetine tüketim eklenmiyor.** Özet ne zaman konuşulduğunu söylüyor, ne konuşulduğunu
  değil.
