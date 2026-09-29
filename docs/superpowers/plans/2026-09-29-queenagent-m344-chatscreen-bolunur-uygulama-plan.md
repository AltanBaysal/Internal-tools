# Madde 344 — ChatScreen.jsx bölünür · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mesajı çizen sekiz bileşen `ChatScreen.jsx`'ten beş dosyaya taşınır; ekran ve davranış
değişmez, test turunun kırmızısı yeşile döner.

**Architecture:** Saf taşıma. Her bileşen bugünkü satırlarıyla, gövdesi ve yorumu aynen, yeni dosyasına
gider; değişen yalnız `export` sözleri ve importlar. `ChatScreen.jsx`'te ekranın kendisi kalır.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m344-chatscreen-bolunur-uygulama-design.md)

## Global Constraints

- Taşınan satırlar baytı baytına aynı; tek yer değiştirme `CreatingFile`'ın yorumu (bugün 155–156).
- `ChatScreen` fonksiyonunun gövdesine (bugün 304–636) dokunulmaz.
- `workspace.css` değişmez; `dist` derlenmez.
- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Commit mesajında çift tırnak yok; amend yok.

Aşağıdaki satır numaraları `8383f1e5`'teki `ChatScreen.jsx`'in.

---

### Task 1: Beş dosya, ve ChatScreen.jsx'in ekrana inmesi

**Files:**
- Create: `queen-agent/frontend/src/features/workspace/ToolCalls.jsx`
- Create: `queen-agent/frontend/src/features/workspace/Stamp.jsx`
- Create: `queen-agent/frontend/src/features/workspace/EditMessage.jsx`
- Create: `queen-agent/frontend/src/features/workspace/MessageFoot.jsx`
- Create: `queen-agent/frontend/src/features/workspace/FileCard.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.jsx:1-302`
- Test: test turunun beş dosyası ve `ChatScreen.test.jsx`'in kilidi (commit edilmiş, değişmez)

**Interfaces:**
- Consumes: test turunun beklediği adlar — `ToolCalls`, `Stamp` + `{ LiveStrip }`, `EditMessage`,
  `MessageFoot`, `FileCard` + `{ CreatingFile }`, hepsi `./<Dosya>.jsx`'ten.
- Produces: dalga 2'nin 347, 348 ve 349'unun üstüne kurulacağı beş dosya.

- [ ] **Step 1: `ToolCalls.jsx`**

```jsx
import { useState } from "react";

```

ardından 26–76. satırlar aynen; 44. satır `export default function ToolCalls({ calls, running }) {` olur.

- [ ] **Step 2: `Stamp.jsx`**

```jsx
import { useEffect, useState } from "react";

import { clockTime } from "../../shared/time.js";

```

ardından 78–153. satırlar aynen; 93. satır `export default function Stamp({ at, usage }) {`, 130. satır
`export function LiveStrip({ round, of, tokens }) {` olur.

- [ ] **Step 3: `EditMessage.jsx`**

```jsx
import { useState } from "react";

```

ardından 157–210. satırlar aynen; 163. satır
`export default function EditMessage({ text, onConfirm, onCancel }) {` olur.

- [ ] **Step 4: `MessageFoot.jsx`**

212–275. satırlar aynen, import yok; 257. satır
`export default function MessageFoot({ standing, onVersion, onEdit }) {` olur.

- [ ] **Step 5: `FileCard.jsx`**

Sıra: 14. satır (`CHIP_LENGTH`), boş satır, 19–24 (`extensionOf`), boş satır, 155–156 (`CreatingFile`'ın
yorumu), 277–284 (`CreatingFile`), boş satır, 286–302 (`FileCard`). Import yok. 277. satır
`export function CreatingFile() {`, 289. satır
`export default function FileCard({ name, selected, onOpen }) {` olur.

- [ ] **Step 6: `ChatScreen.jsx`'i ekrana indir**

14. satırı ve 19–302. satırları sil (ekranın 304. satırı ile önündeki boş satır kalır). Importlar:

```jsx
import { useEffect, useRef, useState } from "react";

import Composer from "./Composer.jsx";
import ContextGauge from "./ContextGauge.jsx";
import EditMessage from "./EditMessage.jsx";
import FileCard, { CreatingFile } from "./FileCard.jsx";
import FileRail from "./FileRail.jsx";
import Markdown from "./Markdown.jsx";
import MessageFoot from "./MessageFoot.jsx";
import ModelPicker from "./ModelPicker.jsx";
import ModePicker from "./ModePicker.jsx";
import PermissionCard from "./PermissionCard.jsx";
import Skeleton from "./Skeleton.jsx";
import SkillPicker from "./SkillPicker.jsx";
import Stamp, { LiveStrip } from "./Stamp.jsx";
import ToolCalls from "./ToolCalls.jsx";

// A reader further from the bottom than this is reading, not watching, and the answer must not pull
// them away from it. The design's own number.
const STICK_WITHIN = 220;

export default function ChatScreen({
```

- [ ] **Step 7: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend` 669 yeşil (652 + 17). queen-agent'ın arka ucu 933,
queen-editor'ün ön ucu 749 yeşil; queen-editor'ün arka ucu 377'nin bilinen iki kırmızısı.

- [ ] **Step 8: Farkı oku**

`git diff 8383f1e5..HEAD` ve çalışma kopyası: taşınan her satırın yeni dosyada aynen durduğu,
`ChatScreen` gövdesinin değişmediği, ölü import kalmadığı.

- [ ] **Step 9: Commit**

```powershell
git add queen-agent/frontend/src/features/workspace/ToolCalls.jsx queen-agent/frontend/src/features/workspace/Stamp.jsx queen-agent/frontend/src/features/workspace/EditMessage.jsx queen-agent/frontend/src/features/workspace/MessageFoot.jsx queen-agent/frontend/src/features/workspace/FileCard.jsx queen-agent/frontend/src/features/workspace/ChatScreen.jsx docs/superpowers/specs/2026-09-29-queenagent-m344-chatscreen-bolunur-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m344-chatscreen-bolunur-uygulama-plan.md
git commit -m @'
feat: Madde 344 -- ChatScreen.jsx is the screen alone, and each part of a message draws from its own file

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
