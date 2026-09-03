# Madde 155 — Uygulama turu planı

**Kaynak:** [tasarım](../specs/2026-09-03-queenagent-m155-sahne-uygulama-design.md) ·
**Tur:** uygulama *(yeşile götürür)*

Yalnız kod. Hiçbir teste dokunulmuyor.

---

## 1. `ports.py`

- `Engine.write_once(system, user, model)` — bir soru, bir cevap, araç yok.

## 2. `xai_engine.py`

- Aynı istemci, mesajları kendi kurar: `system` ve `user`. Uygulamanın `SYSTEM_PROMPT`'u girmez.

## 3. `tools.py` — `ToolResult`

- Beşinci alan `spent`, varsayılanı `None`.

## 4. `tools.py` — `WRITING`

- Alt isteğin sistem promptu: SDXL promptunun nasıl yazıldığı. Kodda bir sabit.
- Komşuluk kuralı **yok** — istek önceki kareyi görmüyor.

## 5. `tools.py` — `_add_scene`

- Liste kontrolleri, kare açma, `_renumber`, numara aralığını söyleyen cevap.

## 6. `tools.py` — `_write_frame_prompt`

- Boş kareleri bul *(en fazla 100)*.
- İlk istek tek başına, kalanı `ThreadPoolExecutor(max_workers=5)`.
- Cevabı ayrıştır, `_unknown_names` ile doğrula, kare numarasına göre yerleştir.
- Dosyayı **bir kez** yaz.
- Harcamayı topla, raporu kur.

## 7. `tools.py` — araç tanımları ve yönlendirme

- `add_frames` gider; `add_scene` ve `write_frame_prompt` gelir.
- `run_tool(..., engine=None, model="")`.

## 8. `modes.py` ve `skills.py`

- İki ad değişir; iki metin yeniden yazılır.

## 9. `stream_answer.py`

- `result.spent` turun toplamına **eklenir**.

## 10. Koş ve yeşili gör

```
python -m pytest queen-agent -q
```

Defterin iki kırmızısı dışında hepsi yeşil. Diğer üç satır ardışık koşulur.

`feat(m155): …`
