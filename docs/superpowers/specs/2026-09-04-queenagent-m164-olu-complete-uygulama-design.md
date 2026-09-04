# Madde 164 — ölü `complete` yolu · **uygulama turu**

**Tarih:** 4 Eylül 2026 · **Branch:** `feat/v7` · **Kaynak:** [test turu
spec'i](2026-09-04-queenagent-m164-olu-complete-testler-design.md) · **Yol haritası:** [Madde
164](../plans/2026-09-03-v7-roadmap.md)

Üç kırmızıyı yeşile çeviren silme. Üç katman, üç metot, ve arkalarında öksüz kalan bir parametre.

## Silinen

| Dosya | Ne |
|---|---|
| `ports.py` | `Engine.complete` — sözleşme |
| `xai_engine.py` | `XaiEngine.complete` — uyarlayıcı |
| `client.py` | `XaiClient.complete` — taşıma |

## Arkalarında kalan iki iz, ve ikisi de düzeliyor

- **`_answered`'ın `tools` parametresi öksüz.** Tek çağıranı `complete_once` ve o `None` geçiyor;
  araç gönderen tek yol akış, ve o `_request`'i doğrudan çağırıyor. Parametre gider, `_request`'inki
  `tools=None` varsayılanını alır. **Ölü kod, tanımı gereği:** hiçbir çağrının dolduramadığı bir
  parametre.
- **İki docstring var olmayan bir kardeşe atıf yapıyor.** `complete_once`'ınki *"complete throws the
  usage away…"* diye başlıyor, `Engine.write_once`'ınki *"Apart from `complete` because of what
  rides in front of it…"* diyor. İkisinin de **anlattığı şey doğru** — biri neden usage taşıdığını,
  öteki neden kendi system promptunu getirdiğini — yalnız kıyas ettikleri şey ortadan kalkıyor.
  Kıyas `stream`'e döner: sohbetin yolu odur, ve app'in system promptunu önüne koyan da odur.

  CLAUDE.md'nin kuralı burada bağlayıcı: *bir yorum yalnız bugün doğru olanı söyler.*

## Bilerek yapılmayanlar

- **`complete_once`, `stream`, `_request`, `_answered`'ın gövdesi değişmiyor.** Bu madde hiçbir
  davranışı değiştirmiyor; ölçüsü de o — takım başladığı yeşille kapanıyor.
- **`FakeEngine`/`FakeClient`'ın kalan metotları** duruyor. Sahtelerin sildiği tek şey `complete`'ti
  ve o test turunda gitti.

## Doğrulama

1. `python -m pytest queen-agent -q` → **785 yeşil + defterin 2 kırmızısı.** *(Kırmızı turda 782 + 3;
   toplam sabit — bu tur test eklemiyor, silmiyor.)*
2. Dört sabit test satırı, sırayla, birebir.
3. `Grep` ile `def complete\b` ve `\.complete\(`: `queen-agent/` altında sıfır. `complete_once` ile
   `chat/completions` adresi kalır; ikisi de başka şey.
4. Tek yeşil commit, mesajda çift tırnak yok.
