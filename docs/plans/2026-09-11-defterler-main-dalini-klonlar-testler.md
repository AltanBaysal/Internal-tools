# Defterler `main` dalını klonlar — TEST turu (uygulama planı)

**Goal:** Dört test kırmızıya dönecek: queen-agent'ın iki mevcut testi sabiti değişerek, queen-editor'ün
iki yeni testi dosyasıyla birlikte. Defterlere dokunulmuyor.

**Architecture:** queen-agent'ta tek satır — muhafız zaten var, yalnız neyi doğru saydığı değişiyor.
queen-editor'de aynı muhafızın eşi yeni bir dosyada, tek yardımcıyla.

**Tech Stack:** pytest.

**Tasarım:** [TEST turu spec'i](../specs/2026-09-11-defterler-main-dalini-klonlar-testler-design.md)

## Global Constraints

- **Defterlere dokunulmaz.** `queenagent.ipynb` ve `queeneditor.ipynb` bu commit'te olduğu gibi kalır.
- **Kırmızı bırakılır.** `skip`/`xfail` yok.
- Dil: test adları ve docstring'ler **İngilizce**, assert mesajları **Türkçe**.
- Commit mesajında **çift tırnak yok**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-agent/backend/tests/test_notebook.py` | defterin metni | `BRANCH` sabiti değişir |
| `queen-editor/backend/tests/test_notebook_clones_its_branch.py` | defter hangi dalı klonluyor | yeni dosya, 1 yardımcı + 2 test |

---

### Task 1: queen-agent — muhafız `main`'i bekler

- [ ] **Step 1:** `BRANCH = "feat/queenagent-v8"` → `BRANCH = "main"`

Üstündeki yorum bloğu olduğu gibi kalır: mekanizmayı anlatıyor ve hâlâ doğru.

- [ ] **Step 2: İkisinin de düştüğünü gör**

Run: `python -m pytest queen-agent -q`
Expected: FAIL ×2 — `test_the_notebook_clones_the_branch_this_run_is_tried_on` ve
`test_no_other_branch_name_is_left_lying_in_the_notebook`.

---

### Task 2: queen-editor — muhafızın eşi

- [ ] **Step 1: Dosyayı yaz**

`queen-editor/backend/tests/test_notebook_clones_its_branch.py`, `BRANCH = "main"` sabiti,
`_source()` yardımcısı ve spec'in B1/B2 testleri.

- [ ] **Step 2: İkisinin de düştüğünü gör**

Run: `python -m pytest queen-editor -q`
Expected: FAIL ×2 — defterde `BRANCH       = "feat/v6"` yazıyor; ikinci test `{'feat/v6'}` fazlasını
gösterir. Hiçbiri `NameError`/`FileNotFoundError` gibi bir yazım hatasından düşmemeli.

---

### Task 3: Kırmızıyı doğrula ve commit'le

- [ ] **Step 1: Dört komutu koş**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```
Expected: iki python takımı 2'şer düşer, iki frontend takımı yeşil (onlara dokunulmadı).

- [ ] **Step 2: Ağaçta yalnız test ve doküman olduğunu doğrula**

Run: `git status --short`
Expected: iki test dosyası + `docs/superpowers`. Defterler ve `frontend/` temiz.

- [ ] **Step 3: Commit**

## Self-Review

**Spec kapsamı:** A1→Task 1 · B1, B2→Task 2. Spec'te olup planda olmayan madde yok.

**Ad tutarlılığı:** Bir sonraki turun uyması gereken sözleşme tek satır, iki defterde aynı:
`BRANCH       = "main"` — `BRANCH` ile `=` arasındaki yedi boşluk dahil, çünkü testler tam metni
arıyor.

**Yakalanan tuzak:** queen-agent'ın `test_no_other_branch_name...` testi `feat/` ile başlayan her
kelimeyi topluyor. Defter `main`'e döndüğünde o testin boş küme beklemesi, defterin yorumlarında da
hiçbir `feat/...` adı kalmaması demek — bir sonraki tur bunu gözden kaçırmamalı.

**Bilerek zayıf:** spec'in "bilerek yapılmayan" bölümü — `main` üzerinde eski bir `feat/` adı hâlâ
hiçbir testi düşürmüyor.
