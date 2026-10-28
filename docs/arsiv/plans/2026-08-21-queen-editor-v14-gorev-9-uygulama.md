# v14 Görev 9 — Detayda Yeni mod seçicisi: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün bıraktığı kırmızıyı — ön yüzde on test, python tarafında bir koleksiyon
hatası — yeşile döndürmek.

**Architecture:** Önce ortak eve taşınan iki kural, sonra onları kullanan yeniden üretim, sonra uç,
sonra ekranın üç parçası.

**Tech Stack:** Python 3.13, React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-9-yeni-mod-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor — üç mekanik düzeltme dışında.** Üçü de test turunun
  atladığı ve hiçbiri bir testin ne tarif ettiğine dokunmuyor:

  | Nerede | Ne | Neden |
  |---|---|---|
  | `test_photo_usecases.py` içe aktarımı | `InvalidMode` artık `production_mode`'dan | Bir adın taşınması onu içe aktaran her yeri kapsar. |
  | 8. maddenin iki testi | `getByText("Loop")` yerine satırın kendisi | "Loop" artık sayfada iki yerde: bilgi satırında ve seçicinin bir seçeneğinde. İddia aynı, seçici belirsizleşti. |
  | `sends the open layer and the edited text` | beşinci argüman `"standard"` | `regenerateFrame` bir argüman kazandı; testin ölçtüğü şey ilk dördü. |
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.
- **Mod verilmeyen çağrı bugünkü gibi kalıyor.** Planda `mode` alanı doğmuyor, ve `run_loop`
  onu zaten yokluğuna göre okuyor.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/.../domain/production_mode.py` | modun ortak kuralları | `InvalidMode`, `validate`, `frame_after` |
| `backend/.../domain/usecases/queue_layer.py` | kuyruk | iki tanım siliniyor, ortak eve çağrı |
| `backend/.../domain/usecases/regenerate.py` | yeniden üretim | `NoNextFrame`, `mode`, `linkedTo` |
| `backend/.../presentation/routes.py` | uç | gövdeden `mode`, iki 400 |
| `frontend/.../production_modes.js` | modun ismi | `nounOf` |
| `frontend/.../LayerPanel.jsx` | panelin cümlesi | `MODE_WORDS` → `MODE_TAIL` |
| `frontend/src/shared/api.js` | istek gövdesi | `mode` |
| `frontend/.../useGeneration.js` | hook | `mode` |
| `frontend/.../PhotoDetail.jsx` | formun üç parçası | select, sebep, satır |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Ortak ev

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/production_mode.py`
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/queue_layer.py`

**Interfaces:**
- Produces: `production_mode.InvalidMode`, `production_mode.validate(mode, kind)`,
  `production_mode.frame_after(gallery, fid) -> str | None`. Task 2 ve Task 3 okuyor.

- [ ] **Step 1: `production_mode.py`'yi genişlet**

Modülün belgesinin altına, `STANDARD` tanımlarının üstüne:

```python
from backend.features.photo_generation.domain import layers, queue
```

`of`'un altına:

```python
class InvalidMode(Exception):
    """A production mode nobody knows, or one given to a layer that ends nowhere.

    Lives here rather than with either use case: two of them raise it, and the rule it stands for is
    about modes.
    """


def validate(mode, kind):
    """Refuse a mode this list does not know, or one asked of a layer that arrives nowhere.

    Both callers -- the queue and making a layer again -- want exactly these two answers, so they
    ask once rather than each keeping a copy that could drift.
    """
    if mode not in ALL:
        raise InvalidMode(f"Üretim modu şunlardan biri olmalı: {', '.join(ALL)}.")
    if mode != STANDARD and kind != layers.VIDEO:
        # Only a video ends on a picture. Ignoring the argument would hide the caller's mistake
        # behind a sound that came out fine.
        raise InvalidMode("Üretim modu yalnız video işine verilebilir.")


def frame_after(gallery, fid):
    """The frame a linked video ends on: the one that comes after it in the film.

    The film's sequence, not the gallery's reading order. The gallery is newest-first and the export
    stitches it reversed (export_summary.exportable) -- the foot of the gallery is the film's first
    frame -- so the frame that plays next is the one ABOVE, at index - 1. Linking downwards would
    make every chain run against the film it is part of.

    None where there is nothing to end on: the last frame of the film -- the top of the gallery --
    has no next, and a next whose photo never landed is the same emptiness seen from closer up.
    """
    for index, frame in enumerate(gallery):
        if frame["id"] != fid:
            continue
        after = gallery[index - 1] if index > 0 else None
        return after["id"] if after and after["status"] == queue.DONE else None
    return None
```

- [ ] **Step 2: `queue_layer`'ı ortak eve bağla**

`InvalidMode` sınıfı ve `_frame_after` fonksiyonu siliniyor. `_mark` içindeki çağrı:

```python
    target = production_mode.frame_after(gallery, fid)
```

Doğrulamanın iki `if`'i tek satır oluyor:

```python
    production_mode.validate(mode, kind)
```

Ve içe aktarımın yanına, adın buradan da okunabilmesi için değil, **kullanılabilmesi** için bir şey
gerekmiyor: `queue_layer` `production_mode`'u zaten içe aktarıyor.

`InvalidMode`'u dışa verenler onu artık `production_mode`'dan alıyor — `routes.py` Task 4'te.

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: hâlâ koleksiyon hatası (`NoNextFrame` yok), ama `test_photo_routes.py`'nin
`from ...queue_layer import InvalidMode` satırı varsa o da kırılır — Task 4'te düzeliyor.

---

### Task 2: Yeniden üretim modu alıyor

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/regenerate.py`

**Interfaces:**
- Consumes: Task 1'in `validate` ve `frame_after`'ı.
- Produces: `NoNextFrame`, ve `regenerate(..., mode=…)`.

- [ ] **Step 1: İçe aktarım ve istisna**

```python
from backend.features.photo_generation.domain import layers, production_mode, queue
```

`LayerMissing`'in altına:

```python
class NoNextFrame(Exception):
    """A linked video was asked for on a frame the film has nothing after (message is user-facing).

    Its own exception rather than InvalidMode: the mode is a real one and the request is
    understood -- what is missing is a frame to end on.
    """
```

- [ ] **Step 2: İmza ve doğrulama**

```python
def regenerate(runner, store, record, plan_store, order_store, producers, new_seed, now,
               project, fid, kind, prompt, log=None, writers=None,
               mode=production_mode.STANDARD):
```

Belgesine bir paragraf:

```python
    """Returns the identity of the frame the new layer will be made on.

    The source is named by its identity rather than by a file: a copy frame shares its source's
    picture (madde 102), so one file name can belong to two frames and each of them has its own
    layer to make again.

    `mode` is what the new video should be, and the form's default is the source video's own -- so
    changing only the prompt keeps the video the user had (madde 94). A linked one's target is
    worked out here, from the gallery already open on this side.
    """
```

Gövdenin başına, galeriyi okuduktan **sonra** (hedef ona bağlı) ama plan yazılmadan önce:

```python
    production_mode.validate(mode, kind)
```

`validate` galeriden bağımsız olduğu için fonksiyonun ilk satırı olabilirdi; galeri okumasının
üstünde duruyor, çünkü ucuz olan önce reddeder ve olmayan bir projede bile mod hatası mod hatasıdır.

- [ ] **Step 3: Hedefi bul ve işe yaz**

`carry_layers` çağrısının üstüne:

```python
    mark = {} if mode == production_mode.STANDARD else {"mode": mode}
    if mode == production_mode.LINKED:
        target = production_mode.frame_after(gallery, fid)
        if target is None:
            # Named rather than planned with nothing: a job carrying no target reaches the render
            # and fails there on a frame it cannot even name.
            raise NoNextFrame("Bu son kare — bağlanacak sonraki kare yok.")
        mark["linkedTo"] = target
```

ve plan satırına `**mark`:

```python
        "model": source.get("model", "") if kind == layers.PHOTO else "",
        **mark,
    }])
```

Standart modda `mark` boş: bugüne kadarki her çağıran mod vermiyordu ve planın aynı şekilde okunmaya
devam etmesi gerekiyor.

- [ ] **Step 4: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: koleksiyon açılıyor. Kalan kırmızılar: uç testlerinin ikisi, ve varsa
`test_photo_routes.py`'nin içe aktarımı.

---

### Task 3: Uç modu okuyor

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/presentation/routes.py`

- [ ] **Step 1: İçe aktarımları düzelt**

`InvalidMode` artık `production_mode`'dan:

```python
from backend.features.photo_generation.domain.production_mode import InvalidMode
from backend.features.photo_generation.domain.usecases.queue_layer import InvalidScope
from backend.features.photo_generation.domain.usecases.regenerate import LayerMissing, NoNextFrame
```

Dosyadaki bugünkü satırlar neyse onlara göre uyarlanır; kural tek: `InvalidMode` `production_mode`'dan
gelir.

- [ ] **Step 2: Gövdeden modu geçir**

```python
            frame = regenerate(project, body.get("frame"), layer,
                               prompt if isinstance(prompt, str) else "",
                               mode=body.get("mode", production_mode.STANDARD))
```

ve iki istisna 400'e:

```python
        except LayerMissing as exc:
            return jsonify({"error": str(exc)}), 400
        except (InvalidMode, NoNextFrame) as exc:
            return jsonify({"error": str(exc), "field": "mode"}), 400
```

`field: "mode"` — kuyruk ucunun `InvalidMode` cevabıyla aynı şekil, çünkü aynı şeyi söylüyorlar.

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: python tarafı yeşil.

---

### Task 4: Modun ismi ortak eve

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/production_modes.js`
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

**Interfaces:**
- Produces: `nounOf(mode, plain) -> string`. Panel ve detay sayfası okuyor.

- [ ] **Step 1: `nounOf`'u yaz**

`labelOf`'un altına:

```js
// What each mode calls what it makes. No row for the plain one: what it makes is the layer's own
// noun -- video in one panel, ses in the other -- and this module has no layer.
const NOUN = { [LOOP]: "loop video", [LINKED]: "bağlı video" };

/** The mode's own noun for what it produces; `plain` is what the caller calls it otherwise. */
export function nounOf(mode, plain) {
  return NOUN[mode] || plain;
}
```

- [ ] **Step 2: Panelin `MODE_WORDS`'ünü kuyruğa indir**

```jsx
/** What a mode promises about what it makes.
 *
 * No row for the plain mode: its promise is the layer's own line, built from the layer's words. The
 * noun each mode uses lives with the modes themselves (nounOf) -- two screens say it now.
 */
const MODE_TAIL = {
  [LOOP]: "her video kendine döner.",
  [LINKED]: "her video sıradaki karede biter.",
};
```

ve `said` hesabı:

```jsx
  const said = { noun: nounOf(mode, words.noun),
                 tail: MODE_TAIL[mode] || `her kare kendi ${words.own} alır.` };
```

Onay kartındaki `(MODE_WORDS[added.mode] || words).noun` de:

```jsx
              {added.count} {nounOf(added.mode, words.noun)} kuyruğa eklendi
```

İçe aktarım: `import { LINKED, LOOP, MODES, STANDARD, nounOf } from "./production_modes.js";`

- [ ] **Step 3: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: `LayerPanel.test.jsx`'in 43'ü hâlâ yeşil — kelime taşındı, cümle değişmedi.
`PhotoDetail`'in on kırmızısı duruyor.

---

### Task 5: Mod istekle gidiyor

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js`
- Modify: `queen-editor/frontend/src/features/photo_generation/useGeneration.js`

- [ ] **Step 1: `api.js`**

```js
export async function regenerateFrame(project, frame, layer, prompt, mode) {
  return request(`/api/projects/${encodeURIComponent(project)}/regenerate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ frame, layer, prompt, mode }),
  });
}
```

- [ ] **Step 2: `useGeneration.js`**

```js
  const regenerate = useCallback((frame, kind, prompt, mode) => (
    regenerateFrame(project, frame, kind, prompt, mode)
```

- [ ] **Step 3: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: değişen bir şey yok — çağıran henüz mod vermiyor.

---

### Task 6: Formun üç parçası

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`

**Interfaces:**
- Consumes: `nounOf`, `labelOf`, `MODES`, `STANDARD`, `LINKED`, `frame.modes`, `frames`, `index`.

- [ ] **Step 1: İçe aktarım ve durum**

```jsx
import { LINKED, MODES, STANDARD, labelOf, nounOf } from "./production_modes.js";
```

`sent` durumunun yanına:

```jsx
  // What the video should be made in next. Untouched until the box is used, so the default can
  // follow the poll: null means the video's own mode, whatever the record last said it was.
  const [newMode, setNewMode] = useState(null);
```

ve `[fid]` efektine `setNewMode(null);` — kutu, arkasındaki kareyle birlikte gider.

- [ ] **Step 2: Kuralı hesapla**

`arrivesAt`'in altına:

```jsx
  // The mode the form would send. This video's own until the box is touched (madde 94).
  const picked = newMode ?? madeIn ?? STANDARD;
  // What a linked one would end on. The same question the server asks: the gallery's top is the
  // film's last frame, and a next whose picture has not landed is no target either.
  const after = index > 0 ? frames?.[index - 1] : null;
  const noTarget = picked === LINKED
    && (index === 0
      ? "Bu son kare — bağlanacak sonraki kare yok."
      : after?.status === "done" ? null : "Sonraki karenin fotoğrafı henüz üretilmedi.");
```

`noTarget` ya bir cümle ya `null`/`false` — kapanmanın kendisi ve sebebi tek değerde, çünkü ikisi
hiç ayrılmıyor.

- [ ] **Step 3: Kutuyu, sebebi ve satırı çiz**

`holds && (…)` butonunun **üstüne**, formun kendi bloğu olarak:

```jsx
            {holds && open === "video" && (
              /* Only a video arrives at a picture, so only its form has this to ask. */
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                <Mono size={10} style={LABEL} id="yeni-mod">Yeni mod</Mono>
                <select className="wf-input" aria-labelledby="yeni-mod" value={picked}
                        onChange={(e) => setNewMode(e.target.value)}
                        style={{ fontSize: 12.5, color: "var(--ink)", cursor: "pointer",
                                 // Danger first: a box that cannot be pressed through must not look
                                 // like an ordinary change.
                                 borderColor: noTarget ? "var(--danger)"
                                   : picked !== (madeIn ?? STANDARD) ? "var(--accent)" : undefined }}>
                  {MODES.map((one) => (
                    <option key={one.id} value={one.id}>{one.label}</option>
                  ))}
                </select>
                {noTarget && <Note size={12} style={{ color: "var(--danger)" }}>{noTarget}</Note>}
              </div>
            )}
```

ve butonun **altına**:

```jsx
            {holds && open === "video" && (
              /* What one press opens, in the mode's own words: a copy frame beside this one, never
                 a video written over the one that is here (madde 77). */
              <Note size={12} style={{ color: "var(--ink-3)", textAlign: "center" }}>
                Yeni bir kare açılır — {frame.id} kopyası, {nounOf(picked, "video")}.
              </Note>
            )}
```

Butonun kendisi `disabled={sent.includes(open) || Boolean(noTarget)}`.

- [ ] **Step 4: Modu gönder**

```jsx
    return regenerate(frame.id, layer, typed, layer === "video" ? picked : undefined)
```

Video dışı katmanda `undefined`: sunucu gövdede mod olmayan isteği bugünkü gibi okuyor, ve bir sese
mod göndermek `InvalidMode` demek olurdu.

- [ ] **Step 5: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil.

---

### Task 7: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

9. maddenin **İş** hücresi ✅ ile başlar, sayaç `8/31` → `9/31`. B bölümü bitiyor.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the regenerate form asks which mode the new video should be

A Yeni mod box on the video tab, opened on the mode this video was made in. Editing only
the prompt and pressing once now gives back the video that was there -- until today a
loop made again came back plain and lost its badge.

A linked one's target is found on the server, from the gallery it already holds. The
last frame of the film is refused there with a reason of its own: a job planned with
nothing to end on would reach the render and fail on a target it could not name.

The screen shuts the button before that request can leave, and it asks the server's own
question rather than only the design's. The design named the last frame; a next frame
whose picture has not landed is no target either, and letting it through would be the
error-after-the-press the design refused. Two cases, two sentences, one closed button.

Which frame comes next, and whether a mode may be asked of a layer, now live with the
modes themselves. The queue and the regenerate both call them instead of each keeping a
copy. The mode's noun moved the same way: two screens say loop video now.

Nothing changes for a caller that names no mode -- the plan gains no field, and the
engine already reads its absence as plain.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** motor tarafı Task 1–3, ekran tarafı Task 4–6.

**Tip tutarlılığı:** `validate(mode, kind)` iki çağıranda da aynı sırayla; `frame_after` üç
çağıranda (`_mark`, `regenerate`, testler) aynı imzayla. `nounOf(mode, plain)` iki ekranda da iki
argümanla.

**Kontrol edilen tuzak:** `noTarget` bir cümle ya da yalancı bir değer. `picked !== LINKED` iken
`&&` kısa devre yapıp `false` üretiyor, `Boolean(noTarget)` de onu `false`'a çeviriyor — buton
açık kalıyor.

**Kontrol edilen tuzak 2:** kenarlıkta tehlike önce sorgulanıyor. Vurgu önce gelseydi, bağla
seçildiği anda kutu hem değişmiş hem kapalı olur ve vurgu rengiyle çizilirdi.

**Kontrol edilen tuzak 3:** `picked !== (madeIn ?? STANDARD)` — modu yazılmamış bir videoda
`madeIn` yok, ve `picked` da `STANDARD`. `madeIn` ile doğrudan karşılaştırmak, o kutuyu açılır
açılmaz değişmiş gösterirdi.

**Kontrol edilen tuzak 4:** `regenerate` çağrısı video dışı katmanda `undefined` veriyor.
`picked`'i her zaman göndermek, foto sekmesinde `standard` göndermek demekti — bugün geçerli ama
`validate` bir gün standart olmayan varsayılan görürse sessizce yanlış tarafa düşerdi.

**Kontrol edilen tuzak 5:** `setNewMode(null)` `[fid]` efektinde. Kalsaydı, oklarla geçilen bir
sonraki karenin kutusu öncekinin seçimini gösterirdi.

**Kontrol edilen sınır:** `validate` galeri okumasının üstünde. Olmayan bir projede bile bilinmeyen
mod bilinmeyen moddur, ve ucuz olan önce reddeder.