# v14 Görev 18 — Fotoğraf varyant varsayılanı 4 → 2: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tek kırmızıyı yeşile döndürmek ve yanındaki bayat yorumu düzeltmek.

**Architecture:** Bir sayı adlandırılıyor ve değişiyor; bir yorum ekranda olanı anmaya başlıyor.

**Tech Stack:** React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-18-varyant-varsayilani-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor.**
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/GeneratePanel.jsx` | kutunun ilk değeri | iki değişiklik |
| `backend/.../usecases/start_batch.py` | onay kartının sayısını anlatan yorum | bir cümle |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Varsayılan

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx`

- [ ] **Step 1: Sabit**

`MAX_VARIANTS`'ın altına:

```js
// What the box starts at in a project that has never saved a count. Two rather than four (İstek 8):
// four was the number the app was born with, and the user makes fewer variants of a prompt than
// that in practice. A name rather than a bare string inside the initial state, because "why this
// number" is the whole of what this line says.
const FIRST_VARIANTS = "2";
```

- [ ] **Step 2: Başlangıç değeri**

```js
  const [variants, setVariants] = useState(
    settings.variants === null ? FIRST_VARIANTS : String(settings.variants),
  );
```

Koşul aynı: varsayılan yalnız kaydedilmiş bir sayı yokken devreye giriyor.

---

### Task 2: Bayat yorum

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/start_batch.py`

- [ ] **Step 1: Örneği düzelt**

```python
    # How many frames the queue really took. The panel's own estimate is a preview it is not
    # allowed to enforce, so the confirmation card quotes this instead.
    return len(frames)
```

Cümlenin sebebi duruyor; giden, panelde artık olmayan bir satırı örnek gösteren yarısı.

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil — 384 / 474 / 694 / 478.

---

### Task 3: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

18. maddenin **İş** hücresi ✅ ile başlar, sayaç `17/31` → `18/31`. D bölümü kapanır.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): a new project's photo count starts at two

Four was the number the app was born with; two is what the work actually looks like. It
moves in one place, because the panel is the only place a first value comes from -- the
server has no default and refuses anything that is not an integer between 1 and 26.

Only an empty setting is touched. A project that saved a count of its own opens on that
count, and the layer panel still opens at one: the request asks for the photo panel's
default and says the other one stays, which are two decisions rather than one number.

The number gets a name on the way. As a bare string inside an initial state there was
nowhere to say why it is what it is, and why is the entire content of this change.

One comment nearby is corrected while its subject is being read. It explained why the
confirmation card quotes the server's count rather than the panel's arithmetic -- which is
still true -- by pointing at a preview line that the panel has not drawn for some time.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in iki parçası Task 1 ve Task 2.

**Tip tutarlılığı:** `FIRST_VARIANTS` bir **dize**, çünkü kutu metin tutuyor ve boşaltılabilmesi
gerekiyor — sayı olsaydı `String()` çağrısı bir dalda olur bir dalda olmazdı.

**Kontrol edilen tuzak:** koşul `=== null`. `settings.variants` sıfır olamaz (sunucu 1'in altını
reddediyor), ama gevşek bir doğruluk sınaması yine de yanlış olurdu — kaydedilmemiş hâli anlatan
şey `null`'un kendisi.

**Değişmeyen:** `LayerPanel.jsx`, `settings_store`, `start_batch`'in kuralları.
