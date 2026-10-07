# Defterler `main` dalını klonlar — UYGULAMA turu (uygulama planı)

**Goal:** İki defterin `BRANCH` satırını `main` yapmak ve eskimiş yorumlarını doğru olanla
değiştirmek; önceki commit'in dört kırmızı testi yeşile döner.

**Architecture:** Tek hücre, iki defter. Kod yok, test yok — değişen şey defterlerin metni.

**Tech Stack:** Jupyter JSON (Edit ile, hücre kaynağı üzerinde).

**Tasarım:** [UYGULAMA turu spec'i](../specs/2026-09-11-defterler-main-dalini-klonlar-uygulama-design.md)

## Global Constraints

- **Test dosyalarına dokunulmaz.**
- `BRANCH       = "main"` — yedi boşluk sözleşmenin parçası.
- Dil: defter yorumları **İngilizce** (geliştirici okuyor), çıktı metinleri **Türkçe** — ikisi de
  şimdiki haliyle kalıyor.
- Commit mesajında **çift tırnak yok**, ve mesaj bir dosyadan verilir (`git commit -F`): boruya
  yazılan PowerShell here-string'i mesajın başına UTF-8 BOM koyuyor.

## File Structure

| Dosya | İşlem |
|---|---|
| `queen-agent/queenagent.ipynb` | CONFIG: `BRANCH` satırı + üstündeki yorum |
| `queen-editor/queeneditor.ipynb` | CONFIG: `BRANCH` satırı + üstündeki yorum, satır sonu notu |

---

### Task 1: queen-agent defteri

- [ ] **Step 1:** Yorumu, varsayılanın `main` olduğunu söyleyecek şekilde yeniden yaz; `BRANCH`
      değerini `main` yap.
- [ ] **Step 2:** Run: `python -m pytest queen-agent -q` → yeşil.

---

### Task 2: queen-editor defteri

- [ ] **Step 1:** `# DEV RUN: the Madde 138 trial...` notunu kaldır, `BRANCH` değerini `main` yap,
      yorum bloğuna adı tutan testin dosya adını ekle. Satır sonu yorumunun `#` kolonu `REPO`
      satırıyla hizalı kalır.
- [ ] **Step 2:** Run: `python -m pytest queen-editor -q` → yeşil.

---

### Task 3: Yeşili doğrula ve commit'le

- [ ] **Step 1: Dört komutu koş**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```
Expected: dördü de yeşil; python takımlarında düşen sayısı 0.

- [ ] **Step 2: Ağaçta yalnız iki defter ve doküman olduğunu doğrula**

Run: `git status --short`
Expected: iki `.ipynb` + `docs/superpowers`. Test dosyaları ve `frontend/` temiz.

- [ ] **Step 3: Commit** (mesaj dosyadan)

## Self-Review

**Spec kapsamı:** spec'in iki değişen satırı → Task 1 ve Task 2. Fazlası yok.

**Yakalanan tuzak:** `test_no_other_branch_name...` defterin *yorumlarını* da tarıyor. queen-editor'ün
satır sonu notu bir dal adı içeriyor (`feat/v6` değil ama "Madde 138 trial"), ve yeni not hiçbir dal
adı yazmamalı — yoksa satır `main`'i klonlarken yorum başka bir şey vaat eder.

**Bilerek yapılmayan:** `dist/` yeniden derlenmiyor — arayüz değişmedi.
