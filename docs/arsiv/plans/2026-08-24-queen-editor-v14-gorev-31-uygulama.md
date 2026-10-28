# v14 Görev 31 — Galeri gerekmeyen bir cevabı beklemez: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Önceki commit'in yedi kırmızı testini yeşile döndürmek.

**Architecture:** Proje kaydının durumu adres seviyesinden bir prop'a iner. `App` artık dallanmıyor,
`ProjectScreen` ve `SidePanel` üçlüyü yalnız geçiriyor, okuyan tek yer fotoğraf panelinin çizildiği
dal. `ProjectLoading.jsx` silinir.

**Tech Stack:** React 18, Vite, Vitest + jsdom.

**Spec:** [Görev 31 uygulama spec'i](../specs/2026-08-24-queen-editor-v14-gorev-31-uygulama-design.md)

## Global Constraints

- **Test dosyaları değişmiyor.** `App.test.jsx` ve `SidePanel.test.jsx` bir önceki commit'te ne
  yazıldıysa o kalır. Bir testi kodun keyfine uydurmak, bu turun tamamını anlamsız kılar.
- **Prop adları testin yazdığı gibi:** `settings` (nesne ya da `null`), `settingsError`,
  `onRetrySettings`.
- **Hata halkadan önce sorulur** — kayıt okunamadığında ikisi de doğru, ve dönmeyi bırakmayan bir
  halka yanlış olan.
- **Uygulamanın dili değişmiyor:** kart yine `Proje ayarları yüklenemedi` diyor.
- Dil: kod ve yorumlar **İngilizce**; arayüz metni **Türkçe**; commit mesajı **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Test komutu (depo kökünden, `cd` yok): `npm test --prefix queen-editor/frontend`
- Derleme komutu: `npm run build --prefix queen-editor/frontend`
- **`dist` aynı commit'e girer.**

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/App.jsx` | adres → ekran | `ProjectRoute` dallanmayı bırakır |
| `queen-editor/frontend/src/features/photo_generation/ProjectLoading.jsx` | — | **sil** |
| `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx` | proje ekranının iskeleti | iki yeni prop'u geçirir |
| `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx` | sağ sütun | fotoğraf panelinin üç hâli |

---

### Task 1: Sağ sütun kaydın üç hâlini bilsin

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx`

**Interfaces:**
- Consumes: `StatusErrorCard` (`shared/StatusErrorCard.jsx`), `wf-spinner` sınıfı (`shared/app.css`).
- Produces: `SidePanel` üç yeni davranış — `settingsError` doluyken kart, `settings` `null` iken
  halka, dolu iken bugünkü `GeneratePanel`. Ray ve diğer beş panel üç hâlde de çalışır.

- [ ] **Step 1: `StatusErrorCard`'ı içe al**

Dosyanın import bloğunda, `Mono`'nun üstüne:

```jsx
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
```

- [ ] **Step 2: Bekleyişin duracağı ölçüyü yaz**

`LABEL` sabitinin altına:

```jsx
// The panel's own waiting: the ring stands where the boxes will be, so the column keeps its shape
// while the record is in flight. The screen behind it is not waiting for anything (madde 31).
const WAITING = { flex: 1, display: "flex", alignItems: "center", justifyContent: "center" };
```

- [ ] **Step 3: İmzaya iki prop ekle**

Bugünkü hâli:

```jsx
export default function SidePanel({ job, error, errorField, busyElsewhere, settings, project,
                                    stopping, queue, failures, models, modelsError, producers,
                                    frames, selected, onQueueLayer,
                                    onGenerate, onStop, onResume,
                                    onCancel, onClearError, onRetryAll }) {
```

Yerine:

```jsx
export default function SidePanel({ job, error, errorField, busyElsewhere, settings, settingsError,
                                    project, stopping, queue, failures, models, modelsError,
                                    producers, frames, selected, onQueueLayer,
                                    onGenerate, onStop, onResume, onCancel, onClearError,
                                    onRetryAll, onRetrySettings }) {
```

- [ ] **Step 4: Fotoğraf panelini üç dala ayır**

Bugünkü hâli:

```jsx
        {open === "photo" && (
          <GeneratePanel job={job} error={error} errorField={errorField}
                         busyElsewhere={busyElsewhere} settings={settings}
                         models={models} modelsError={modelsError}
                         producer={(producers?.producers || []).find((p) => p.id === "photo")}
                         onGenerate={onGenerate} onClearError={onClearError}
                         onInstall={producers?.install} />
        )}
```

Yerine:

```jsx
        {/* The project record fills this panel's boxes and nothing else on the screen reads it, so
            waiting for it is this column's business alone (madde 31). The failure is asked about
            first: with an unreadable record there is no record either, and a ring that never stops
            would promise something that is not coming. */}
        {open === "photo" && (settingsError ? (
          <StatusErrorCard text="Proje ayarları yüklenemedi" raw={settingsError}
                           onRetry={onRetrySettings} />
        ) : !settings ? (
          <div style={WAITING}><span className="wf-spinner" /></div>
        ) : (
          <GeneratePanel job={job} error={error} errorField={errorField}
                         busyElsewhere={busyElsewhere} settings={settings}
                         models={models} modelsError={modelsError}
                         producer={(producers?.producers || []).find((p) => p.id === "photo")}
                         onGenerate={onGenerate} onClearError={onClearError}
                         onInstall={producers?.install} />
        ))}
```

- [ ] **Step 5: Sağ sütunun dört testinin yeşile döndüğünü gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `SidePanel.test.jsx` **18 tests, 0 failed**. `App.test.jsx` hâlâ **3 failed** — o dosya
Task 2'nin işi.

---

### Task 2: Adres artık dallanmasın

**Files:**
- Modify: `queen-editor/frontend/src/App.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`
- Delete: `queen-editor/frontend/src/features/photo_generation/ProjectLoading.jsx`

**Interfaces:**
- Consumes: Task 1'in yazdığı üç prop — `settings` (nullable), `settingsError`, `onRetrySettings`.
- Produces: adres bir projeyi gösterdiğinde kaydın durumu ne olursa olsun `ProjectScreen` çizilir.

- [ ] **Step 1: `ProjectRoute`'u sadeleştir**

`App.jsx`'in bugünkü hâli:

```jsx
import ProjectLoading from "./features/photo_generation/ProjectLoading.jsx";
import ProjectScreen from "./features/photo_generation/ProjectScreen.jsx";
import ProjectsScreen from "./features/projects/ProjectsScreen.jsx";
import { useProjectSettings } from "./features/projects/useProjectSettings.js";
import ExportScreen from "./features/photo_generation/ExportScreen.jsx";
import PhotoDetail from "./features/photo_generation/PhotoDetail.jsx";
import { routeFromPath, useRoute } from "./shared/router.js";
import { StatusErrorCard } from "./shared/StatusErrorCard.jsx";

function ProjectRoute({ project }) {
  const { status, settings, error, save, reload } = useProjectSettings(project);
  if (status === "loading") return <ProjectLoading project={project} />;
  if (status === "error") {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center",
                    justifyContent: "center", padding: 32 }}>
        <StatusErrorCard text="Proje ayarları yüklenemedi" raw={error} onRetry={reload} />
      </div>
    );
  }
  return <ProjectScreen project={project} settings={settings} onSaveSettings={save} />;
}
```

Yerine:

```jsx
import ProjectScreen from "./features/photo_generation/ProjectScreen.jsx";
import ProjectsScreen from "./features/projects/ProjectsScreen.jsx";
import { useProjectSettings } from "./features/projects/useProjectSettings.js";
import ExportScreen from "./features/photo_generation/ExportScreen.jsx";
import PhotoDetail from "./features/photo_generation/PhotoDetail.jsx";
import { routeFromPath, useRoute } from "./shared/router.js";

// The record fills the photo panel's boxes and nothing else on the screen reads it, so the screen
// is drawn whatever became of it and the one panel that asked carries the waiting (madde 31).
// Neither state is passed on as a status: what a panel needs to know is whether it has the record,
// and if not, whether something went wrong.
function ProjectRoute({ project }) {
  const { status, settings, error, save, reload } = useProjectSettings(project);
  return (
    <ProjectScreen project={project}
                   settings={status === "ready" ? settings : null}
                   settingsError={status === "error" ? error : null}
                   onRetrySettings={reload}
                   onSaveSettings={save} />
  );
}
```

- [ ] **Step 2: `ProjectScreen` üçlüyü geçirsin**

İmzanın bugünkü hâli:

```jsx
export default function ProjectScreen({ project, settings, onSaveSettings }) {
```

Yerine:

```jsx
export default function ProjectScreen({ project, settings, settingsError, onRetrySettings,
                                        onSaveSettings }) {
```

`SidePanel` çağrısının bugünkü ilk satırı:

```jsx
        <SidePanel job={job} error={saveError || error} errorField={errorField}
                   busyElsewhere={busyElsewhere} settings={settings} project={project}
```

Yerine:

```jsx
        <SidePanel job={job} error={saveError || error} errorField={errorField}
                   busyElsewhere={busyElsewhere} settings={settings}
                   settingsError={settingsError} onRetrySettings={onRetrySettings}
                   project={project}
```

- [ ] **Step 3: Çağıranı kalmayan ekranı sil**

Run: `git rm queen-editor/frontend/src/features/photo_generation/ProjectLoading.jsx`

- [ ] **Step 4: Takımın tamamen yeşil olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: **0 failed.** `App.test.jsx` 3 tests yeşil, `SidePanel.test.jsx` 18 tests yeşil, geri
kalan her dosya bugünkü hâlinde.

---

### Task 3: Derle, doğrula, commit'le

- [ ] **Step 1: Ön yüzü derle**

Run: `npm run build --prefix queen-editor/frontend`

Expected: hatasız biter ve `queen-editor/frontend/dist/` altındaki dosyalar tazelenir.

- [ ] **Step 2: Değişen her şeyi gör**

Run: `git status --short`

Expected: `App.jsx`, `ProjectScreen.jsx`, `SidePanel.jsx`, silinmiş `ProjectLoading.jsx`,
`dist/` altındaki dosyalar ve `docs/superpowers`. **Test dosyaları bu listede olmamalı.**

- [ ] **Step 3: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the gallery stops waiting for a textarea

The project record fills four boxes in the photo panel -- the prompt list, the
negative, the variant count and the model. Nothing else on the screen reads it.
The gallery is not even handed it. Until now the whole page waited for it
anyway: bar, gallery and rail together collapsed into a single ring until the
answer came back over the Colab tunnel.

Coming back from a frame is where that became visible, because that is where
something is taken away, but the same gap was there on the very first visit.

The state stops being read at the address and becomes a prop. App no longer
branches; the screen is drawn whatever became of the record, and the column
that asked for it carries the waiting: a ring in its own place while it is in
flight, the failure card in the same place when it cannot be read at all. The
failure is asked about first -- with no record there is no record either, and a
ring that never stops would promise something that is not coming.

The form is still seeded once at its own mount, so nothing is synced afterwards
and typing still cannot be written over. ProjectLoading had one caller and that
branch is gone with it.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** Üç prop → Task 1 Step 3, Task 2 Step 1–2. Hata sıralaması → Task 1 Step 4. Silinen
dosya → Task 2 Step 3. Derlenmiş çıktı → Task 3 Step 1. Spec'te olup planda karşılığı olmayan madde
yok.

**Ad tutarlılığı:** `settings`, `settingsError`, `onRetrySettings` — üçü de test döngüsünün
`SidePanel.test.jsx`'e yazdığı adlarla birebir aynı, ve dört dosyada tek yazımla geçiyor.

**Test dosyalarına dokunulmuyor:** Task 1 ve 2'nin dosya listelerinde hiçbir `.test.jsx` yok.

**Bilerek dışarıda:** `useProjectSettings.js` hiç açılmıyor. Kaydın nasıl istendiği bu maddenin
konusu değil; onu susturmak 32. maddenin işi ve o dosya ilk kez orada değişecek.
