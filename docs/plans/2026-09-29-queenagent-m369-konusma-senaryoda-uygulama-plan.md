# Madde 369 — Konuşma senaryonun içine yazılır: uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Kırmızı iki testi yeşile getiren iki madde işareti: Start a scenario'nun Step 4'ünde
konuşmanın sahne cümlesine yazılması, kare yazarında sözlerin aksiyon satırına girmemesi.

**Mimari:** Yalnız metin, `prompt.py`'de iki sabit. Kod değişmez.

**Teknoloji:** Python sabitleri, pytest.

**Spec:** [2026-09-29-queenagent-m369-konusma-senaryoda-uygulama-design.md](../specs/2026-09-29-queenagent-m369-konusma-senaryoda-uygulama-design.md)

## Genel kısıtlar

- Modele giden metin sade, kısa İngilizce; bir kural bir kez, modelin onu okuduğu yerde.
- Start a scenario tavanı 1000 kelime; yeni sayı 504.
- `skip`/`xfail` yok; suite dört satırla, paralel, olduğu gibi.
- Commit mesajında çift tırnak yok, amend yok.

---

### Görev 1: `prompt.py`

**Dosyalar:** Değişir: `queen-agent/backend/features/workspace/domain/prompt.py`

**Arayüzler:** Değişen sabitler: `START_A_SCENARIO`, `WRITE_FRAME_SYSTEM_PROMPT`. Adları ve türleri aynı.

- [ ] **Adım 1: Step 4.** `"- Write them with add_scene: one sentence each, in the language the user is writing in.\n"`
  satırının altına:

```python
    "- If the user wants someone to speak in a frame, write their words, in quotation marks, "
    "into that frame's scene sentence: the video's prompt is written from it.\n"
```

- [ ] **Adım 2: Kare yazarı.** `"not write that they take it off.\n"` ile biten madde işaretinin altına,
  `"\n" + SDXL_PROMPT_RULES`'tan önce:

```python
    "- If somebody speaks in the scene, leave their words out of your line. The model cannot "
    "draw speech, and quoted words come back drawn as text in the picture.\n"
```

### Görev 2: Yeşil

- [ ] Dört satır, paralel, olduğu gibi. Beklenen: queen-agent arka ucu 971 geçti; öteki üçü kırmızı
  turdaki gibi.
- [ ] Commit: `feat: Madde 369 -- speech the user wants rides in the frame's scene sentence`
