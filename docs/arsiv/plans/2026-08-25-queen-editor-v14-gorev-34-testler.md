# v14 Görev 34 — Açık panel geri dönüşte yerinde kalır: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dört test yazmak; ikisi düşecek, ikisi tutucu olarak yeşil doğacak. Kod bu döngüde
değişmiyor.

**Architecture:** Tek dosya. Depo `SidePanel`'in kendi modülünde doğacağı için taşınacak kablo yok;
dosya her teste taze modül veren düzene geçiyor, sonra dört test ekleniyor.

**Tech Stack:** Vitest + jsdom + @testing-library/react. `globals` kapalı — `describe`/`it`/`expect`
dosyada `vitest`'ten adıyla alınıyor.

**Spec:** [Görev 34 test spec'i](../specs/2026-08-25-queen-editor-v14-gorev-34-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `SidePanel.jsx` bu commit'te olduğu gibi kalır.
- **Kırmızı bırakılır.** `skip`/`xfail` yok.
- **Mevcut on dokuz testin cümleleri değişmiyor** — yalnız dosyanın kurulumu.
- **Depo proje anahtarlı**, ve **kapalı sütun `null`**, "hatırlanmıyor" ile karıştırılamaz.
- **`dist` bu commit'e girmez** — ön yüz kaynağı değişmiyor.
- Dil: test adları ve yorumlar **İngilizce**; commit mesajı **İngilizce**; belgeler **Türkçe**.
- Commit mesajında **çift tırnak yok**.
- Test komutu (depo kökünden, `cd` yok): `npm test --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/features/photo_generation/SidePanel.test.jsx` | sağ sütunun hangi panelle açıldığı | taze modül düzeni, sonra dört test |

Tek dosya, çünkü sınanan davranışın tamamı tek bileşenin içinde doğuyor. Ekran seviyesinde bir test
yok: 33'te vardı çünkü orada sessizce eksik kalabilecek bir kablo vardı; burada dışarıdan geçirilen
hiçbir şey yok.

---

### Task 1: Dosya her teste taze modül alsın

Bu adım kendi başına bir teslimat: hiçbir davranış değişmiyor ve takım yeşil kalıyor. Ayrı duruyor
çünkü bir sonraki adımın testleri ancak bu düzen kurulduktan sonra anlamlı — depo sızarsa testler
birbirinin başlangıcını belirler.

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/SidePanel.test.jsx:1-4`

**Interfaces:**
- Consumes: dosyanın mevcut `column(props)` ve `renderColumn(props)` yardımcıları. İkisi de
  `SidePanel`'i JSX içinde çağırıyor, yani değişkenin render anında dolu olması yeterli — ikisine de
  dokunulmuyor.
- Produces: her testin kendi `SidePanel` modülüyle koşması.

- [ ] **Step 1: İçe almayı `beforeEach`'e taşı**

Dosyanın ilk dört satırı bugün:

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import SidePanel from "./SidePanel.jsx";
```

Yerine:

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Which panel is open is remembered for the length of a visit, and that memory lives in the module.
// So each test gets the module itself fresh -- otherwise a test that closes the column would be
// deciding how the next one opens. Nothing is mocked in this file, so resetModules really does
// rebuild it.
let SidePanel;

beforeEach(async () => {
  vi.resetModules();
  ({ default: SidePanel } = await import("./SidePanel.jsx"));
});
```

- [ ] **Step 2: Mevcut on dokuz testin hâlâ yeşil olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `SidePanel.test.jsx` **19 tests, 0 failed**; takımın tamamı yeşil (571 tests).

Düşen olursa dur: bu adım hiçbir davranışa dokunmuyor, dolayısıyla düşen bir test kurulumun kendisi
hakkında bir şey söylüyor demektir.

---

### Task 2: Dört testi ekle

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/SidePanel.test.jsx` (dosyanın sonu)

**Interfaces:**
- Consumes: Task 1'in kurduğu taze modül düzeni; dosyanın `RUNNING` ve `PROMPT_BOX` sabitleri;
  `renderColumn(props)`.
- Produces: implementasyon döngüsünün uyacağı sözleşme — `SidePanel`, aldığı `project` için en son
  hangi panel açıksa onunla doğar; kapalı bırakılmışsa kapalı doğar; hatırlanan yoksa `"photo"` ile
  doğar; başka bir proje kendi varsayılanıyla doğar. `SidePanel`'in dışa açık yüzü değişmiyor —
  yeni prop yok.

- [ ] **Step 1: Testleri dosyanın sonuna ekle**

Son `describe` bloğunun kapanışından sonra:

```jsx
describe("SidePanel — coming back to the column", () => {
  it("opens on the panel that was open when it was last torn down", () => {
    const first = renderColumn({ job: RUNNING, queue: [{ layer: "photo", owed: 2 }] });
    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));
    first.unmount();

    // Opening a frame tears the whole project screen down, this column with it. Watching the queue
    // and then looking at a frame should not cost the panel.
    renderColumn({ job: RUNNING, queue: [{ layer: "photo", owed: 2 }] });

    expect(screen.getByRole("heading", { name: "Kuyruk" })).toBeTruthy();
    expect(screen.getByLabelText("Kuyruğu takip et").getAttribute("aria-current")).toBe("page");
  });

  it("comes back closed when it was left closed", () => {
    const first = renderColumn();
    fireEvent.click(screen.getByLabelText("Fotoğraf üret"));      // closes the open panel
    first.unmount();

    renderColumn();

    // Closed is an answer too: the width was given back to the gallery on purpose. It is also the
    // trap in the store -- closed is null, and so is having nothing remembered.
    expect(screen.queryByPlaceholderText(PROMPT_BOX)).toBeNull();
    expect(document.querySelectorAll("[aria-current='page']")).toHaveLength(0);
    expect(screen.getByLabelText("Fotoğraf üret")).toBeTruthy();  // the rail stays
  });

  it("still opens on the form panel when nothing has been chosen yet", () => {
    renderColumn();

    // The first visit of a session has nothing to go on, and the form is where the column opens.
    expect(screen.getByPlaceholderText(PROMPT_BOX)).toBeTruthy();
    expect(screen.getByLabelText("Fotoğraf üret").getAttribute("aria-current")).toBe("page");
  });

  it("opens another project on its own default", () => {
    const first = renderColumn({ job: RUNNING, queue: [{ layer: "photo", owed: 2 }] });
    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));
    first.unmount();

    renderColumn({ project: "başka" });

    // Which panel is being watched is the user's work in one project, never a fact about the app.
    expect(screen.getByPlaceholderText(PROMPT_BOX)).toBeTruthy();
  });
});
```

- [ ] **Step 2: İkisinin düştüğünü, ikisinin yeşil doğduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `SidePanel.test.jsx` **23 tests, 2 failed**:

- *opens on the panel that was open when it was last torn down* — ikinci sütun *Fotoğraf üret* ile
  açılıyor, `Kuyruk` başlığı bulunamıyor.
- *comes back closed when it was left closed* — ikinci sütun kapalı değil, prompt kutusu ekranda.

Yeşil doğan ikisi (`still opens on the form panel…`, `opens another project on its own default`)
**tutucudur ve kırmızıya düşmemeleri gerekir.** Bugün de doğrular; varlık sebepleri yanlış
uygulamaları kırmak — biri deponun ilk değerini `null` seçeni, öteki projeyi anahtar yapmayı
unutanı.

Mevcut on dokuz testten düşen olursa dur.

---

### Task 3: Kırmızıyı doğrula ve commit'le

**Files:**
- Değişiklik yok; bu görev doğrulama ve kayıt.

- [ ] **Step 1: Toplamı gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: **2 failed**, ikisi de `SidePanel.test.jsx`'ten; 573 test içinde 571 yeşil. Başka hiçbir
dosya düşmemeli — özellikle `App.test.jsx`, `ProjectScreen.test.jsx` ve `QueuePanel.test.jsx`
31–33'ten yeşil kalmalı.

- [ ] **Step 2: Yalnız beklenen dosyaların değiştiğini doğrula**

Run: `git status --short`

Expected: `SidePanel.test.jsx` ve `docs/superpowers` altındaki iki yeni belge. `SidePanel.jsx` ve
`queen-editor/frontend/dist` bu listede **olmamalı.**

- [ ] **Step 3: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): red for a column that remembers which panel was open

THESE TESTS FAIL ON PURPOSE. The code that answers them is the next commit.

Watching the queue and then looking at a frame costs the panel: coming back, the
column is on the photo form again whatever was open before. Same cause as the
last three items -- the address swaps the whole screen, React throws away the
state of a component that no longer exists, and the new instance opens on its
default.

Closed is remembered too. A user who closed the column gave that width to the
gallery on purpose, and reopening it for them is the same kind of wrong. It is
also where the store can go wrong quietly: closed is null, and so is having
nothing remembered, and the two must not be the same answer.

Two of the four are green from the start and are meant to be. One breaks the
build that starts the store at nothing, which would leave the column shut on a
first visit; the other breaks the build that forgets to key it by project, which
would carry one project's panel into another. Neither describes a bug that
exists today; both describe a wrong turn that is easy to take.

The file now takes a fresh module per test. The memory is real module state, so
a test that closes the column would otherwise be deciding how the next one
opens. Nothing is mocked in this file, so resetModules really does rebuild it.

This lands after the item that taught the queue panel to keep quiet before the
first answer. In the other order this one would put that wrong sentence on the
screen for the first time.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** B1 → Task 2 testi 1. B2 → Task 2 testi 2. B3 → Task 2 testi 3. B4 → Task 2
testi 4. Taze modül düzeni → Task 1. Spec'in "kapalı `null` tuzağı" notu → Task 2 testi 2'nin
yorumu ve commit mesajı. Spec'te olup planda karşılığı olmayan madde yok.

**Yer tutucu yok:** Her adımda çalıştırılacak gerçek kod ve gerçek komut var.

**Ad tutarlılığı:** Testler `SidePanel`'in dışa açık yüzünden yeni bir ad istemiyor — depo tamamen
bileşenin içinde doğacak, ve sınanan tek şey hangi panelin açık doğduğu. Dosyanın mevcut
`renderColumn`, `RUNNING`, `PROMPT_BOX` adları olduğu gibi kullanılıyor.

**Bilerek dışarıda:**

- **Ekran seviyesinde test yok.** 33'te vardı çünkü `known` bayrağı dört dosyadan geçiyordu ve
  eksik bir kablo sessizce kalabiliyordu. Burada geçen bir şey yok.
- **Deponun ömrü sınanmıyor.** Sayfa yenilenince sıfırlanması, deponun modül seviyesinde olmasının
  doğrudan sonucu; jsdom'da bir sayfa yenilemesi taklit etmek, testin kendi kurgusunu sınamak
  olurdu.
