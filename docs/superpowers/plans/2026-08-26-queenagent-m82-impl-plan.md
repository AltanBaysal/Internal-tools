# Madde 82 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-26-queenagent-m82-model-secimi-sokulur-uygulama-design.md](../specs/2026-08-26-queenagent-m82-model-secimi-sokulur-uygulama-design.md)
**Kırmızı testler:** `0643b00`.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

**Sıra alttan üste:** domain → veri → sunum → kablolama → ön yüz. Her adım bir öncekinin
kaldırdığı şeye dayanıyor.

---

## Arka uç

### 1. `domain/chat.py` — alan gider

`Chat.model` ve üstündeki üç satırlık yorum siliniyor. `skill`'in yorumu *"unlike a model"* diyor;
karşılaştıracak bir şey kalmadığı için o cümle de düzeliyor.

### 2. `domain/usecases/start_chat.py` — parametre gider

`model=""` parametresi ve `Chat(...)`'e geçtiği yer.

### 3. `domain/usecases/set_chat_choices.py` → `set_chat_skill.py`

`git mv`, sonra içerik:

```python
"""Change which skill governs a chat's turns.

Works mid-conversation. Only the next answer changes -- what was already said was said under
whatever governed it then, and nothing in this app rewrites a message.
"""
from dataclasses import replace

from backend.features.workspace.domain.errors import ChatNotFound


def set_chat_skill(chat_store, project_id, chat_id, skill):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)
    changed = replace(chat, skill=skill)
    chat_store.replace(project_id, changed)
    return changed
```

`UNCHANGED` gidiyor: iki alan varken *"verilmedi"* ile *"boş verildi"*yi ayırmak gerekiyordu, tek
alanlı bir çağrıda alan hep veriliyor.

`test_set_chat_choices.py` → `test_set_chat_skill.py` (`git mv`), import ve dört çağrı yeni ada
geçiyor.

### 4. `data/file_chat_store.py` — yazma ve okuma gider

`model` yazan satır ve `model=raw.get("model", "")` okuyan satır. Diskteki eski anahtar
görülmüyor; sohbet bir daha yazıldığında düşüyor.

### 5. `presentation/routes.py` — uç nokta ve zincir gider

- `GET /api/model` bloğu siliniyor.
- `make_workspace_bp(..., default_model, stops)` → `make_workspace_bp(..., stops)`.
- `_sse(pieces, default_model)` → `_sse(pieces)`; `_chat_json(piece, default_model)` →
  `_chat_json(piece)`.
- `_chat_summary(chat, default_model)` ve `_chat_json(chat, default_model)` parametrelerini
  bırakıyor; `"model": chat.model or default_model` satırı gidiyor.
- POST'ta `model=payload.get("model", "")` gidiyor.
- PATCH:

```python
        # The skill is the only thing about a chat that changes. A title arriving here is not a
        # rename that failed quietly, and neither is a model: both are requests this route does
        # not understand.
        if "skill" not in payload:
            return jsonify({"error": "a chat only carries a skill"}), 400
        try:
            chat = set_chat_skill(chat_store, project_id, chat_id, payload["skill"])
```

`UNCHANGED` importu da gidiyor.

### 6. `domain/usecases/stream_answer.py` — model geçilmiyor

```python
            for piece in engine.stream(conversation, tools=TOOL_SPECS):
```

Üstündeki iki satırlık yorum *(None rather than a name…)* gidiyor: anlattığı seçim kalmadı.

### 7. `data/xai_engine.py` ve `services/xai/client.py` — parametre gider

Her ikisinde `complete`/`stream`'in `model=None` parametresi, ve `client.py`'de `_request`'inki.
İstek:

```python
        # One model, named once where the client is built.
        payload = {"model": self._model, **body}
```

`# The caller's model wins…` yorumu gidiyor.

### 8. `main.py` — bir argüman az

`make_workspace_bp(...)` çağrısından `config.XAI_MODEL` çıkıyor. `XaiClient(...)`'e verilen
`config.XAI_MODEL` **kalıyor** — modelin adının geçtiği tek yer orası.

### 9. `test_chats_api.py` ve `test_stream_answer.py` — fixture'lar daralır

Test turunda bilerek bırakılmışlardı. `_client`'tan `default_model` çıkıyor, paylaşılan sahte
motorların `stream`'inden `model=None` çıkıyor, ve o dosyalardaki `StrictEngine` sınıfları artık
gereksiz — paylaşılanlar zaten katı oldu, ikisi siliniyor ve testleri paylaşılanı kullanıyor.
`test_xai_engine.py`'de aynısı: `StrictClient` gidiyor, `FakeClient` katı oluyor.

## Ön yüz

### 10. `ModelLabel.jsx` — yeni

```jsx
// Which model answers, and that is all: since Madde 82 there is one, so there is nothing to
// choose. config.py holds its id; this holds the name a person reads, and the two move together.
// A span rather than a button -- a control that opens nothing would be a promise the app cannot
// keep.
export default function ModelLabel() {
  return <span className="model-label">Grok Build</span>;
}
```

### 11. `ModelPicker.jsx` ve `models.js` silinir

`git rm`. İkisinin de tek tüketicisi seçiciydi.

### 12. `ChatScreen.jsx` ve `ProjectScreen.jsx` — etiket geçer

`ModelPicker` importu `ModelLabel` oluyor, elemanı `<ModelLabel />`. `onModelChange` prop'u
ChatScreen'den, `model` ile `onModelChange` ProjectScreen'den gidiyor. `picker`/`onPicker` →
`skillsOpen`/`onToggleSkills`, ve `SkillPicker`'a `open={skillsOpen}` ile
`onToggle={onToggleSkills}` geçiyor.

`karar 1`'in sırasını anlatan yorum düzeliyor: ortadaki artık bir denetim değil.

### 13. `App.jsx` — tutulan şey gider

- `lastModel` durumu, `/api/model` `useEffect`'i, `chooseModel`.
- `picker` → `skillsOpen` boolean'ı; `togglePicker` → `toggleSkills`.
- Escape'in `picker === "model"` dalı; `fark 67`'yi anlatan yorum dörde iniyor.
- İki ekrana geçen `model` / `onModelChange` prop'ları.
- `DRAFT`'a eklenen `model: lastModel`.

### 14. `useChatLists.js` — parametre gider

```js
export function startChatInProject(projectId, text, skill = "") {
  return postJson(`/api/projects/${projectId}/chats`, { text, skill });
}
```

`App.jsx`'teki çağrısı da bir argüman kaybediyor.

### 15. `workspace.css` — etiket gelir

`.picker`'ın yanına:

```css
/* The model's name, sitting where its picker used to. Not a control since Madde 82: it reads like
   the button beside it and does nothing, so it takes the picker's type without its hover. */
.model-label {
  padding: 6px 9px;
  font-size: 13px;
  color: var(--muted);
}
```

`.menu__label`'ın yorumu *"the model's says MODEL"* diyor — tek menü kaldı, cümle düzeliyor.

### 16. `dist` derlenir

`npm run build --prefix queen-agent/frontend`, kaynakla **aynı commit'e**.

## Beklenen yeşil

İkisi de yeşil; arka uçta yalnız defterin iki kırmızısı kalır.

**Düşmemesi gerekenler:** skill seçiminin bütün testleri, `Menu`, `SkillPicker`, `test_config.py`.
Biri düşerse sökülen şey sökülmemesi gereken bir yere dokunmuş demektir, ve o zaman **kod düzelir,
test değil**.

## Bilerek yapılmayanlar

- **`config.XAI_MODEL` kalıyor.** Modelin adının geçtiği tek yer.
- **Diskteki kayıtlara dokunulmuyor.** Göç yok; anahtar okunmuyor ve bir dahaki yazımda düşüyor.
- **`SkillPicker`, `Menu`, `.picker` açılmıyor** *(prop adları hariç)*. Skill seçimi gerçek bir
  seçim ve olduğu gibi duruyor.
