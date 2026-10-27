# Madde 500 — Eski belgeler ve roadmap'ler arşive, plan

**Hedef:** biten roadmap'ler ve belgeleri `docs/arsiv/`'de, on not `docs/arsiv/notlar/`'da, her link
açılıyor.

**Spec:** [m500](../specs/2026-10-27-queen-editor-m500-arsiv-design.md)

## Kısıtlar

- Yalnız belgeler ve onlara giden linkler değişir; kod ve test değişmez.
- Taşıma `git mv`'yle. Betikler `tmp/`'de durur ve iş bitince silinir.
- Önceden kırık linkler düzeltilmez, listede ayrı kalır.
- Commit'i ana ajan atar.

### Görev 1: Taban

- [ ] `tmp/m500_links.py`: repodaki her `.md`'nin her göreli linkini ve `#anchor`'ını çözen denetçi;
  kod bloklarını ve satır içi kodu atlar.
- [ ] Taşımadan önce koşar: `python tmp/m500_links.py before`. Liste taban olarak saklanır.
- [ ] `docs/` dışından `docs/`'a giden yollar taranır (`queen-editor/`, `queen-agent/`,
  `collab-toolbox/`, `CLAUDE.md`, `.claude/`); bir kodun ya da testin `docs/`'u okumadığı görülür.

### Görev 2: Notlar

- [ ] On not `git show 4403108a^:docs/<ad>` ile `docs/arsiv/notlar/<ad>`'a yazılır.
- [ ] `4403108a`'nın değiştirdiği 20 belgedeki farkı tersine uygulanır (`git apply -R`): 31 link geri
  gelir, henüz eski yere (`../<not>.md`) gösterir.

### Görev 3: Taşıma ve linkler

- [ ] `tmp/m500_move.py`: kalanı ve gideni spec'teki kurala göre ayırır; önce her `.md`'nin linklerini
  eski yerinden çözüp yeni yere göre yazar (notlarınkini `docs/` kökünden), sonra `git mv`.
- [ ] Önce kuru koşu, sayılar spec'teki sayılarla karşılaştırılır; sonra `--apply`.
- [ ] `tmp/m500_keep_dead.py`: taşınan belgelerde önceden kırık olan linkler, yeni klasörden yine aynı
  eksik yolu adlandıracak biçimde yazılır.
- [ ] Boş kalan `docs/design-needs/` ve `docs/research/2026-08-14-mira-ara/` silinir.

### Görev 4: Denetim

- [ ] `python tmp/m500_links.py after`: listede tabandakilerden başka satır yok.
- [ ] `git status`'ta taşınanlar `R` olarak görünüyor.
- [ ] Dört takım teker teker: `python -m pytest queen-agent -q`, `npm test --prefix queen-agent/frontend`,
  `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
- [ ] `tmp/m500_*` silinir.
