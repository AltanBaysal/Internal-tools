# Madde 526 — Aracın kuralları, tasarımcı ve tasarım reviewer'ı, plan

**Hedef:** queen-studio'nun kural dosyaları ve backlog'u, iki tasarım agent'ı ve CLAUDE.md'nin dördüncü
aracı yerinde.

**Spec:** [m526](../specs/2026-11-06-queen-studio-m526-kurallar-ve-tasarimci-design.md)

## Kısıtlar

- Yalnız belgeler; kod ve test yok. Kural dosyaları, agent'lar ve CLAUDE.md İngilizce, `docs/` Türkçe.
- Tasarım adımındaki kural kopyalanmaz, adımına link verilir.
- Commit'i ana agent atar.

### Görev 1: queen-studio'nun dosyaları

- [ ] `queen-studio/FOUNDATION.md`: ilkeler ve kararlar, nedenleriyle, adımlara linkle.
- [ ] `queen-studio/CODE-STANDARD.md`: düzen, dil, mesajlar, maliyet, UI, kontrol araçları, testler.
- [ ] `queen-studio/BACKLOG.md`: başlık ve "Sonraya kalanlar"a gösteren bir satır.

### Görev 2: Agent'lar

- [ ] `.claude/agents/designer.md`: ne kurduğu, neyi yazmadığı, `frontend-design`, UX kontrol listesi,
  raporu.
- [ ] `.claude/agents/design-reviewer.md`: neye baktığı, neye bakmadığı, raporu.
- [ ] `.claude/agents/coder.md` ve `qa.md`: "dört suite" yerine maddenin suite'leri.

### Görev 3: CLAUDE.md

- [ ] Giriş: dört araç ve kural dosyaları.
- [ ] Commands: bir maddenin koştuğu suite'ler.
- [ ] Subagents: tasarımcı, tasarım reviewer'ı, iki akış; "dört suite" yerine maddenin suite'leri.
- [ ] Browser: tasarım maddesinde tasarımcı ve tasarım reviewer'ı da, sırayla.
- [ ] Designs: queen-studio'nun ekranları bu repoda, tasarımcıyla.
- [ ] Style: queen-studio'nun UI'ı İngilizce.

### Görev 4: Denetim

- [ ] Yeni ve değişen dosyalardaki her göreli link açılıyor.
- [ ] Var olan dört suite teker teker yeşil. Bir kerelik: queen-studio'nun henüz suite'i yok, ve
  belge değişikliği hiçbirine dokunmaz; yalnız kanıt için.
