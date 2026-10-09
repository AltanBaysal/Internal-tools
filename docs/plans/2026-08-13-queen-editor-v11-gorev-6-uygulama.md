# v11 Görev 6 — LLM açıklamaları kalkar: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `008001f`'deki iki kırmızı testi yeşile çevirmek ve koşuyu kapatmak.

**Architecture:** İki metin ve onları çizen eleman siliniyor.

**Tech Stack:** React 18, vitest, Vite build.

**Tasarım:** [implementasyon spec'i](../specs/2026-08-13-queen-editor-v11-gorev-6-uygulama-design.md)

## Global Constraints

- **Testler değişmiyor.** `008001f`'deki iki test sözleşme.
- Yorum ve commit mesajı **İngilizce**.
- **`dist/` aynı commit'te** yeniden derlenir.
- Commit mesajında **çift tırnak yok**.
- Komutlar: `npm test --prefix queen-editor/frontend` · `npm run build --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/LayerPanel.jsx` | panelin söyledikleri | 2 metin + 1 eleman silinir |
| `queen-editor/EKSIKLER.md` | bulunanlar listesi | bu koşunun kapattığı maddeler çıkar |
| `queen-editor/frontend/dist/` | Colab'ın servis ettiği paket | yeniden derlenir |

---

### Task 1: İki cümle ve onları çizen eleman silinir

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

- [ ] **Step 1: `WORDS`'ten iki `hint` satırını sil**

`video` ve `audio` girdilerinden `hint: ...` satırları çıkar. Geri kalan alanlar aynı sırada kalır.

- [ ] **Step 2: Paneli çizen `<Note>`'u sil**

```jsx
      <Note size={11} style={{ color: "var(--ink-4)", marginTop: "auto" }}>
        {words.hint}
      </Note>
```

tümüyle çıkar. `marginTop: "auto"` de onunla gidiyor — dibe itilecek bir şey kalmıyor.

- [ ] **Step 3: `Note` import'unun hâlâ kullanıldığını doğrula**

`Note` panelin başka yerlerinde de kullanılıyor (model adı, süre notu, tahmin satırı); import kalır.
Kalmadığını görürsen import da silinir.

- [ ] **Step 4: Ön yüz takımı**

Run: `npm test --prefix queen-editor/frontend`
Expected: 323 geçen, 0 düşen.

---

### Task 2: Liste bu koşunun kapattıklarından arınır

**Files:**
- Modify: `queen-editor/EKSIKLER.md`

- [ ] **Step 1: Kapanan altı maddeyi çıkar**

"## Sen" başlığından çıkanlar: xAI 400, durdu-ama-kuyrukta, seçili sayı artmıyor, halkalar kalıyor,
etiketin köşesi, LLM açıklaması.

Kalanlar: üç kurulum maddesi (foto 403, video 403, ses) — onları kullanıcının Colab turu kapatacak.
"## Claude" başlığı olduğu gibi kalır.

- [ ] **Step 2: Başlık cümlesini güncelle**

Dosyanın başındaki "Aşağıdakiler o koşudan artan, kararı sana kalan iki şey" cümlesi v7'ye
gönderiyor; v11'in ne kapattığını da söyleyecek şekilde yenilenir.

---

### Task 3: Derle ve commit'le

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist queen-editor/EKSIKLER.md docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): let the layer panels stop explaining themselves

The two tests from the previous commit go green, and v11 closes.

Both panels carried a line at the foot saying a language model writes the
prompt. Read once, then in the way on every open -- and the place a prompt is
actually read, the frame's own page, still says the model will write it when its
turn comes. The element goes with the text: an empty one left behind is an
invitation to put the sentence back.

EKSIKLER loses the six items this run closed and keeps the three about
installing, which only a Colab round can answer.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** iki metin + eleman→Task 1 · liste→Task 2 · `dist/`→Task 3. Eksik yok.

**Kontrol edilen yan etki:** `marginTop: "auto"` silinen elemandaydı; panelin öteki blokları
`gap: 14` ile aralanıyor, dolayısıyla dibe itilen bir şey kalmadığında yerleşim yukarıdan akmaya
devam ediyor.

**Liste kararı:** kapanan maddeler çıkarılıyor ama kurulumla ilgili üçü duruyor — çünkü onları
kapatacak olan test bende değil, kullanıcıda. Roadmap'in kapsam sınırı da bunu söylüyor.
