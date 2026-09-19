# Madde 230 · ComfyUI'ye ulaşılamayınca ekran ne olduğunu ve log'u söyleyecek — test turunun planı

**Spec:** [test turu](../specs/2026-09-17-queen-editor-m230-comfy-ulasilamiyor-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar. Testler henüz olmayan şuna göre yazılıyor: `ComfyClient` bir
`log_path` alıyor, ve `requests.ConnectionError`'ı `ComfyUnreachable`'a *(`services/comfy/errors.py`)*
çeviriyor.

## Adımlar

**1 · `test_comfy_client.py`.** Sahte `http`'nin istenen çağrıda `requests.ConnectionError`
fırlatabilmesi için bir `refuse` bayrağı. Log `tmp_path`'e 40 satır olarak yazılır.

| Test | Olgu |
|---|---|
| `test_an_unreachable_server_is_named_in_the_first_line` | 1 |
| `test_the_connection_errors_own_words_are_kept_whole` | 2 |
| `test_the_last_thirty_lines_of_the_comfy_log_ride_along` | 3 |
| `test_an_unreadable_log_is_said_with_its_path_and_the_error_still_comes` | 4 |
| `test_waiting_on_history_names_an_unreachable_server_too` | 5 |
| `test_an_unreachable_server_is_the_runs_fault_not_the_frames` | 6 |

**2 · `test_notebook_installs_the_producer_groups.py`.**
`test_the_app_is_told_where_comfyui_writes_its_log` → `"QE_COMFY_LOG"` defterde geçiyor.

**3 · Takım koşulur**, dördü de. Beklenen: yalnız **queen-editor'ün arka ucu kırmızı**.

**4 · Kırmızı commit'lenir.**
