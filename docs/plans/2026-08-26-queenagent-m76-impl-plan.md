# Madde 76 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-26-queenagent-m76-tuketim-istenir-uygulama-design.md](../specs/2026-08-26-queenagent-m76-tuketim-istenir-uygulama-design.md)
**Kırmızı testler:** `f8f0e1b` — bu maddeden iki tane.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Sıra

### 1. `services/xai/client.py` — istek sayıyı ister

`stream`, gövdeye `stream` bayrağını koyduğu yerde `stream_options: {"include_usage": True}`'yi de
koyar. Aynı sözlükte, aynı satırda — ikisi aynı kararın parçası. `complete` ve ortak `_request`
gövdesi dokunulmaz.

*Yeşile döner:* `test_a_streaming_request_asks_for_the_counts`.
*Yeşil kalır:* `test_a_request_that_is_not_a_stream_does_not_ask`.

### 2. `services/xai/client.py` — `_spoken` boş kareyi geçer

Bugünkü satır `frame.get("choices", [{}])[0]` diyor ve boş listede patlıyor. Listeyi önce bir
değişkene alıp boşsa `None` döner.

*Yeşile döner:* `test_the_closing_counts_frame_does_not_bring_the_answer_down`.

### 3. Üç yorum düzelir

Hiçbir testi yeşile döndürmez; CODE-STANDARD'ın kuralıdır — çelişkide yorum koda uydurulur.

- `client.py` → `_spent` docstring'i: sayının **yalnız kapanış karesinde** ve **ancak istenirse**
  geldiğini söyler. Bugünkü "her karede geliyor" cümlesi gider.
- `ports.py` → `Engine.stream`: "birden çok kez söyleyebilir" gider, "akışın sonunda bir kez" gelir.
  Motorun hiç söylememesi hâlâ geçerli — sahte motorların hepsi öyle.
- `stream_answer.py` → toplama yorumu: "en sonuncu geçerli" kuralının neden **durduğu** yazılır.
  Bugün tek sayı geliyor, yani kural boşta; servis kümülatif diziye dönerse doğru cevabı vermeye
  devam ediyor. Kaldırmak kazancı olmayan bir kırılganlık olurdu.

## Beklenen yeşil

Arka uçta **2 failed, 432 passed** — kalan iki kırmızı defterin dalı
(`test_the_notebook_clones_main`, `test_the_notebook_ships_pointing_at_no_feature_branch`),
kullanıcının kendi isteği. Ön yüzde **489**, dokunulmuyor.

Başka bir dosyanın düşmesi beklenmiyor: imza değişmiyor, tip değişmiyor.

## Bilerek yapılmayanlar

- **Toplama kuralı kaldırılmıyor.** "Tur içinde en sonuncu geçerli" bugün tek sayı geldiği için
  boşta çalışıyor, ama servis eski davranışına dönerse doğru cevabı veriyor. Silmek, karşılığında
  hiçbir şey almadan kırılganlık satın almak olurdu.
- **`stream_options` ayarlanabilir yapılmıyor.** Kapatmak isteyen yok; FOUNDATION 3.
- **`dist` derlenmiyor.** Ön yüz kaynağında tek satır değişmiyor.
