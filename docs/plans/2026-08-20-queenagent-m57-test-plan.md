# Madde 57 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-20-queenagent-m57-test-design.md](../specs/2026-08-20-queenagent-m57-test-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Dosya

`queen-agent/backend/tests/test_notebook.py` — Madde 56'nın altına. Hücre işareti:
`SERVE = "# === Serve ==="`.

## Testler

1. **`test_the_root_travels_to_the_app_in_the_environment`** — `"QUEENAGENT_ROOT": DRIVE_ROOT`
   geçiyor. Bağlanmazsa uygulama ev dizinine, yani runtime ile ölen bir yere yazar.

2. **`test_the_server_starts_in_the_background`** — `Popen` var. `run` hücreyi bloklardı.

3. **`test_a_server_that_never_came_up_shows_its_own_log`** — `/api/health` yoklanıyor, ve
   başarısızlık yolunda log dosyası okunup basılıyor. Sebep uydurulmuyor.

4. **`test_the_address_comes_from_cloudflared`** — `cloudflared` ve `trycloudflare` geçiyor.
   Colab'ın kendi proxy'si POST taşımıyor.

5. **`test_the_link_is_printed_saying_it_has_no_password`** — linkin basıldığı yerin yakınında
   parolasız olduğunu söyleyen bir uyarı var. Uyarı linkin yanında durmalı; başka yerde yazılı
   olması o an linki kopyalayana ulaşmaz.

6. **`test_the_cell_stays_open`** — `tail` ile `-f` var. Biten hücre, kapanan runtime, ölen tünel.

7. **`test_running_it_twice_is_safe`** — `pkill` ile önceki süreçler öldürülüyor. Bu oturumda
   yaşandı: eski bir sunucu bütün istekleri karşılamaya devam etti.

8. **`test_the_serve_cell_refuses_to_run_before_config`** — `assert "APP_DIR" in globals()`.

Her testin **olumlu** bir iddiası var; hiçbiri yalnız bir yokluğa dayanmıyor. Madde 56'da öğrenilen
kural.

## Beklenen kırmızı

**Sekizi de.** Sunucu hücresi henüz yok, `_cell(SERVE)` boş metin döndürüyor.

## Bu turda yapılmayan

Deftere dokunulmaz.
