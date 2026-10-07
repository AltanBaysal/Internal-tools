# Madde 106 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m106-akis-sohbetin-uygulama-design.md](../specs/2026-08-28-queenagent-m106-akis-sohbetin-uygulama-design.md)
**Tek dosya:** `queen-agent/frontend/src/features/workspace/useChat.js`
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. Yeni state ve ref'ler — `streamingInto`'nun altına

```js
  // The same fact for the screen: state rather than a ref, because what the hook returns is gated
  // on it and the gate has to move a render (Madde 106).
  const [streamingChatId, setStreamingChatId] = useState(null);
  // The chat the screen is on now, read where a stream ends: a turn that lands elsewhere must not
  // repaint this one.
  const live = useRef(chatId);
  live.current = chatId;
  // The record the hook holds now, read by the loading effect: the birth guard may only skip the
  // load when what is held already belongs here.
  const held = useRef(null);
  held.current = chat;
  // The send that owns the shared stream states -- the newest one. An older stream keeps running
  // on the server; what it may not do is draw on, or clear, a screen that is no longer its own.
  const owner = useRef(null);
```

## B. Yükleme etkisinin doğum koruması daralır

```js
    if (chatId === streamingInto.current) return undefined;
```

olur:

```js
    // Madde 88's birth guard, narrowed by Madde 106: skip the load only while what is held
    // already belongs here -- the stood-up draft record (id null) or this chat's own. A return
    // from another chat holds that chat's record, and the transcript comes back from disk.
    if (chatId === streamingInto.current && held.current) {
      const heldId = held.current.id;
      if (heldId === null || heldId === chatId) return undefined;
    }
```

## C. `send` — jeton, yerel hedef, kapılar

Başta *(`const at = ...` satırından önce)* jeton ve hedef; sıfırlamaların sonunda akış hedefi:

```js
      const token = {};
      owner.current = token;
      // Where this turn lands. Starts as the chat it was sent from; the first frame can name a
      // newborn instead. Local, so a send that lost the screen still knows its own chat.
      let target = chatId;
```

```js
      streamingInto.current = chatId;
      setStreamingChatId(chatId);
```

Kare işleyicisi: `chat` karesi `target`'ı her durumda yazar, gerisini yalnız sahipken; öteki
kareler tek kapının arkasına geçer, `file` karesinin `announce`'u kapının önünde kalır; `error`
karesi ayrıca `target === live` ister. Tur sonu okuması her durumda atılır, `setChat`/`setError`
yalnız `landed === live.current` iken; `catch`'teki `setRefused` aynı kapıdan; `finally` yalnız
sahipken temizler ve `streamingInto`/`streamingChatId`'yi null'a çeker.

## D. Dönüş kapısı

```js
  // What the stream draws belongs to the chat it runs into (Madde 106): standing elsewhere, none
  // of it shows -- and coming back, it shows again. The draft is its own chat here: null equals
  // null until the first frame names the newborn, and the address follows it.
  const visible = streamingChatId === (chatId ?? null);
```

Dönen demette: `thinking: visible && thinking`, `streamingText: visible ? streamingText : ""`,
`creatingFile: visible && creatingFile`, `createdFiles: visible ? createdFiles : []`,
`streamingCalls: visible ? streamingCalls : []`, `permission: visible ? permission : null`.
`chat`, `error`, `refused`, `missing` kapısız — `error` yazım anında kapılandı, sohbet değişimi
onu zaten temizliyor.

## E. Doğrulama ve kapanış

1. İki suite; üç kırmızı yeşerir, 560 yeşil, defter çifti dışında kırmızı yok.
2. `npm run build --prefix queen-agent/frontend` — `dist` kaynakla aynı commit'te.
3. Commit: kod + dist + bu turun iki belgesi.

## Bilerek yapılmayanlar

- **`App.jsx`, `ChatScreen.jsx` ellenmez** — kapı hook'un içinde, ekranlar aynı sözleşmeyi okur.
- **`stop`/`answer` ellenmez** — ikisi de görünür akışın sohbetine gider.
- **Sunucu ellenmez.**
