# Queen Editor — Bölüm 5.1: Tasarım sadakati (artboard 03/04) · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Proje ekranını tasarımın **artboard 03 (Hazır)** ve **04 (Üretim sürüyor)** hâline oturtmak — başlık, 320px panel, tek satır negatif, satır içi varyant kutusu, `N prompt × M varyant = K foto` sayacı, `wf-stroke` ilerleme kutusu, ortalanmış boş galeri ve üretilen karenin spinner'lı yeri.

**Architecture:** Yalnız sunum katmanı. Backend, uçlar, `useGeneration` ve testlerin **hiçbiri değişmez**; dört bileşen tasarımın ölçüleriyle yeniden yazılır. Panel artık üretim sırasında da ekranda kalır: form sabit, yalnız **alt aksiyon bloğu** Üret ↔ ilerleme kutusu arasında değişir — bu yüzden `ProgressPanel`'i `ProjectScreen` değil `GeneratePanel` çağırır.

**Tech Stack:** React 18 · Vite 5 · vendor `kit.jsx` + `styles.css` (değişmez)

**Tasarım kaynağı:** claude.ai/design → `Queen Editor Basit v1.html` → `simple-screens.jsx` (`ProjectScreen`, `LeftPanel`, `Gallery`, `Tile`) · artboard etiketleri `simple-app.jsx`'te (`03 · Hazır`, `04 · Üretim sürüyor (7/48)`).
**Spec:** [2026-07-25-queen-editor-b5-coklu-foto-design.md](../specs/2026-07-25-queen-editor-b5-coklu-foto-design.md)

## Global Constraints

- **Başlangıç durumu kirli:** Bölüm 5 commit'lendikten sonra `GeneratePanel.jsx` yarım düzeltildi (varyant sayı girişine çevrildi, `VariantPicker` import'u kaldırıldı) ve spec'te iki satır güncellendi. `VariantPicker.jsx` diskte ama **kimse kullanmıyor**. `dist/` bu değişiklikten sonra **derlenmedi**. Bu planın her task'ı ilgili dosyayı **baştan yazar**, o yüzden yarım hâl sorun değil.
- **Vendor değişmez.** `kit.jsx` ve `styles.css` elle düzenlenmez. Tasarımın kullandığı sınıflar mevcut ve doğrulandı: `wf-stroke`, `wf-input`, `wf-img`, `wf-btn--sm`, `wf-hl`, `--bg-3`, `--ink-4`, `--danger-bg`.
- **Ölçüler tasarımdan birebir:** panel `320`, panel `gap 14`, panel `padding 16`, galeri `gap 12` + `repeat(5, 1fr)`, galeri `padding 16`, varyant kutusu `width 56` + `textAlign center` + `fontSize 13`, prompt textarea `rows 11` + `fontSize 11.5` + `flex 1`, negatif `input` + `fontSize 12.5`, ilerleme çubuğu `height 5` + iz `var(--bg-3)`, tile adı `Mono size 10`.
- **Tek bilinçli sapma — kaydırma:** tasarım artboard'ları sabit yükseklikli çerçeve olduğu için galeri `overflow: hidden`. Canlı üründe galeri **`overflowY: auto`** olur; yoksa 48 fotonun çoğu erişilemez. (B3'te `.wf-scrim`'in `position` düzeltmesiyle aynı gerekçe.)
- **Panelin yeri sağ.** Tasarımın bölüm altyazısı "Sol: prompt listesi" der ve bileşenin adı `LeftPanel`'dir, ama render sırası (galeri önce) ve `borderLeft` panelin **sağda** olduğunu söyler; artboard'da görünen de budur. Ad ve altyazı eskimiş.
- **Kapsam dışı (tasarımda var, bizde sonraki bölümler):** kırmızı hatalı kare + **Tekrar dene** (artboard 05) ve **Kaldığı yerden devam et** kartı (artboard 06) → **Bölüm 7**. Prompt'ların kalıcılığı (tasarımın brief'i `localStorage` diyor, bizim spec `prompts.json`) → **Bölüm 6**. "bekliyor" (pending) tile'ları → plan bilgisi gerektiriyor, **Bölüm 6/7**.
- **Frontend testi yok:** bu repoda React test altyapısı hiç kurulmadı (Bölüm 1-5 boyunca da yoktu) ve bu bölümün işi kurmak değil. Her task'ın kapısı `npm run build`'in temiz geçmesi; görsel doğrulama Task 6'daki listeyle Colab'da yapılır.
- **Backend hiç değişmez:** `python -m pytest -q` sonuna kadar **136** kalmalı.
- **Dil:** kod yorumu İngilizce, UI metni Türkçe (metinler tasarımdan birebir: "Prompt listesi", "Negatif prompt", "Varyant", "Üret", "Durdur", "Projeden çık", "henüz fotoğraf yok", "Prompt'ları yaz, Üret'e bas — fotoğraflar burada belirecek", "şimdi:", "… fotoğraf üretilemedi — diğerleri devam ediyor").
- **Commit politikası:** Colab kodu repodan klonluyor → Task 6'da önce commit+push (kullanıcı onayıyla), sonra görsel doğrulama.

## Dosya yapısı

| Dosya | Sorumluluk | Durum |
|---|---|---|
| `features/photo_generation/ProjectScreen.jsx` | Başlık + iki sütunlu gövde (galeri sol, panel sağ). Veri `useGeneration`'dan gelir, dağıtımı burada. | Baştan yazılır |
| `features/photo_generation/GeneratePanel.jsx` | 320px panelin tamamı: üç form alanı + alt aksiyon bloğu (Üret + sayaç ↔ ilerleme kutusu) + durum/hata satırları. | Baştan yazılır |
| `features/photo_generation/ProgressPanel.jsx` | Yalnız `wf-stroke` ilerleme kutusu (sayaç + Durdur + çubuk + "şimdi:"). Panelin içinde yaşar. | Baştan yazılır |
| `features/photo_generation/Gallery.jsx` | 5 sütunlu ızgara, tile (foto + ad), boş durum, üretilen karenin spinner'lı tile'ı. | Baştan yazılır |
| `features/photo_generation/VariantPicker.jsx` | — | **Silinir** |
| `features/photo_generation/useGeneration.js` | — | **Dokunulmaz** (`{job, photos, error, generate, stop}` yeterli) |

---

### Task 1: Yerleşim ve başlık — `ProjectScreen.jsx`

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx` (tamamı)

**Interfaces:**
- Consumes: `useGeneration(project) -> {job, photos, error, generate, stop}` · `navigate(path)` · kit `Hand`, `Btn`
- Produces: `<Gallery project photos current />` ve `<GeneratePanel job error busyElsewhere onGenerate onStop />` çağrıları — Task 2 ve 4 bu imzaları gerçekler.

- [ ] **Step 1: `ProjectScreen.jsx`'i baştan yaz**

```jsx
import { navigate } from "../../shared/router.js";
import { Btn, Hand } from "../../vendor/kit.jsx";
import Gallery from "./Gallery.jsx";
import GeneratePanel from "./GeneratePanel.jsx";
import { useGeneration } from "./useGeneration.js";

const HEADER = {
  display: "grid",
  gridTemplateColumns: "1fr auto 1fr",
  alignItems: "center",
  padding: "14px 32px",
  background: "var(--bg-2)",
  borderBottom: "1px solid var(--border)",
};

// Artboard 03/04: gallery on the left (the content), the 320px panel on the right (the controls).
// The panel stays put while a batch runs -- only its bottom block swaps (see GeneratePanel).
export default function ProjectScreen({ project }) {
  const { job, photos, error, generate, stop } = useGeneration(project);
  // The worker is global: a batch started from another project blocks this one (the server 409s).
  const busyElsewhere = job.status === "running" && job.project !== project;
  const running = job.status === "running" && !busyElsewhere;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={HEADER}>
        <Hand size={20}><span className="wf-hl">Queen Editor</span></Hand>
        <Hand size={20}>{project}</Hand>
        <Btn ghost style={{ color: "var(--danger)", justifySelf: "end" }}
             onClick={() => navigate("/")}>Projeden çık</Btn>
      </div>

      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        {/* The artboard can clip its gallery because it is a fixed-height frame; a real page
            has to scroll, otherwise most of a 48-photo run is unreachable. */}
        <div style={{ flex: 1, minWidth: 0, overflowY: "auto" }}>
          <Gallery project={project} photos={photos} current={running ? job.current : null} />
        </div>
        <GeneratePanel job={job} error={error} busyElsewhere={busyElsewhere}
                       onGenerate={generate} onStop={stop} />
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Derle**

Run: `cd queen-editor/frontend && npm run build`
Expected: PASS. Fazladan geçirilen prop'lar (`current`, `onStop`) JSX'te zararsızdır — eski `Gallery`/`GeneratePanel` onları yok sayar, derleme kırılmaz. Ekran bu noktada henüz doğru değil; başlık ve iki sütun yerine oturmuş olur.

---

### Task 2: Panel formu ve aksiyon bloğu — `GeneratePanel.jsx`

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx` (tamamı)

**Interfaces:**
- Consumes: kit `Btn`, `Icon`, `Mono`, `Note` · `<ProgressPanel job onStop />` (Task 3)
- Produces: `<GeneratePanel job error busyElsewhere onGenerate onStop />`; `onGenerate({prompts, negative, variants})` — `variants` **sayı**, sayıya çevrilemiyorsa `null` (sunucu Türkçe mesajla reddeder).

- [ ] **Step 1: `GeneratePanel.jsx`'i baştan yaz**

```jsx
import { useState } from "react";

import { Btn, Icon, Mono, Note } from "../../vendor/kit.jsx";
import ProgressPanel from "./ProgressPanel.jsx";

const PANEL = {
  width: 320,
  flexShrink: 0,
  borderLeft: "1px solid var(--border)",
  padding: 16,
  display: "flex",
  flexDirection: "column",
  gap: 14,
  overflow: "hidden",
  boxSizing: "border-box",
};

const LABEL = { color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" };

const RAW_ERROR = {
  color: "var(--ink-3)",
  background: "var(--bg)",
  border: "1px solid var(--border)",
  borderRadius: 3,
  padding: "6px 8px",
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
};

const PLACEHOLDER = '["ilk prompt", "ikinci prompt"]';

/** Count for the "12 prompt × 4 varyant = 48 foto" line -- a preview, not a rule.
 *
 * The real parse and every error message live in the backend (domain/prompt_list.py). This only
 * decides whether we can show a number at all: anything it cannot read confidently hides the line,
 * so a wrong count can never be displayed. Trailing commas are stripped because a list pasted out
 * of a notebook usually has one and JSON does not allow it. */
function countPrompts(text) {
  const body = text.trim().replace(/^[A-Za-z_]\w*\s*=\s*/, "").replace(/,(\s*\])/g, "$1");
  try {
    const value = JSON.parse(body);
    if (!Array.isArray(value)) return null;
    return value.filter((item) => typeof item === "string" && item.trim()).length;
  } catch {
    return null;
  }
}

// Artboard 03: prompt list, one shared negative, variant count, Üret. Artboard 04 keeps all three
// fields on screen and swaps only the block underneath them.
export default function GeneratePanel({ job, error, busyElsewhere, onGenerate, onStop }) {
  const [prompts, setPrompts] = useState("");
  const [negative, setNegative] = useState("");
  // Text, not a number: the field has to survive being cleared while typing. Whatever is not a
  // whole number goes to the server as null and comes back with the server's own message.
  const [variants, setVariants] = useState("4");

  const running = job.status === "running" && !busyElsewhere;
  const count = countPrompts(prompts);
  const perPrompt = Number(variants);
  const planned = count !== null && Number.isInteger(perPrompt) && perPrompt > 0
    ? count * perPrompt
    : null;
  const summary = {
    done: `bitti — ${job.done}/${job.total}`,
    stopped: `durduruldu — ${job.done}/${job.total}`,
  }[job.status];

  return (
    <div style={PANEL}>
      <div style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1, minHeight: 0 }}>
        <Mono size={11} style={LABEL}>Prompt listesi</Mono>
        <textarea
          className="wf-input"
          rows={11}
          value={prompts}
          placeholder={PLACEHOLDER}
          onChange={(e) => setPrompts(e.target.value)}
          style={{ fontSize: 11.5, flex: 1, fontFamily: "IBM Plex Mono, monospace" }}
        />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Mono size={11} style={LABEL}>Negatif prompt</Mono>
        <input
          className="wf-input"
          value={negative}
          onChange={(e) => setNegative(e.target.value)}
          style={{ fontSize: 12.5 }}
        />
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <Mono size={11} style={{ ...LABEL, flex: 1 }}>Varyant</Mono>
        <input
          className="wf-input"
          type="number"
          min={1}
          max={26}
          value={variants}
          onChange={(e) => setVariants(e.target.value)}
          style={{ width: 56, textAlign: "center", fontSize: 13 }}
        />
      </div>

      {running ? (
        <ProgressPanel job={job} onStop={onStop} />
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <Btn hl disabled={!prompts.trim() || busyElsewhere}
               onClick={() => onGenerate({
                 prompts,
                 negative,
                 variants: Number.isInteger(perPrompt) && variants.trim() !== ""
                   ? perPrompt
                   : null,
               })}
               style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
            <Icon.Sparkle /> Üret
          </Btn>

          {planned !== null && (
            <Mono size={11} style={{ color: "var(--ink-3)", textAlign: "center" }}>
              {count} prompt × {perPrompt} varyant = <span style={{ color: "var(--accent)" }}>{planned} foto</span>
            </Mono>
          )}
          {summary && (
            <Mono size={11} style={{ color: "var(--ink-2)", textAlign: "center" }}>{summary}</Mono>
          )}
          {busyElsewhere && (
            <Note size={12} style={{ color: "var(--ink-3)" }}>
              Üretim sürüyor: {job.project} — bitmesini bekle.
            </Note>
          )}
          {error && <Note size={12} style={{ color: "var(--danger)" }}>{error}</Note>}
          {job.status === "error" && (
            <div className="wf-stroke" style={{ padding: 12, display: "flex",
                                                flexDirection: "column", gap: 8,
                                                borderColor: "var(--danger)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--danger)" }}>
                <Icon.Warn />
                <Note size={13} style={{ color: "var(--danger)", fontWeight: 500 }}>Üretim durdu</Note>
              </div>
              <Note size={12} style={{ color: "var(--ink-2)" }}>
                {job.done}/{job.total} tamamlandı — üretilenler kaydedildi.
              </Note>
              {/* The server's own error text -- we never guess the cause. */}
              <Mono size={10} style={RAW_ERROR}>{job.error}</Mono>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Derle**

Run: `cd queen-editor/frontend && npm run build`
Expected: PASS — `ProgressPanel.jsx` zaten var ve `{job, onStop}` alıyor; Task 3 yalnız içeriğini tasarıma çeviriyor.

---

### Task 3: İlerleme kutusu — `ProgressPanel.jsx`

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/ProgressPanel.jsx` (tamamı)

**Interfaces:**
- Consumes: kit `Btn`, `Mono`, `Note` · `job` durumu (`done`, `failed`, `total`, `current{number, letter, prompt}`)
- Produces: `<ProgressPanel job onStop />` — panelin alt bloğu, kendi başına tam genişlik kaplar.

- [ ] **Step 1: `ProgressPanel.jsx`'i baştan yaz**

```jsx
import { Btn, Mono, Note } from "../../vendor/kit.jsx";

const BOX = { padding: 12, display: "flex", flexDirection: "column", gap: 8 };
const TRACK = { height: 5, background: "var(--bg-3)", borderRadius: 3, overflow: "hidden" };

// Artboard 04: the panel's bottom block while a batch runs. The form above it stays on screen,
// so this shows progress only -- it never repeats what the fields already say.
export default function ProgressPanel({ job, onStop }) {
  const { done = 0, failed = 0, total = 0, current } = job;
  const finished = done + failed;
  // total is 0 on the first poll after the 202: the server has not planned the frames yet.
  const percent = total ? Math.round((finished / total) * 100) : 0;

  return (
    <div className="wf-stroke" style={BOX}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <Mono size={13} style={{ color: "var(--accent)" }}>{finished} / {total || "…"}</Mono>
        <Btn sm onClick={onStop}>Durdur</Btn>
      </div>

      <div style={TRACK}>
        <div style={{ width: `${percent}%`, height: "100%", background: "var(--accent)" }} />
      </div>

      {current && (
        <Note size={12} style={{ color: "var(--ink-2)", whiteSpace: "nowrap",
                                 overflow: "hidden", textOverflow: "ellipsis" }}>
          şimdi: "{current.prompt}"
        </Note>
      )}
      {failed > 0 && (
        <Note size={12} style={{ color: "var(--danger)" }}>
          {failed} fotoğraf üretilemedi — diğerleri devam ediyor
        </Note>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Derlemeyi dene**

Run: `cd queen-editor/frontend && npm run build`
Expected: PASS (Gallery hâlâ eski hâlinde ama imzası uyumlu: fazladan `current` prop'u zararsız).

---

### Task 4: Galeri — `Gallery.jsx`

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx` (tamamı)

**Interfaces:**
- Consumes: `photoUrl(project, file)` · kit `ImgPH`, `Mono`, `Note`
- Produces: `<Gallery project photos current />` — `photos: string[]` (sunucu sıralar), `current: {number, letter, prompt} | null`.

- [ ] **Step 1: `Gallery.jsx`'i baştan yaz**

```jsx
import { photoUrl } from "../../shared/api.js";
import { ImgPH, Mono, Note } from "../../vendor/kit.jsx";

const PAD = { padding: 16 };
const GRID = { display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 12 };
const EMPTY = {
  minHeight: "60vh",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: 8,
};

function Tile({ name, muted, children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      {children}
      <Mono size={10} style={{ color: muted ? "var(--ink-4)" : "var(--ink-3)" }}>{name}</Mono>
    </div>
  );
}

// Artboard 03/04: five columns, newest number first (the server sorts). The frame being rendered
// sits at the front as a spinner tile, so the grid shows what is happening, not just what landed.
export default function Gallery({ project, photos, current }) {
  if (!photos.length && !current) {
    return (
      <div style={{ ...PAD, ...EMPTY }}>
        <Mono size={12} style={{ color: "var(--ink-3)" }}>henüz fotoğraf yok</Mono>
        <Note size={13} style={{ color: "var(--ink-3)" }}>
          Prompt'ları yaz, Üret'e bas — fotoğraflar burada belirecek
        </Note>
      </div>
    );
  }

  return (
    <div style={PAD}>
      <div style={GRID}>
        {current && (
          <Tile name={`${current.number}_${current.letter}.png`} muted>
            <ImgPH loading style={{ aspectRatio: "1/1" }} />
          </Tile>
        )}
        {photos.map((file) => (
          <Tile key={file} name={file}>
            {/* New tab on click -- the gesture the design gives every tile. */}
            <a href={photoUrl(project, file)} target="_blank" rel="noreferrer">
              <img src={photoUrl(project, file)} alt={file}
                   style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover",
                            border: "1px solid var(--border)", borderRadius: 3, display: "block" }} />
            </a>
          </Tile>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Derle**

Run: `cd queen-editor/frontend && npm run build`
Expected: PASS — uyarı yok.

---

### Task 5: Temizlik, derleme ve spec

**Files:**
- Delete: `queen-editor/frontend/src/features/photo_generation/VariantPicker.jsx`
- Modify: `docs/superpowers/specs/2026-07-25-queen-editor-b5-coklu-foto-design.md`
- Regenerate: `queen-editor/frontend/dist/`

**Interfaces:**
- Consumes: Task 1-4'ün dosyaları
- Produces: kimsenin import etmediği dosya kalmaz; `dist/` güncel; spec ekrandaki gerçeği anlatır.

- [ ] **Step 1: Artık kullanılmayan bileşeni sil**

```bash
git rm queen-editor/frontend/src/features/photo_generation/VariantPicker.jsx
```

- [ ] **Step 2: Öksüz import kalmadığını doğrula**

Run: `cd queen-editor && grep -rn "VariantPicker" frontend/src docs` (ya da Grep aracı)
Expected: hiçbir sonuç yok.

- [ ] **Step 3: Spec'in ekran tablosunu ve frontend bölümünü tasarıma göre güncelle**

`## Ekran (artboard eşlemesi)` tablosundaki **boşta** ve **üretiliyor** satırları şunlarla değiştirilir:

```markdown
| boşta | Başlık: sol **Queen Editor** · orta proje adı · sağ **Projeden çık** (kırmızı, ghost). Solda galeri (5 sütun, en yeni numara üstte; boşsa ortalanmış "henüz fotoğraf yok" + yönlendirme). Sağda 320px panel: prompt listesi · **Negatif prompt** (tek satır) · **Varyant** (etiketle aynı satırda, 56px ortalı sayı kutusu) · **Üret** + altında `N prompt × M varyant = K foto` | 03 |
| üretiliyor | Form **ekranda kalır**; panelin yalnız alt bloğu `wf-stroke` kutuya döner: `7 / 48` + **Durdur** yan yana, 5px ilerleme çubuğu, `şimdi: "…"`, başarısız sayısı. Galeride üretilen kare spinner'lı tile olarak en başta durur | 04 |
```

`## Frontend` bölümündeki varyant paragrafı şununla değiştirilir:

```markdown
Ölçüler ve metinler tasarımın `simple-screens.jsx`'inden birebir alınır (panel 320, galeri 5×gap 12,
varyant kutusu 56px ortalı, prompt textarea `rows 11`/11.5px, negatif tek satır `input`). Kit'in
`Segment`'i kullanılmaz — wireframe olduğu için butonlarında `onClick` yok ve tasarım zaten sayı
kutusu gösteriyor. Üret'in altındaki sayaç yalnız bir **önizleme**: metni güvenle sayamazsak satır
görünmez, çünkü kural ve hata mesajları backend'in. Tek sapma galerinin `overflowY: auto` olması —
artboard sabit yükseklikli çerçeve, canlı sayfa kaymak zorunda.
```

- [ ] **Step 4: Derle ve backend'in bozulmadığını doğrula**

Run: `cd queen-editor/frontend && npm run build`
Expected: PASS, `dist/assets/*` yenilenir.
Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (136) — bu bölümde backend'e dokunulmadı.

---

### Task 6: Commit + Colab doğrulaması (kullanıcı kapısı)

**Files:** (yok — commit + doğrulama)

- [ ] **Step 1: Commit + push (kullanıcı onayıyla)**

Mesaj scratchpad'e yazılır, `-F` ile verilir (PowerShell here-string argümanları bölüyor):

```
fix(queen-editor): proje ekranını artboard 03/04'e oturt

The screen was built from the written spec while the design project was
unreachable; with simple-screens.jsx in hand it was off in seven places.

Header now carries the product name, the project and a red "Projeden çık".
The panel is 320px with a left border and, while a batch runs, keeps the form
on screen -- only its bottom block becomes the wf-stroke progress box
(counter + Durdur on one row, 5px bar, current prompt). The negative is a
single-line input, the variant count sits inline at 56px, and Üret carries the
"N prompt x M varyant = K foto" preview.

The gallery empties to the design's centered two-liner and shows the frame in
flight as a spinner tile, so the grid tracks the run instead of only its
results.

Backend, endpoints and the 136 tests are untouched: this is presentation only.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
```

```bash
git add -- queen-editor/frontend/src queen-editor/frontend/dist \
  docs/superpowers/specs/2026-07-25-queen-editor-b5-coklu-foto-design.md \
  docs/superpowers/plans/2026-07-25-queen-editor-b5-1-tasarim-sadakati.md
git commit -F "<scratchpad>/b51-commit-msg.txt" -- \
  queen-editor/frontend/src queen-editor/frontend/dist \
  docs/superpowers/specs/2026-07-25-queen-editor-b5-coklu-foto-design.md \
  docs/superpowers/plans/2026-07-25-queen-editor-b5-1-tasarim-sadakati.md
git push origin feat/queen-editor-v1
```

- [ ] **Step 2: Kullanıcı Colab doğrulaması (T4)**

Notebook değişmedi; **Run all** yeni kodu klonlar. Ekranda beklenen:

1. **Başlık:** solda `Queen Editor`, ortada proje adı, sağda kırmızı **Projeden çık** → basınca liste ekranı.
2. **Yerleşim:** solda galeri, sağda 320px panel, arada dikey çizgi.
3. **Panel:** "Prompt listesi" (uzun mono kutu) · "Negatif prompt" (**tek satır**) · "Varyant" etiketi ve **yanında 56px ortalı sayı kutusu** (4).
4. **Sayaç:** 3 prompt'luk liste yapıştır, varyant 2 → Üret'in altında `3 prompt × 2 varyant = 6 foto`. Listeyi boz (parantezi sil) → satır **kaybolur**, hata çıkmaz.
5. **Üretim:** Üret → form yerinde kalır, altta `0 / 6` + **Durdur** + çubuk + `şimdi: "…"`. Galeride üretilen kare **spinner'lı** görünür, biten kareler önüne eklenir.
6. **Durdur** → süren kare biter, form geri gelir, `durduruldu — n/6`.
7. **Boş proje:** yeni proje aç → galeri ortasında "henüz fotoğraf yok" + "Prompt'ları yaz, Üret'e bas — fotoğraflar burada belirecek".
8. **Kaydırma:** 20+ foto olunca galeri kayar, panel yerinde kalır.

---

## Doğrulama özeti

| Ne | Nasıl |
|---|---|
| Başlık ve yerleşim | Colab görsel kontrol 1-2 |
| Form alanları tasarım ölçüsünde | Colab görsel kontrol 3 |
| Sayaç önizlemesi (ve bozuk metinde susması) | Colab görsel kontrol 4 |
| İlerleme kutusu, form ekranda kalıyor | Colab görsel kontrol 5-6 |
| Boş galeri metni | Colab görsel kontrol 7 |
| Galeri kayması (tek bilinçli sapma) | Colab görsel kontrol 8 |
| Öksüz dosya kalmadı | `grep -rn "VariantPicker" frontend/src docs` → 0 |
| Arayüz derleniyor | `cd frontend && npm run build` |
| Backend bozulmadı | `python -m pytest -q` → 136 |
| Bölüm 5.1 kapanır | Kullanıcı doğrular → commit + push |
