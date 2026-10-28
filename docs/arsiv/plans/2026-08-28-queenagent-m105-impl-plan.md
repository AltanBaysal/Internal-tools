# Madde 105 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m105-skill-sohbetin-uygulama-design.md](../specs/2026-08-28-queenagent-m105-skill-sohbetin-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `remembered.js` — sona

```js
// What does not parse never happened: storage is shared with every past version of the app, and a
// map that will not read is an empty map rather than a crash.
function parsedMap(text) {
  try {
    const parsed = JSON.parse(text);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) return parsed;
  } catch {
    // Nothing to do and nothing to say.
  }
  return {};
}

// A map under one name: an entry per chat, so what one chat picks never stands in another
// (Madde 105). The write goes through the functional form -- two picks in one breath must not
// undo each other.
export function useRememberedMap(name) {
  const [kept, setKept] = useRemembered(name, "{}");
  const remember = (key, value) =>
    setKept((current) => JSON.stringify({ ...parsedMap(current), [key]: value }));
  return [parsedMap(kept), remember];
}
```

## B. `App.jsx`

1. Import: `useRemembered` → `useRememberedMap`.
2. `lastSkill` bloğu *(Madde 100 yorumuyla)* şu ikiliye döner:

```js
  // The selection is the chat's own since Madde 105 -- one browser key, an entry per chat, so what
  // is picked in one chat never stands in another. Remembered for the reason Madde 100 gave: a
  // five-step flow that loses its skill on a reload sends the next turn with no instruction.
  const [chatSkills, rememberChatSkill] = useRememberedMap("chat-skills");
  // What the next chat is born with. The draft's and the project screen's picker hold a chat that
  // does not exist yet; the birth writes the value into the newborn's entry and lets it go, so the
  // next draft starts with nothing.
  const [draftSkill, setDraftSkill] = useState("");
```

3. `drafting`'in altına yürürlükteki seçim ve değiştiricisi:

```js
  // One value on the screen and in the request, Madde 86's rule at the chat's boundary.
  const skillInForce = drafting ? draftSkill : (chatSkills[route.chatId] ?? "");
  const changeSkill = (value) => {
    if (drafting) setDraftSkill(value);
    else rememberChatSkill(route.chatId, value);
  };
```

4. `born` çengeli *(useChat'in ikinci callback'i)* doğumda yazar ve bırakır:

```js
    (id) => {
      // The skill that governed the birth becomes the newborn's own selection, and the draft lets
      // it go -- Madde 105.
      if (draftSkill) rememberChatSkill(id, draftSkill);
      setDraftSkill("");
      openChat(route.projectId, id, { replace: true });
      return Promise.all([reloadProjectChats(), reloadProjects()]);
    },
```

5. ProjectScreen: `skill={draftSkill}`, `onSkillChange={setDraftSkill}`,
   `onSend={(text) => chat.send(text, draftSkill, lastMode)}`; üstündeki yorum doğum değerini
   anlatır. ChatScreen: `skill={skillInForce}`, `onSkillChange={changeSkill}`,
   `onSend={(text) => chat.send(text, skillInForce, lastMode)}`; Madde 86 yorumu 105'e döner.

## C. Doğrulama ve kapanış

1. İki suite; altı kırmızı yeşerir, defter çifti dışında kırmızı kalmaz.
2. `npm run build --prefix queen-agent/frontend` — `dist` kaynakla aynı commit'te.
3. Commit: kod + dist + bu turun iki belgesi.

## Bilerek yapılmayanlar

- **`useChat.js` ellenmez** — skill mesajla zaten yolculuk ediyor.
- **`SkillPicker` ellenmez** — aldığı çift aynı.
- **Sunucu ellenmez.**
