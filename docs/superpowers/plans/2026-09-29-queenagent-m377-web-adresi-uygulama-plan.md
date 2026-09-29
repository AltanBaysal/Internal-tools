# Madde 377 — bağlantı testi internet adresini dosya saymaz · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `_local_links(text)` yazılır, ve roadmap'lerin bağlantı testi ona bağlanır; queen-editor'ün
arka uç süiti yeşile döner.

**Architecture:** `queen-editor/backend/tests/test_version_record.py`'de, öteki yardımcıların
yanında bir yardımcı; bugünkü düzenli ifadeyi taşır, `://` taşıyan bağlantıyı ayıklar.
`test_a_roadmap_can_still_reach_everything_it_links_to` kendi ifadesi yerine onu çağırır.

**Tech Stack:** pytest.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m377-web-adresi-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi.
- Kod, yorum ve test adı İngilizce; hata cümlesi Türkçe (dosyanın öteki testleri gibi).
- `test_every_link_to_a_roadmap_resolves_from_where_it_is_written` değişmez.
- `npm run build` koşulmaz, `dist` commit'lenmez: ön uca dokunulmuyor.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Yardımcı, ve test ona bağlı

**Files:**
- Modify: `queen-editor/backend/tests/test_version_record.py` — `_markdown()`'un altı, ve
  `test_a_roadmap_can_still_reach_everything_it_links_to`'nun döngüsü

**Interfaces:**
- Consumes: kırmızı turun `test_a_web_address_is_not_a_file_a_roadmap_has_to_reach`'i (`11029a5d`).
- Produces: `_local_links(text: str) -> set[str]` — yerel `.md` bağlantıları, çapasız.

- [ ] **Step 1: Kırmızı zaten commit'li**

Test turunun iddiası `11029a5d`'de: `_local_links` yok, `NameError` veriyor; eski test iki MiniMax
adresiyle kırmızı.

- [ ] **Step 2: Yardımcıyı `_markdown()`'un altına yaz**

```python
def _local_links(text):
    """A text's links to .md files, without their #anchor -- the ones a move of folders can break.

    A web address is left out: it can end in .md too (v9's MiniMax guides do), but it is no file on
    disk, and looking for it there kept the suite red over a link nothing here could fix (Madde 377).
    """
    return {link for link in re.findall(r"\(([^()\s#]+\.md)(?:#[^()\s]*)?\)", text)
            if "://" not in link}
```

- [ ] **Step 3: Testi yardımcıya bağla**

`test_a_roadmap_can_still_reach_everything_it_links_to`'da:

```python
        for link in set(re.findall(r"\(([^()\s#]+\.md)(?:#[^()\s]*)?\)", _read(path))):
```

satırı şu olur:

```python
        for link in _local_links(_read(path)):
```

- [ ] **Step 4: Dört satırı koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `python -m pytest queen-editor -q` 1160 passed, kırmızı yok. Öteki üç süit yeşil: 933, 652,
749.

- [ ] **Step 5: Commit'le**

```powershell
git add queen-editor/backend/tests/test_version_record.py docs/superpowers/specs/2026-09-29-queenagent-m377-web-adresi-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m377-web-adresi-uygulama-plan.md
git commit -m @'
fix(queen-editor): Madde 377 -- a roadmap's link test looks on disk only for local files, not web addresses

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
