# v14 Görev 28 eki — Bekleyen karo da döner: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tek kırmızı testi yeşile döndürmek — bekleyen karo da dönsün.

**Architecture:** Tek dosya, tek koşul, bir yorum. Ardından ön yüz derlenir.

**Spec:** [Görev 28 eki implementasyon spec'i](../specs/2026-08-24-queen-editor-v14-gorev-28-halka-uygulama-design.md)

## Global Constraints

- **Test dosyasına dokunulmuyor.**
- Halkanın sınıfı `.wf-spinner` — `Rendering` onu kendi getiriyor, elle yazılmıyor.
- Dil: kod ve yorumlar **İngilizce**, commit mesajı **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- **`dist` kaynakla aynı commit'e girer.**
- Test komutları (depo kökünden, `cd` yok):
  `npm test --prefix queen-editor/frontend` · `python -m pytest queen-editor -q`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/features/photo_generation/TileImage.jsx` | karonun ne çizdiği | tek koşul + yorum |
| `queen-editor/frontend/dist/**` | defterin çalıştırdığı ön yüz | yeniden derlenir |

---

### Task 1: Tutucu artık izne bakmıyor

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/TileImage.jsx`

**Interfaces:**
- Consumes: `Rendering({ style })`.
- Produces: yok.

- [ ] **Step 1: Çizim bloğunu değiştir**

Bugünkü hâli:

```jsx
      {state !== "here" && (granted && state === "waiting"
        // Only the tile that holds the slot turns. Every tile is in the queue from the moment it
        // is built, so a ring on each of them would be a gallery of rings saying nothing.
        ? <Rendering style={style} />
        : <div className="wf-img" style={style} />)}
```

Yerine:

```jsx
      {state !== "here" && (state === "waiting"
        // Waiting and downloading look alike: with a single slot almost every tile is waiting, and
        // a gallery of still boxes reads as nothing happening. What it gives up is knowing which
        // tile holds the slot. The one that will never get its picture keeps the quiet box, so a
        // ring still means something is coming.
        ? <Rendering style={style} />
        : <div className="wf-img" style={style} />)}
```

`granted` değişkeni **duruyor** — fotoğrafın `src`'sini ve süreyi hâlâ o yönetiyor. Düşen yalnız
çizimdeki payı.

- [ ] **Step 2: Takımın yeşile döndüğünü gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: **553 passed.**

Düşen kalırsa: *leaves a quiet holder where a picture never arrived* düşüyorsa koşul `state !==
"gone"` gibi bir şeye çevrilmiştir — aranan `state === "waiting"`, çünkü gelmeyen karo halkasız
kalmalı.

---

### Task 2: Derle ve commit'le

- [ ] **Step 1: Python tarafını da gör**

Run: `python -m pytest queen-editor -q`
Expected: **711 passed.**

- [ ] **Step 2: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 3: Test dosyasının değişmediğini doğrula**

Run: `git status --short`
Expected: `TileImage.jsx`, `dist`, `docs/superpowers`. `*.test.*` bu listede **olmamalı.**

- [ ] **Step 4: Commit**

```bash
git add queen-editor/frontend docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): every tile that is still waiting turns

Green. The holder stopped asking whether this tile holds the slot and asks
only whether its picture is still coming, so the whole gallery turns while it
fills instead of one tile in ninety.

Which tile is really downloading is no longer visible anywhere. That was the
trade, made after seeing the still gallery rather than while reading about it.
The tile whose picture failed still keeps the quiet box, so a ring has not
become decoration -- it still says something is on its way.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** K1 → Task 1. Spec'in "dist aynı commit'e girer" kuralı → Task 2. Spec'te olup
planda karşılığı olmayan madde yok.

**Ad tutarlılığı:** Testin aradığı `.wf-spinner`'ı `Rendering` getiriyor; plan yeni bir sınıf adı
uydurmuyor.

**Yakalanan tuzak:** koşulun `state === "waiting"` yerine `state !== "gone"` yazılması. İkisi bu
blokta aynı görünüyor ama `here` durumunda ayrışıyorlar — dıştaki `state !== "here"` bunu şimdilik
örtüyor, yani hata bugün sessiz kalır ve blok bir gün değişince patlar. Step 2'de adıyla yazılı.

**Bilerek dışarıda:** `granted`'ın silinmesi. Çizimden düşüyor ama `src` ve süre hâlâ ona bağlı;
temizlik diye kaldırmak iki çalışan davranışı bozardı.
