# Madde 487 · Queen Editor notebook'u varsayılan olarak A100 açar — plan

**Spec:** [2026-10-21-queen-editor-m487-a100-default-design.md](../specs/2026-10-21-queen-editor-m487-a100-default-design.md)
· **Dal:** `feat/queen-editor-v10` · Test önce (TDD).

1. `queen-editor/backend/tests/test_notebook_opens_on_an_a100.py` — metadata'nın A100 istediğini ve
   hiçbir hücrenin T4 demediğini soran iki test. Kırmızı.
2. `queen-editor/queeneditor.ipynb`:
   - `metadata`'ya `"accelerator": "GPU"` ve `"colab": {"gpuType": "A100", "provenance": []}`;
   - CONFIG'in GPU kontrolünün mesajında "T4 GPU seç" → "A100 GPU seç".

   Dosya bugünkü biçiminde kalır (girinti 1, ASCII'ye kaçırılmamış metin, diskte CRLF), diff yalnız
   bu iki yer. Yeşil.
3. `queen-editor/README.md` — Run bölümündeki runtime cümlesi A100'e.
4. `python -m pytest queen-editor -q`.
