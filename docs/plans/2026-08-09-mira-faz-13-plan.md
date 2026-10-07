# Mira Faz 13 (Arama) — Uygulama Planı

**Hedef:** ⌘K paneli; proje adı, sohbet başlığı, dosya adı ve dosya içeriği; en fazla 8 sonuç; Esc
sıralaması (Madde 28).

**Mimari:** Tek uç nokta, sunucuda arama. Klavyenin tek sahibi `App`; `FilePanel` kendi Esc
dinleyicisini bırakır.

**Kaynak spec:** [Faz 13](../specs/2026-08-09-mira-faz-13-arama-design.md)

## Global Kısıtlar

- Eşleşme: büyük/küçük harf duymayan alt dize. Bulanık yok.
- Grup sırası: proje → sohbet → dosya adı → dosya içeriği. Toplam 8.
- Boş sorgu diski hiç okumaz.
- Test komutları: `python -m pytest d:\code\github\internal-tools\mira -q` ·
  `npm --prefix d:\code\github\internal-tools\mira\frontend test`.

---

### Task 1: `search` (arka uç)

**Dosyalar:** Değiştir `domain/file.py` (veya yeni `domain/hit.py`), `presentation/routes.py` ·
Oluştur `domain/usecases/search.py` · Test `backend/tests/test_search.py`

**Arayüzler:**
- Üretir: `Hit(kind, label, project_id, project_name, chat_id="", file_name="")` ·
  `search(project_store, chat_store, file_store, query, limit=8) -> list[Hit]`
- Tüketir: `ProjectStore.list_all`, `ChatStore.list_all`, `FileStore.list_files` / `read`.

- [ ] **Adım 1:** testleri yaz (spec §8'in 1-7'si) · **Adım 2:** kırmızı · **Adım 3:** yaz ·
      **Adım 4:** yeşil · **Adım 5:** commit.

```python
def search(project_store, chat_store, file_store, query, limit=LIMIT):
    needle = (query or "").strip().lower()
    if not needle:
        return []            # nothing typed, nothing read from disk
    ...
    # by name first, then by content: a name match is the stronger answer, and a file that
    # matches both ways is only listed once.
```

---

### Task 2: Panel ve klavye (ön yüz)

**Dosyalar:** Oluştur `features/workspace/useSearch.js`, `features/workspace/SearchPanel.jsx` ·
Değiştir `FilePanel.jsx` (Esc dinleyicisi gider), `Sidebar.jsx`, `App.jsx`, `workspace.css` · Test
`SearchPanel.test.jsx`, `FilePanel.test.jsx` (Esc testleri `App`'e taşınır), `App.test.jsx`

**Arayüzler:**
- Üretir: `useSearch() -> {query, setQuery, hits, searched}` · `<SearchPanel ... onPick />`
- Tüketir: Faz 10'un `reading` demeti (dosya sonucu `reading.open(name)` çağırır).

- [ ] **Adım 1:** testleri yaz (spec §8'in 8-11'i) · **Adım 2:** kırmızı · **Adım 3:** yaz ·
      **Adım 4:** yeşil · **Adım 5:** derle ve commit.

---

## Öz-denetim

**Spec kapsaması.** §1-3 Task 1 · §4-6 Task 2 · §5'teki klavye taşıması Task 2'nin ilk adımı.

**Ad tutarlılığı.** `kind` sunucuda ve çipte aynı sözcük (`project` / `chat` / `file`).
HTTP'de `projectId` / `projectName` / `chatId` / `fileName`.

**Risk.** `FilePanel`'in Esc testleri siliniyor; aynı davranış `App` testinde yeniden kuruluyor —
yoksa Faz 10'un bir sözü test edilmeden kalır.
