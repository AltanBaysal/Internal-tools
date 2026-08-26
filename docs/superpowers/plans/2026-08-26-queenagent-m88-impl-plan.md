# Madde 88 · Tur 2 (kod) — Plan

**Tasarım:** [2026-08-26-queenagent-m88-cevabi-sunucu-baslatir-uygulama-design.md](../specs/2026-08-26-queenagent-m88-cevabi-sunucu-baslatir-uygulama-design.md)
**Bu turda yeni test yazılmaz.** On sekiz kırmızı *(`b39d92e`)* yeşile döner; test dosyalarında
değişen tek şey kodun şeklini takip eden fixture'lar.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
`npm run build --prefix queen-agent/frontend`

---

## 1. `domain/chat.py` — taşınan kural

`chat_title`'ın yanına:

```python
def is_owed_an_answer(chat):
    """Whether the last thing said in this chat was the user's.

    This lived in the browser until Madde 88, where it could run without anybody asking -- on a
    reload, and on a connection coming back. Here it can only be reached by a request.
    """
    return bool(chat.messages) and chat.messages[-1].role == "user"
```

## 2. `presentation/routes.py`

**Import:** `is_owed_an_answer` `chat.py`'den eklenir. `stream_answer` zaten import edilmiş.

**`post_answer` bütünüyle gider.**

**`post_message` kapının anlamını uygular:**

```python
    # One door, and one meaning: advance this chat. Text writes a message first; no text answers
    # what is already waiting, which is what Try again sends. The answer leaves down the same
    # connection, so the browser never opens a second one and nothing starts a turn by itself.
    @workspace_bp.post("/api/projects/<project_id>/messages")
    def post_message(project_id):
        payload = request.get_json(silent=True) or {}
        wanted = payload.get("chat", "")
        # Absent is not blank. A blank sentence is somebody leaning on the space bar and is
        # refused; no sentence at all means they are asking for the answer, not sending one.
        writing = "text" in payload
        if writing:
            try:
                chat = append_message(
                    chat_store,
                    project_id,
                    wanted,
                    payload["text"],
                    now=_now(),
                    skill=payload.get("skill", ""),
                    project_store=project_store,
                    new_id=_new_id("c"),
                )
            except ProjectNotFound:
                return jsonify({"error": "project not found"}), 404
            except ChatNotFound:
                return jsonify({"error": "chat not found"}), 404
            except EmptyMessage:
                return jsonify({"error": "a message needs text"}), 400
        else:
            chat = chat_store.get(project_id, wanted) if wanted else None
            if chat is None:
                return jsonify({"error": "there is nothing here to answer"}), 400
            if not is_owed_an_answer(chat):
                return jsonify({"error": "this chat has already been answered"}), 400
        return Response(
            _sse(
                chat.id,
                stream_answer(
                    chat_store, file_store, engine, project_id, chat.id, _now(), stops
                ),
            ),
            mimetype="text/event-stream",
        )
```

Doğrulamanın tamamı akıştan önce bitiyor, o yüzden 400 ve 404 hâlâ gerçek durum kodu.

**`_sse` id'yi alır ve önce onu söyler:**

```python
def _sse(chat_id, pieces):
    """Wrap the use case's output as events, telling them apart by type."""
    # First, before the model has said a word: the id cannot come back as a field any more, and the
    # browser needs it to change the address. Sent every time rather than only when it is news --
    # no condition here, and the browser acts only if it differs from what it holds.
    yield _frame("chat", {"chat": chat_id})
    try:
```

Gövdenin geri kalanı değişmiyor.

## 3. `frontend/src/features/workspace/useChat.js`

Kanca yeniden kuruluyor. Giden: `isOwedAnAnswer`, kendiliğinden çalışan efekt, `stopped`, `online`,
ayrı `ask`.

```js
export function useChat(projectId, chatId, onFileCreated, onChatBorn) {
  const [chat, setChat] = useState(null);
  const [error, setError] = useState(null);
  const [refused, setRefused] = useState(null);
  const [missing, setMissing] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [creatingFile, setCreatingFile] = useState(false);
  const [createdFiles, setCreatedFiles] = useState([]);
  const [streamingCalls, setStreamingCalls] = useState([]);

  const announce = useRef(onFileCreated);
  announce.current = onFileCreated;
  const born = useRef(onChatBorn);
  born.current = onChatBorn;
  // Which chat a stream is running into. The first frame changes the address, and the loading
  // effect below must not answer that change by throwing away what is arriving.
  const streamingInto = useRef(null);

  useEffect(() => {
    if (!projectId || !chatId) return undefined;
    if (chatId === streamingInto.current) return undefined;
    let cancelled = false;
    setChat(null);
    setError(null);
    setMissing(false);
    getJson(`/api/projects/${projectId}/chats/${chatId}`)
      .then((loaded) => {
        if (!cancelled) setChat(loaded);
      })
      .catch((failure) => {
        if (cancelled) return;
        if (failure.status === 404) setMissing(true);
        else setError(failure.message);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, chatId]);

  // One road for both jobs, since Madde 88: a sentence and a second attempt are the same request
  // with and without text. The answer comes back down it either way.
  const send = useCallback(
    async (text = null, skill = "") => {
      const at = new Date().toISOString();
      if (text !== null) {
        // The bubble appears before the server answers -- the design says so in as many words.
        setChat((current) =>
          current
            ? { ...current, messages: [...current.messages, { role: "user", at, text, pending: true }] }
            : { id: null, title: text, messages: [{ role: "user", at, text, pending: true }] },
        );
      }
      setRefused(null);
      setError(null);
      setThinking(true);
      setStreamingText("");
      setCreatingFile(false);
      setCreatedFiles([]);
      setStreamingCalls([]);
      const body = text === null ? { chat: chatId } : { chat: chatId ?? "", text, skill };
      try {
        await streamEvents(`/api/projects/${projectId}/messages`, (frame) => {
          if (frame.event === "chat") {
            streamingInto.current = frame.data.chat;
            if (frame.data.chat !== chatId) born.current?.(frame.data.chat);
          } else if (frame.event === "chunk") setStreamingText((t) => t + frame.data.text);
          else if (frame.event === "call") setStreamingCalls((calls) => [...calls, frame.data]);
          else if (frame.event === "file-start") setCreatingFile(true);
          else if (frame.event === "file") {
            setCreatedFiles((names) => [...names, frame.data.name]);
            setCreatingFile(false);
            announce.current?.();
          } else if (frame.event === "done") setChat(frame.data);
          else if (frame.event === "error") setError(frame.data.error);
        }, body);
      } catch (failure) {
        // Refused before anything was written: the optimistic bubble goes back out so the screen
        // never claims something was said when it was not.
        if (text !== null) {
          setChat((current) =>
            current
              ? {
                  ...current,
                  messages: current.messages.filter(
                    (message) => !(message.at === at && message.text === text),
                  ),
                }
              : current,
          );
        }
        setRefused(failure.message);
      } finally {
        setStreamingText("");
        setCreatingFile(false);
        setCreatedFiles([]);
        setStreamingCalls([]);
        setThinking(false);
      }
    },
    [projectId, chatId],
  );

  const stop = useCallback(async () => {
    await postJson(`/api/projects/${projectId}/chats/${chatId}/stop`, {}).catch(() => {});
  }, [projectId, chatId]);

  return {
    chat,
    error,
    refused,
    missing,
    thinking,
    streamingText,
    creatingFile,
    createdFiles,
    streamingCalls,
    send,
    stop,
    // Try again is the same road with no sentence on it: the question is already on disk.
    retry: () => send(null),
  };
}
```

**`streamEvents` bir gövde alacak.** Bugün gövdesiz POST atıyor; imzasına `body` eklenir ve
verildiğinde JSON olarak gönderilir. `shared/sse.js` açılır, koşarken bugünkü imzası okunur.

## 4. `frontend/src/App.jsx`

- `useChat` çağrısı `online` yerine bir `onChatBorn` alır:

```js
  const chat = useChat(
    route.projectId,
    drafting ? null : route.chatId,
    () => Promise.all([reloadFiles(), reloadProjects()]),
    (id) => {
      // The stream named a chat this screen was not on. It exists now, so the address follows it
      // and the lists that count chats are out of date.
      openChat(route.projectId, id, { replace: true });
      return Promise.all([reloadProjectChats(), reloadProjects()]);
    },
  );
```

`openChat` bu satırın **altında** tanımlı; ok fonksiyonunun içinde olduğu için çağrıldığı an
tanımlıdır, ama okunurluk için tanım sırası koşarken kontrol edilir ve gerekiyorsa `openChat`
yukarı alınır.

- `startChat` gider. `onSend` iki ekranda da `chat.send`'e bağlanır:

```js
            onSend={(text) => chat.send(text, lastSkill)}
```

- `ProjectScreen`'in `onSend`'i de aynı olur; `startChatInProject` importu ve kullanımı düşer.

## 5. Fixture — `test_chats_api.py`

`_started` akışın ilk karesinden id alır, ve `_answered` ona katılır:

```python
def _started(client, text="hello"):
    # A chat made through the door -- which since Madde 88 means it has been answered too, because
    # there is no way to write a message without the answer following it down the same connection.
    pid = _project(client)
    body = client.post(f"/api/projects/{pid}/messages", json={"text": text}).get_data(as_text=True)
    return pid, _named(body)
```

Bunu kullanan testlerden **mesaj sayısına ya da içeriğine bakanlar** düzeltilir: sohbet artık bir
cevapla birlikte doğuyor. Hangileri olduğu koşarak bulunur — kestirmek, kestirmenin kendisini
doğrulanacak bir şey yapar.

## Beklenen yeşil

On sekiz kırmızının hepsi. **İki kırmızı kalır ve bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Yeni test yazılmaz.**
- **`stream_answer.py` açılmaz.**
- **`/stop` ucuna dokunulmaz.** 90'ın işi.
- **`ports.py`'deki `Engine.model` parametresine dokunulmaz.** 82'den kalan ayrı bir tutarsızlık.
