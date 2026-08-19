# Madde 44 — Kare listesi konuşulan dilde ve dosyada · Uygulama Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 44](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Test turu:** [2026-08-19-queenagent-m44-kare-dili-testler-design.md](2026-08-19-queenagent-m44-kare-dili-testler-design.md) — kırmızı commit `b50e039`
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 1 · Dil kuralı yönergeye yazılıyor

Sistem yönergesi zaten "kullanıcının dilinde cevapla" diyor (Madde 37). Kare yönergesi bunu **tekrar
etmiyor**, bir istisnayı kapatıyor: bu becerinin çıktısı prompt gibi görünüyor, ve bir şey prompt
gibi göründüğünde model onu İngilizce yazmaya meyilli. Cümle, o meyli adıyla kapatıyor ve
çevirinin nerede yapıldığını söylüyor.

Ayrımın tek cümlelik hâli: **insanın okuduğu liste kullanıcının dilinde, görüntü modelinin okuduğu
prompt İngilizce.**

## 2 · Dosya, senaryonun deseniyle

Madde 41 senaryo için kurdu, burada tekrar kullanılıyor: `create_file` ile yazılır, ad konudan
türer ve `-frames` ekiyle biter (`bar-scene-frames.md`), düzeltme `edit_file` ile dosyaya işler.
Ek, senaryo dosyasıyla kare dosyasını yan yana ayırt edilebilir kılıyor.

"This stays in the chat. Do not create a file." cümlesi düşüyor; yerine sohbete **de** yazılacağı
duruyor — dosya cevabın yerine geçmez.

## 3 · Menü satırları

- **Create character prompt** — "SDXL character tags. Stays in the chat." → dosyadan söz eder.
  Madde 42'nin bıraktığı; ürün o günden beri kullanıcıya yanlış söylüyor.
- **Split into frames** — "Turn the scenario into frames. Stays in the chat." → dosyadan söz eder.

Menünün ikinci satırı becerinin en şaşırtıcı özelliğini taşıyor. Artık şaşırtıcı olan "sohbette
kalıyor" değil, **dosya yazıyor**: kullanıcı bir dosyanın doğacağını önceden bilmeli.

## 4 · Değişen dosyalar

| Dosya | Ne |
|---|---|
| `domain/skills.py` | `SPLIT_INTO_FRAMES` — dil cümlesi, dosya, ad, düzeltme |
| `frontend/features/workspace/skills.js` | İki menü açıklaması |

## 5 · Kabul ölçütü

1. Test turunun sekiz testi de yeşil, başka hiçbir test düşmüyor.
2. İki komut da yeşil.
3. Elle: Türkçe sohbette Türkçe kare listesi + dosyası; üretilen promptlar İngilizce.
