# Madde 421 — Queen AI'ın H3 metninde uzunluk yok, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır, ana klasörde (`feat/queen-editor-v9`). Kod yazılır, dört satır
> koşulur, yeşil görülür. **Commit yok:** 422'yle birlikte kullanıcının Changes'inde okunur.

**Hedef:** `H3_VIDEO_INSTRUCTION`'dan iki uzunluğu çıkarmak, ve artık doğru olmayan bir yorumu
düzeltmek.

**Yaklaşım:** Tek dosya, üç satır; başka hiçbir şey değişmez.

**Spec:** [m421 uygulama turu](../specs/2026-10-06-queen-editor-m421-h3-uzunluk-yok-uygulama-design.md)

## Her yere geçerli kurallar

- Talimat İngilizce kalır; yorum İngilizce, neden'i söyler.
- Testlere dokunulmaz.

---

## Görev 1: `prompt_writer.py`

**Dosya:** Değiştir: `queen-editor/backend/features/photo_generation/data/prompt_writer.py`

- [ ] **Adım 1: *Context*'in ilk satırı.**

```
- H3 makes a video of four seconds, with sound, from a photo.
```
→
```
- H3 makes a video, with sound, from a photo.
```

- [ ] **Adım 2: *Rules*'un hareket satırı.**

```
- Then write what moves and how, in order, from the first frame to the end of the video. Write only what fits in four seconds.
```
→
```
- Then write what moves and how, in order, from the first frame to the end of the video.
```

- [ ] **Adım 3: `LOOP_RULE`'un yorumu.**

```python
# to land on that frame and the next repeat starts from rest, which reads as a pulse every four
# seconds. A motion that returns arrives there by its own rhythm instead.
```
→
```python
# to land on that frame and the next repeat starts from rest, which reads as a pulse each time the
# clip starts again. A motion that returns arrives there by its own rhythm instead.
```

## Görev 2: Koşu — yeşil

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil; test turunun iki kırmızısı yeşile döndü.

- [ ] **Adım 2: Commit yok.**
