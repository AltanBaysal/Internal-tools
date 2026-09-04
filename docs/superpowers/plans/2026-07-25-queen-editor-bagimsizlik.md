# Queen Editor — collab-toolbox'tan bağımsızlık · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Queen Editor'ün Drive kökü kendi klasörü olsun (`MyDrive/queenEditor/`) ve `collab-toolbox`'tan bağımsız olduğu yazılı bir kural hâline gelsin — `photoGenV2` Queen Editor tarafında hiç geçmesin, nova-3dcg tarafında hiç değişmesin.

**Architecture:** Kod tarafı tek değer değişikliği: `config.DRIVE_ROOT` varsayılanı ve notebook'un `DRIVE_FOLDER`'ı. Kök zaten `QE_DRIVE_ROOT` ortam değişkeninden okunuyor (Bölüm 3), yani mimari dokunulmaz. Geri kalanı yazı işi: bağımsızlık ilkesi `CODE-STANDARD.md`'ye, yeni yol da şemsiye spec / yol haritası / Bölüm 3 belgelerine geçer.

**Tech Stack:** Python 3 · Flask · pytest · Google Colab (Drive mount) · Markdown/Jupyter dokümanları

**Spec:** [2026-07-25-queen-editor-bagimsizlik-design.md](../specs/2026-07-25-queen-editor-bagimsizlik-design.md)

## Global Constraints

- **Yeni kök `MyDrive/queenEditor/<proje>/`** — notebook değişkeni `DRIVE_FOLDER = "queenEditor"`, `config.py`'deki tam yol yalnız yedek varsayılan (`/content/drive/MyDrive/queenEditor`).
- **Klasör adı tek düğme, hiçbir yere gömülmez** (kullanıcı kararı: "değiştirmesi kolay olsun, hardcoded olmasın"). Adı değiştirmek = notebook CONFIG'inde `DRIVE_FOLDER`'ı değiştirmek, başka hiçbir yere dokunmadan. Bunun sonucu: docstring, yorum ve kural metinleri klasör adını **tekrar etmez** — "Drive kökü" der, kök yolunu `QE_DRIVE_ROOT`'tan alır. `docs/superpowers/**` bir istisna: onlar tarihli kayıt, adı anmaları normal.
- **`collab-toolbox/` ve nova-3dcg dokümanları değişmez.** Oradaki `photoGenV2` geçişleri o araca ait; dokunulursa çalışan bir notebook bozulur. Değişecek dosyalar yalnız bu planda listelenenler.
- **Yarım kalan düzenleme var:** önceki oturumda `queen-editor/backend/config.py`, `queen-editor/backend/features/projects/data/project_store.py` ve `queen-editor/README.md` içindeki `photoGenV2` zaten `queenEditor` yapılmış olabilir (commit'lenmedi). Her adımda **önce oku, gerekiyorsa değiştir** — aynı değişikliği ikinci kez uygulamaya çalışmak hata verir.
- **Yeni test yok, doğrulama arama ile:** değişen şey bir varsayılan yol dizesi. Testler `tmp_path` kullanıyor, gerçek köke bağlı değil — yolu test etmek kendini tekrar eden bir doğrulama olurdu. Kanıt: `queen-editor/` altında `photoGenV2` aramasının **sıfır** sonuç vermesi + mevcut 42 testin geçmesi.
- **Frontend değişmiyor** → `npm run build` **çalıştırılmaz**, `dist/` yeniden üretilmez (kökü yalnız backend biliyor; gereksiz bir dist churn'ü commit'e girmesin).
- **Dil ayrımı:** kod yorumları/docstring ve `CODE-STANDARD.md` **İngilizce**; notebook markdown/`print` ve `docs/superpowers/**` **Türkçe**.
- **Commit politikası:** Colab'da doğrulanıp "commit" denmeden commit yok. Son task bunu kapı olarak taşır. Commit'ler pathspec ile (`git commit -- <yollar>`), `git add .` yok.

---

### Task 1: Kod ve notebook — yeni Drive kökü

**Files:**
- Modify: `queen-editor/backend/config.py`
- Modify: `queen-editor/backend/features/projects/data/project_store.py`
- Modify: `queen-editor/README.md`
- Modify: `queen-editor/app.ipynb` (NotebookEdit: CONFIG hücresi + başlık markdown'ı)

**Interfaces:**
- Consumes: `config.DRIVE_ROOT` / `QE_DRIVE_ROOT` düzeni (Bölüm 3)
- Produces: çalışan uygulamanın kökü `MyDrive/queenEditor`; sonraki task'lar bu adı doküman metni olarak kullanır.

- [ ] **Step 1: `backend/config.py`'yi oku ve gerekiyorsa kökü değiştir**

Hedef satırlar (dosyanın sonu):

```python
# Every project is a folder under this root. Colab mounts Drive and passes the real path in
# QE_DRIVE_ROOT (app.ipynb); the default is only a sane guess for a Colab runtime.
DRIVE_ROOT = os.environ.get("QE_DRIVE_ROOT", "/content/drive/MyDrive/queenEditor")
```

Zaten `queenEditor` yazıyorsa dokunma.

- [ ] **Step 2: `data/project_store.py` docstring'inden klasör adını çıkar**

Hedef docstring (dosyanın ilk iki satırı) — klasör adı burada **anılmaz**, yoksa ad değişince docstring eskir:

```python
"""ProjectStore over DriveStorage -- the only place that knows a project IS one folder directly
under the Drive root. The root itself comes from config; the domain never learns where it is."""
```

- [ ] **Step 3: `README.md`'de iki yolu kontrol et**

`So far:` paragrafında ve `### 3. Run` bölümünde geçen yol `MyDrive/queenEditor/` olmalı. Metnin kalanı değişmez.

- [ ] **Step 4: `app.ipynb` CONFIG hücresinde `DRIVE_FOLDER`'ı değiştir**

Read ile notebook'u aç (NotebookEdit bunu şart koşar), CONFIG hücresindeki satırı değiştir. Yorum, bu satırın **adın tek düğmesi** olduğunu söyler:

```python
DRIVE_FOLDER = "queenEditor"                # proje kökü (MyDrive altında) — adı buradan değiştir
```

Hücrenin geri kalanı (`BRANCH`, `REPO`, `CLONE_DIR`, `APP_PORT`, assert, print'ler) aynı kalır — hizalama bozulmasın diye `=` sütunu korunur.

- [ ] **Step 5: `app.ipynb` başlık markdown'ındaki yolu değiştir**

İlk (markdown) hücrede geçen `MyDrive/photoGenV2/<ad>/` ifadesi `MyDrive/queenEditor/<ad>/` olur. Hücrenin diğer satırları değişmez.

- [ ] **Step 6: `queen-editor/` altında `photoGenV2` kalmadığını doğrula**

Grep: pattern `photoGenV2`, path `queen-editor`
Expected: **hiç sonuç yok**. Sonuç çıkarsa o dosya bu task'ta atlanmış demektir — düzelt ve aramayı yinele.

- [ ] **Step 7: Testleri çalıştır**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS, **42 test** (yol testlere girmiyor; bu adım değişikliğin hiçbir şeyi kırmadığını gösterir).

---

### Task 2: Bağımsızlık ilkesini `CODE-STANDARD.md`'ye yaz

**Files:**
- Modify: `queen-editor/CODE-STANDARD.md`

**Interfaces:**
- Consumes: spec'in "Bağımsızlık sınırı" tablosu
- Produces: geliştiricinin kod yazmadan önce okuduğu yerde duran kalıcı kural. (Tarihli bir spec'te kalan ilke unutulur; `CODE-STANDARD.md` "read this before adding code" dosyası.)

- [ ] **Step 1: `## Stack` bölümünden sonra yeni bir bölüm ekle** (İngilizce)

`## Services (backend/services/)` başlığının **hemen üstüne**:

```markdown
## Independence from collab-toolbox
Queen Editor wraps the same ComfyUI photo pipeline as `collab-toolbox/photo_generator/nova-3dcg/`,
but it depends on nothing there at runtime — no imported cell, no shared file, no shared Drive
folder. What we inherit is knowledge, not code:

| Inherited (knowledge) | Never (dependency) |
|---|---|
| The ComfyUI graph — copied into `queen-editor/` as our own file (lands in Part 4, with generation) | Reading `collab-toolbox/photo_generator/nova-3dcg/workflow_api.json`, or Drive's copy of it |
| Injection node ids (`PROMPT_NODE` `"3"`, `NEGATIVE_NODE` `"4"`, `SEED_NODE` `"40"`) | `api.ipynb`'s CONFIG cell |
| Setup facts (7 custom-node packages, 5 models, headless ComfyUI) as our own cells in `app.ipynb` | Running or referencing the notebook's cells |
| Proven behaviour: `/prompt` → `/history` → `/view`, infra-vs-frame error split, stop after 3 in a row | Copying those functions — we write them into our own layers |

Every direct subfolder of our Drive root is a project, so the root must be ours alone: point it at
the notebook's folder and its `output/` shows up as a phantom project card. The root is never
hardcoded — the server reads `QE_DRIVE_ROOT`, and `app.ipynb`'s CONFIG cell is the one place that
names the folder (`DRIVE_FOLDER`, currently `queenEditor`). Renaming it is a one-line change there,
so do not repeat the name in comments, docstrings or here.

The batch behaviour is the notebook's, the code is ours: same rules, written into
`services/comfy/` (graph injection) and `features/generation/` (plan, queue, policy), where they can
be tested. Rule of thumb: **graph and reasoning shared, code and folders separate.**
```

- [ ] **Step 2: Dosyanın tutarlı olduğunu gözden geçir**

Read ile `queen-editor/CODE-STANDARD.md`'yi aç; yeni bölüm `## Stack` ile `## Services` arasında duruyor, başlık seviyeleri (`##`) tutarlı ve tablo satırları kapanmış olmalı.

---

### Task 3: Şemsiye spec, yol haritası ve Bölüm 3 belgeleri

**Files:**
- Modify: `docs/superpowers/specs/2026-07-24-queen-editor-v1-design.md`
- Modify: `docs/superpowers/plans/2026-07-24-queen-editor-roadmap.md`
- Modify: `docs/superpowers/specs/2026-07-25-queen-editor-b3-proje-design.md`
- Modify: `docs/superpowers/plans/2026-07-25-queen-editor-b3-proje.md`

**Interfaces:**
- Consumes: Task 1'in belirlediği yol (`MyDrive/queenEditor/`)
- Produces: yolun ve gerekçenin tek anlatısı — hangi belge okunursa aynı şey yazıyor.

- [ ] **Step 1: Şemsiye spec'in başlığına revizyon notu ekle**

`**Tarih:** 2026-07-24 · **Durum:** onaylandı, implementasyon planı bekliyor` satırının altına:

```markdown
**Revizyon:** Drive kökü `photoGenV2` değil `queenEditor` — bkz. [collab-toolbox'tan bağımsızlık](../specs/2026-07-25-queen-editor-bagimsizlik-design.md) (2026-07-25).
```

- [ ] **Step 2: Şemsiye spec'in Drive kökü karar satırını değiştir**

Kararlar tablosundaki satır (`| Proje = Drive klasörü \`photoGenV2/<ad>/\`; ad Türkçe ve boşluk serbest | …`) şununla değiştirilir:

```markdown
| Proje = Drive klasörü `queenEditor/<ad>/`; ad Türkçe ve boşluk serbest | Tasarımın brief'i + kullanıcı kararı. Kök Queen Editor'ün kendisi: `photoGenV2` nova-3dcg notebook'unun klasörü ve içinde `output/` var — her alt klasör proje sayıldığı için orada hayalet kart çıkardı ([bağımsızlık spec'i](../specs/2026-07-25-queen-editor-bagimsizlik-design.md)). Sadece dosya sisteminde geçersiz karakterler (`/ \ : * ? " < > \|`), baş/son boşluk ve nokta engellenir; 1–64 karakter. Tasarımdaki örnek adlar (`kapak çekimi`, `lookbook-mayıs`) aynen çalışır. |
```

- [ ] **Step 3: Şemsiye spec'in kalan iki `photoGenV2` geçişini değiştir**

`### Drive düzeni` şemasındaki `MyDrive/photoGenV2/` → `MyDrive/queenEditor/`, ve Doğrulama listesindeki 3. madde (`Drive'da photoGenV2/kapak çekimi/ oluşur`) → `queenEditor/kapak çekimi/`.

- [ ] **Step 4: Yol haritasındaki yolu değiştir**

`## Bölüm 3 — Proje` bölümündeki satır:

```markdown
- **Ne çalışır:** "Yeni proje" → ad gir → `queenEditor/<ad>/` klasörü oluşur → kart listede belirir.
```

- [ ] **Step 5: Bölüm 3 spec'indeki tüm `photoGenV2` geçişlerini `queenEditor` yap**

Dosyadaki her geçiş Queen Editor'ün kökünü anlatıyor (Amaç, Kararlar, dosya yapısı yorumu, data bölümü) — tümü değişir. Nova-3dcg'ye ait bir geçiş yok.

- [ ] **Step 6: Bölüm 3 spec'ine gerekçeyi ekle**

Kararlar tablosundaki `Drive kökü config.DRIVE_ROOT, QE_DRIVE_ROOT ortam değişkeniyle geçersiz kılınır; notebook CONFIG'inde DRIVE_FOLDER = "queenEditor"` satırının gerekçe hücresinin sonuna:

```markdown
Kök Queen Editor'ün kendi klasörü — nova-3dcg'nin `photoGenV2`'si değil; sebep [bağımsızlık spec'inde](../specs/2026-07-25-queen-editor-bagimsizlik-design.md) (yabancı alt klasör hayalet proje kartı üretir). Ad tek düğme: notebook CONFIG'indeki `DRIVE_FOLDER`; kod, yorum ve docstring adı tekrar etmez, yalnız "Drive kökü" der.
```

- [ ] **Step 7: Bölüm 3 planındaki tüm `photoGenV2` geçişlerini `queenEditor` yap**

Plan, uygulanmış işin kaydı; kod `queenEditor` derken planın `photoGenV2` demesi drift olur. Geçtiği yerler: Goal, `config.py` kod bloğu, `project_store.py` docstring bloğu, Task 9 arayüz satırı ve notebook/README adımları, Task 10 doğrulama listesi.

- [ ] **Step 8: Repo genelinde son durumu doğrula**

Grep: pattern `photoGenV2`, path `.` (repo kökü)
Expected: `queen-editor/` altında **sıfır** sonuç. Kalan geçişler iki kümede olmalı: (1) nova-3dcg'nin kendi dosyaları — `collab-toolbox/photo_generator/nova-3dcg/*` ve nova-3dcg dokümanları (`docs/superpowers/specs/2026-07-21-nova-3dcg-photo-design.md`, `2026-07-22-nova-3dcg-api-design.md`, `docs/superpowers/plans/2026-07-21-nova-3dcg-manual.md`, `2026-07-22-nova-3dcg-api.md`); (2) Queen Editor belgelerinde **eski kökü açıklayan** cümleler (şemsiye spec'in revizyon notu ve karar gerekçesi, B3 spec'in gerekçesi, bağımsızlık spec'i + planı) — bunlar "neden photoGenV2 değil" diyor, silinirse karar gerekçesiz kalır. Yol olarak geçen tek bir `photoGenV2` kalmamalı.

---

### Task 4: Colab doğrulaması + commit (kullanıcı kapısı)

**Files:** (yok — doğrulama + commit)

**Interfaces:**
- Consumes: Task 1-3
- Produces: bağımsızlık değişikliğinin kapanışı; Bölüm 3'ün Colab doğrulaması artık doğru kök üzerinde yapılır.

- [ ] **Step 1: Yerel test turu**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (42 test). `npm run build` **çalıştırılmaz** — frontend dosyalarına dokunulmadı.

- [ ] **Step 2: Commit + push (Colab'ın görebilmesi için doğrulamadan önce)**

Notebook uygulamayı repodan klonluyor; push edilmeyen kök Colab'da görünmez. Kullanıcının onayıyla, pathspec ile iki commit:

```bash
# docs
git add -- docs/superpowers/specs/2026-07-25-queen-editor-bagimsizlik-design.md \
  docs/superpowers/plans/2026-07-25-queen-editor-bagimsizlik.md
git commit -m "docs(queen-editor): collab-toolbox'tan bağımsızlık — spec + plan" -- \
  docs/superpowers/specs/2026-07-25-queen-editor-bagimsizlik-design.md \
  docs/superpowers/plans/2026-07-25-queen-editor-bagimsizlik.md \
  docs/superpowers/specs/2026-07-24-queen-editor-v1-design.md \
  docs/superpowers/specs/2026-07-25-queen-editor-b3-proje-design.md \
  docs/superpowers/plans/2026-07-24-queen-editor-roadmap.md \
  docs/superpowers/plans/2026-07-25-queen-editor-b3-proje.md
# fix (kod + notebook + standart)
git commit -m "fix(queen-editor): Drive kökü kendi klasörü (queenEditor), collab-toolbox bağımsızlığı yazılı" -- \
  queen-editor/backend/config.py \
  queen-editor/backend/features/projects/data/project_store.py \
  queen-editor/app.ipynb queen-editor/README.md queen-editor/CODE-STANDARD.md
git push origin feat/queen-editor-v1
```

- [ ] **Step 3: Kullanıcı Colab doğrulaması**

`app.ipynb` → Run all. Beklenen:
1. `✓ Proje kökü: MyDrive/queenEditor` (CONFIG) ve `✓ Drive bağlı — proje kökü: /content/drive/MyDrive/queenEditor` (mount).
2. Linke gir → Projeler ekranı **boş** (`henüz proje yok`) — `output` diye hayalet kart **yok**.
3. **+ Yeni proje** → `kapak çekimi` → kart belirir; Drive'da `MyDrive/queenEditor/kapak çekimi/` oluşur.
4. Drive'da `MyDrive/photoGenV2/` **değişmemiş**: `workflow_api.json` ve `output/` yerinde, yeni klasör eklenmemiş.
5. Bölüm 3'ün kalan doğrulama adımları (çakışan ad → 409 mesajı, geçersiz karakter → 400 mesajı, ikinci proje en üstte, sayfa yenile → duruyor, karta tıkla → hiçbir şey olmaz, Flask durunca kırmızı hata kartı) aynen geçer.

---

## Doğrulama özeti

| Ne | Nasıl |
|---|---|
| Queen Editor'de eski kök kalmadı | Grep `photoGenV2` · path `queen-editor` → 0 sonuç |
| nova-3dcg dokunulmadı | Grep `photoGenV2` · repo kökü → yalnız `collab-toolbox/**` + nova-3dcg belgeleri |
| Kod kırılmadı | `cd queen-editor && python -m pytest -q` → 42 test |
| İlke yazılı | `queen-editor/CODE-STANDARD.md` içinde "Independence from collab-toolbox" bölümü |
| Belgeler tek anlatı | Şemsiye spec · yol haritası · B3 spec · B3 planı hepsi `queenEditor` diyor, gerekçe bağımsızlık spec'ine linkli |
| Uçtan uca | Colab Run all → boş Projeler ekranı (hayalet kart yok) → proje `MyDrive/queenEditor/` altında oluşur |
