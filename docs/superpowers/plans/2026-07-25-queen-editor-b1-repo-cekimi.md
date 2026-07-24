# Queen Editor — Bölüm 1: Repo çekimi · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Private `Internal-tools` reposunun token'la Colab'da klonlandığını kanıtlayan minik bir notebook (`queen-editor/app.ipynb`) + kullanım kılavuzu (`README.md`).

**Architecture:** Tek bir Colab notebook'u üç hücrede — CONFIG (token + dal), klon (sil-yeniden, `subprocess.run` argüman listesiyle), doğrula (dosya listesi + commit hash). Backend/frontend yok; bu bölüm yalnız klon yolunu sınar. Notebook collab-toolbox `NOTEBOOK-STANDARD.md`'ye uyar (CONFIG tek hücre, gür hata, dil ayrımı); model-indirme/batch makinesi Bölüm 4'te eklenir.

**Tech Stack:** Google Colab · git · Python 3 (stdlib: `os`, `shutil`, `subprocess`)

**Spec:** [2026-07-25-queen-editor-b1-repo-cekimi-design.md](../specs/2026-07-25-queen-editor-b1-repo-cekimi-design.md)

## Global Constraints

- **Dil ayrımı:** `README.md` ve kod yorumları/docstring **İngilizce**; notebook markdown'ı ve `print`/`assert` çıktısı **Türkçe**.
- **Token güvenliği:** `GITHUB_TOKEN` boş placeholder (`""`), hücreye yapıştırılır, **commit'lenmez**. Token yalnız klon URL'inde kullanılır; hiçbir `print`/hata/URL çıktısına düşmez. Klon başarısızlığında git stderr'i basılır ama token `<token>` ile maskelenir.
- **Token türü:** fine-grained, yalnız `Internal-tools`, `Contents: Read-only`.
- **Gür hata (NOTEBOOK-STANDARD §2):** klon/doğrulama başarısızlığı sessiz geçmez — `RuntimeError`/`assert`, mesaj ham (git'in kendi çıktısı), sebep uydurulmaz.
- **Sil-yeniden klon:** `CLONE_DIR` varsa silinip yeniden klonlanır — `git pull`/merge senaryosu yok, tek davranış.
- **Klon = tüm repo, `--depth 1`.** Dal = `BRANCH` (şimdilik `feat/queen-editor-v1`, merge sonrası `main`).
- **Bölüm 1 repoda yalnız `queen-editor/app.ipynb` + `queen-editor/README.md` oluşturur** — `backend/`, `frontend/` yok, boş klasör yok.
- **Commit politikası:** Bu bölüm Colab'da çalıştırılıp kullanıcı doğrulamadan **hiçbir şey commit'lenmez**. Task'ların sonundaki commit adımı kullanıcının "commit" onayını bekler; plan bunu son bir doğrulama+onay adımı olarak taşır.
- **Test gerçeği:** Bölüm 1'in `.py`'si yoktur, dolayısıyla pytest yoktur. Doğrulama = notebook'un kendi `assert`'leri + Colab'da Run all (aşağıdaki adımlar). Bu bilinçlidir; otomatik test Bölüm 3'te backend gelince başlar.

---

### Task 1: README.md (kullanım kılavuzu)

**Files:**
- Create: `queen-editor/README.md`

**Interfaces:**
- Consumes: (yok — ilk task)
- Produces: fine-grained token oluşturma adımları + Colab çalıştırma adımları; Task 2'nin notebook'u bu kılavuzun tarif ettiği token'ı kullanır.

- [ ] **Step 1: `queen-editor/README.md` dosyasını oluştur**

Tam içerik (İngilizce — repo konvansiyonu):

````markdown
# Queen Editor

A two-screen web UI over the `nova-3dcg` ComfyUI photo pipeline: create a project, paste a prompt
list, generate photos into a Google Drive folder. Runs on Google Colab.

Built in cumulative parts — see
[`docs/superpowers/plans/2026-07-24-queen-editor-roadmap.md`](../docs/superpowers/plans/2026-07-24-queen-editor-roadmap.md).
**Part 1** is only this: prove the private repo clones on Colab.

## Part 1 — Repo checkout

`app.ipynb` clones this private repo onto Colab and prints what it fetched. No server, no UI, no
Drive, no ComfyUI yet.

### 1. Create a GitHub token (once)

A fine-grained token scoped to this repo only, read-only:

1. GitHub → **Settings → Developer settings → Fine-grained tokens → Generate new token**.
2. **Repository access → Only select repositories → `Internal-tools`**.
3. **Repository permissions → Contents → Read-only**. No other permission is needed.
4. Generate and copy the token.

If the token leaks, it can only *read* this one repo — nothing else.

### 2. Run on Colab

1. Download `queen-editor/app.ipynb` from GitHub and upload it to Colab (**File → Upload notebook**).
2. Paste the token into the `GITHUB_TOKEN` line of the CONFIG cell.
3. **Runtime → Run all.**
4. The last cell prints the cloned commit and the contents of `queen-editor/`. The token never
   appears in any output.

> **Never commit the notebook with your token in it.** Leave `GITHUB_TOKEN = ""` before saving.
````

- [ ] **Step 2: Gözden geçir**

Kontrol: token adımları fine-grained + `Contents: Read-only`'ye birebir uyuyor mu; İngilizce; roadmap linki doğru göreli yol mu (`queen-editor/README.md`'den `../docs/...`).

---

### Task 2: app.ipynb (klon notebook'u)

**Files:**
- Create: `queen-editor/app.ipynb`

**Interfaces:**
- Consumes: README'de tarif edilen fine-grained token (kullanıcı CONFIG'e yapıştırır).
- Produces: Colab'da `CLONE_DIR = /content/Internal-tools` altına klonlanmış repo; sonraki bölümlerde sunucu bu klonun `queen-editor/`'ından başlar.

Notebook 4 hücreden oluşur: 1 markdown başlık + 3 kod (CONFIG, klon, doğrula). `.ipynb`'yi NotebookEdit aracıyla ya da geçerli bir Jupyter JSON'u yazarak oluştur; her hücre içeriği birebir aşağıdadır.

- [ ] **Step 1: Markdown başlık hücresi (Türkçe)**

```markdown
# Queen Editor — Repo çekimi (Bölüm 1)

Bu notebook private `Internal-tools` reposunu Colab'a klonlar — Queen Editor'ün ilk adımı:
**klon çalışıyor mu?** Sunucu, arayüz, Drive, ComfyUI **yok**; sadece kodun Colab'a indiğini kanıtlar.

## Kullanım
1. Bu `app.ipynb`'yi Colab'a yükle (**File → Upload notebook**).
2. Aşağıdaki **CONFIG** hücresine GitHub token'ını yapıştır (fine-grained, yalnız bu repo,
   `Contents: read` — kurulum için `README.md`).
3. **Runtime → Run all.**
4. En alttaki çıktıda `queen-editor/` içeriği + commit hash görünmeli; **token görünmemeli**.

> Token'ı yapıştırdıktan sonra notebook'u bu haliyle **kaydedip commit'leme** — token sızar.
> `GITHUB_TOKEN`'ı boş bırak.
```

- [ ] **Step 2: CONFIG kod hücresi**

```python
# === CONFIG ===
# Fine-grained GitHub token, this repo only, "Contents: read" (see README for setup).
# Paste it here at runtime; leave it empty ("") before saving/committing -- the token grants
# repo access and must never land in git history.
GITHUB_TOKEN = ""

BRANCH    = "feat/queen-editor-v1"       # dev branch for now; switch to "main" after merge
REPO      = "AltanBaysal/Internal-tools" # <owner>/<repo>
CLONE_DIR = "/content/Internal-tools"    # clone target on Colab's local disk

assert GITHUB_TOKEN, "❌ GITHUB_TOKEN boş — CONFIG hücresine fine-grained token'ını yapıştır (README'ye bak)"
print("✓ CONFIG hazır")
print(f"✓ Dal: {BRANCH}  |  Repo: {REPO}  |  Hedef: {CLONE_DIR}")
```

- [ ] **Step 3: Klon kod hücresi**

```python
# === Clone (delete-and-reclone: the local tree is disposable, always fetch the latest) ===
# subprocess.run with an argument LIST (not shell=True): the token never reaches the shell
# history or a log line. On failure git's stderr is printed RAW, with the token masked.
import os, shutil, subprocess

def _mask(text):
    """Replace the token with <token> so no output ever carries it."""
    return text.replace(GITHUB_TOKEN, "<token>") if GITHUB_TOKEN else text

if os.path.exists(CLONE_DIR):
    shutil.rmtree(CLONE_DIR)              # no pull/merge -- a fresh clone has one behaviour

clone_url = f"https://{GITHUB_TOKEN}@github.com/{REPO}.git"   # never printed (carries the token)
result = subprocess.run(
    ["git", "clone", "--branch", BRANCH, "--depth", "1", clone_url, CLONE_DIR],
    capture_output=True, text=True,
)
if result.returncode != 0:
    # Raw git output, token masked -- never invent a cause (repo comment rule).
    raise RuntimeError("❌ Klon başarısız:\n" + _mask(result.stderr.strip() or result.stdout.strip()))

print("✓ Klon tamam")
```

- [ ] **Step 4: Doğrula kod hücresi**

```python
# === Verify: prove the right branch/commit landed, without leaking anything ===
import os, subprocess

qe_dir = os.path.join(CLONE_DIR, "queen-editor")
assert os.path.isdir(qe_dir), f"❌ {qe_dir} yok — yanlış dal ya da eksik dosya (klon queen-editor/ getirmedi)"
assert os.path.exists(os.path.join(qe_dir, "app.ipynb")), \
    "❌ queen-editor/app.ipynb yok — klon beklenen içeriği getirmedi"

commit = subprocess.run(
    ["git", "-C", CLONE_DIR, "rev-parse", "--short", "HEAD"],
    capture_output=True, text=True,
).stdout.strip()

print(f"✓ Klonlanan commit: {commit}  (dal: {BRANCH})")
print("✓ queen-editor/ içeriği:")
for name in sorted(os.listdir(qe_dir)):
    print(f"   - {name}")
```

- [ ] **Step 5: Notebook'un geçerli JSON olduğunu doğrula (lokal)**

Run: `python -c "import json; json.load(open('queen-editor/app.ipynb', encoding='utf-8')); print('ok')"`
Expected: `ok` — dosya geçerli bir `.ipynb`. (Kod mantığının gerçek testi Colab'da; bu adım yalnız dosyanın bozuk olmadığını garantiler.)

---

### Task 3: Colab doğrulaması + commit (kullanıcı kapısı)

**Files:** (yok — doğrulama + commit)

Bu task kod üretmez; Bölüm 1'i kullanıcının Colab'da denemesi ve onayıyla kapatır. Commit politikası gereği buraya kadar hiçbir şey commit'lenmez.

- [ ] **Step 1: Kullanıcı Colab doğrulaması**

Kullanıcı, `queen-editor/app.ipynb`'yi Colab'a yükler, fine-grained token'ını CONFIG'e yapıştırır, **Run all** yapar. Beklenen:
- Çıktıda `queen-editor/` içeriği (`app.ipynb`, `README.md`), kısa commit hash ve `feat/queen-editor-v1`.
- Token hiçbir çıktıda görünmez.
- (Negatif) `GITHUB_TOKEN = ""` iken: Türkçe "token gerekli" hatası, klon denenmez.
- (Negatif) Yanlış/expired token: git'in kendi 401/403 mesajı, token maskeli.

- [ ] **Step 2: Kullanıcı onayıyla commit**

Kullanıcı "çalışıyor, commit" dedikten sonra, spec + plan + yeni dosyalar birlikte, açık pathspec ile:

```bash
git add -- queen-editor/README.md queen-editor/app.ipynb \
  docs/superpowers/specs/2026-07-25-queen-editor-b1-repo-cekimi-design.md \
  docs/superpowers/plans/2026-07-25-queen-editor-b1-repo-cekimi.md
git commit -m "feat(queen-editor): Bölüm 1 — repo çekimi notebook'u + kılavuz" -- \
  queen-editor/README.md queen-editor/app.ipynb \
  docs/superpowers/specs/2026-07-25-queen-editor-b1-repo-cekimi-design.md \
  docs/superpowers/plans/2026-07-25-queen-editor-b1-repo-cekimi.md
```

(Paralel pencere riskine karşı `git add` + bare `git commit` değil, pathspec kullanılır.)

---

## Doğrulama özeti

| Ne | Nasıl |
|---|---|
| README doğru | Token adımları fine-grained + Contents:read'e uyar; İngilizce |
| Notebook geçerli dosya | `json.load` ile lokalde |
| Klon çalışıyor | Colab Run all → `queen-editor/` içeriği + commit hash |
| Token sızmıyor | Colab çıktısında token yok; boş/yanlış token negatif testleri |
| Bölüm 1 kapanır | Kullanıcı Colab'da doğrular → onayla → commit |
