# Madde 377 — bağlantı testi internet adresini dosya saymaz · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `_local_links`'in internet adresini dışarıda bıraktığını tutan bir iddia, kırmızı.

**Architecture:** `queen-editor/backend/tests/test_version_record.py`'ye bir test; henüz yazılmamış
`_local_links(text)` yardımcısına küçük bir metin verir, ve yalnız yerel bağlantının döndüğünü
bekler.

**Tech Stack:** pytest.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m377-web-adresi-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi.
- Kod, yorum ve test adı İngilizce; hata cümlesi Türkçe (dosyanın öteki testleri gibi).
- Bu turda `_local_links` yazılmaz, `test_a_roadmap_can_still_reach_everything_it_links_to` değişmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Tek iddia, kırmızı

**Files:**
- Modify: `queen-editor/backend/tests/test_version_record.py` — `test_a_roadmap_can_still_reach_everything_it_links_to`'nun hemen altı

**Interfaces:**
- Consumes: yok.
- Produces: uygulama turunun yazacağı `_local_links(text) -> set[str]` — bir metindeki yerel `.md`
  bağlantıları, çapasız; internet adresi yok.

- [ ] **Step 1: Testi yaz**

```python
def test_a_web_address_is_not_a_file_a_roadmap_has_to_reach():
    """A roadmap cites a guide on the web by its address, and that address can end in .md too -- v9's
    MiniMax guides do. No move of folders can break it, and looking for it on disk kept the suite red
    over a link nothing here could fix (Madde 377)."""
    written = "[guide](https://example.org/docs/GUIDE.md) and [plan](../plans/x-plan.md#adim-2)"

    assert _local_links(written) == {"../plans/x-plan.md"}, (
        "internet adresi diskte aranacak bir dosya sayıldı"
    )
```

- [ ] **Step 2: Dört satırı koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `python -m pytest queen-editor -q` iki kırmızı — yeni test `NameError: name '_local_links'
is not defined` ile, ve `test_a_roadmap_can_still_reach_everything_it_links_to` eskisi gibi. Öteki üç
süit yeşil.

- [ ] **Step 3: Kırmızıyı commit'le**

```powershell
git add queen-editor/backend/tests/test_version_record.py docs/superpowers/specs/2026-09-29-queenagent-m377-web-adresi-testler-design.md docs/superpowers/plans/2026-09-29-queenagent-m377-web-adresi-testler-plan.md
git commit -m @'
test(queen-editor): Madde 377 red -- a web address in a roadmap is not a file to find on disk

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
