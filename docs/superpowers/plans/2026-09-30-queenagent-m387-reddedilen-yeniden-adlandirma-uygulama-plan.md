# Madde 387 — Reddedilen yeniden adlandırma · uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Amaç:** Satırın yeniden adlandırma alanı sunucunun cevabını bekler, reddde yazılan adla açık kalır.

**Mimari:** Yalnız `ProjectRow.jsx`'in `RenameField`'ı değişir: `onDone` yerine `onSave` (söz döner)
ve `onClose`. `useProjects`, `App` ve CSS değişmez.

**Teknoloji:** React 18.

**Spec:** `docs/superpowers/specs/2026-09-30-queenagent-m387-reddedilen-yeniden-adlandirma-uygulama-design.md`

## Genel kısıtlar

- Yorumlar İngilizce, neden'i söyler, yalnız bugün doğru olanı.
- `dist` kurulmaz; testlere dokunulmaz.

---

### Görev 1: `RenameField` cevabı bekler

**Dosya:** `queen-agent/frontend/src/features/workspace/ProjectRow.jsx`

**Arayüz:** `RenameField({ name, onSave, onClose })` — `onSave(name) => Promise<truthy | falsy>`,
kabulde truthy. `ProjectRow`'un `onRename(id, name)`'i bu sözü döner (App'te `editProject`).

- [ ] **Adım 1:** `RenameField` şöyle olur:

```jsx
// The name corrected in the row's own place rather than in the browser's box (the design's 170).
// The draft is the field's, as a message edit's is (EditMessage): only the finished name leaves.
// The field stays until the server has answered, and a refusal leaves the name where it was typed,
// ready to send again -- as the naming screen keeps the name it could not create (Madde 387).
function RenameField({ name, onSave, onClose }) {
  const [draft, setDraft] = useState(name);
  // Enter's field can take its focus with it, and a second press can come before the answer --
  // neither may send the same name a second time.
  const done = useRef(false);
  const finish = async (save) => {
    if (done.current) return;
    done.current = true;
    const typed = draft.trim();
    // An empty name, or one given up on, asks the server nothing.
    if (!save || !typed) {
      onClose();
      return;
    }
    if (await onSave(typed)) onClose();
    else done.current = false;
  };
  ...input unchanged...
}
```

- [ ] **Adım 2:** `ProjectRow`'da bağlama:

```jsx
      <RenameField
        name={project.name}
        onSave={(name) => onRename?.(project.id, name)}
        onClose={() => setRenaming(false)}
      />
```

- [ ] **Adım 3:** Dört satır paralel; hepsi yeşil (queen-agent frontend 825).
- [ ] **Adım 4:** Commit, uygulama spec'i ve planıyla:
  `feat: Madde 387 -- a refused rename keeps the typed name in its row`
