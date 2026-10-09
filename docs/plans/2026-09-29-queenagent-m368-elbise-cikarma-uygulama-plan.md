# Madde 368 — Elbise çıkarma sahnesi senaryoya, aksi söylenmedikçe eklenmez: uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Start a scenario'nun sahneler adımına, kıyafetin sahneden sahneye değişebildiğini ve
çıkarıldığı ya da değiştirildiği anın kullanıcı istemedikçe sahne olarak yazılmadığını söyleyen madde.

**Mimari:** `START_A_SCENARIO`'ya tek bir madde; başka metin, kod ya da test değişmez.

**Teknoloji:** Python string sabiti.

**Spec:** [2026-09-29-queenagent-m368-elbise-cikarma-uygulama-design.md](../specs/2026-09-29-queenagent-m368-elbise-cikarma-uygulama-design.md)

## Genel kısıtlar

- Modele giden metin İngilizce, düz ve kısa.
- Start a scenario tavanı 1000 kelime *(test_skills.py)*; yeni sayı 479.
- Suite yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşar.
- Commit mesajında çift tırnak yok, amend yok.

---

### Görev 1: Sahneler adımı

**Dosyalar:** Değişir: `queen-agent/backend/features/workspace/domain/prompt.py` (`START_A_SCENARIO`,
Step 4)

- [ ] **Adım 1:** `add_scene` maddesinin altına, `Write no actions here.`'dan önce:

```python
    "- Write them with add_scene: one sentence each, in the language the user is writing in.\n"
    "- What someone wears can change from one scene to the next. The moment clothes are taken "
    "off or changed is not written as a scene unless the user asks for it: the model cannot "
    "draw it.\n"
    "- Write no actions here.\n"
```

- [ ] **Adım 2: Yeşil.** Dört satır, paralel, olduğu gibi. Beklenen: hepsi yeşil;
  `test_the_scenes_step_writes_no_frame_of_clothes_coming_off_unless_asked` geçer, tavan testi
  yeşil kalır.
- [ ] **Adım 3: Commit:** `feat: Madde 368 -- the scenes step writes no frame of clothes coming off unless asked`
