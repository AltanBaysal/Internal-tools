# Madde 225 · Beklerken ekran susmayacak — test turunun planı

**Spec:** [test turu](../specs/2026-09-16-queen-editor-m225-bekleme-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar. Testler henüz olmayan şuna göre yazılıyor: `ProjectsScreen` bir
**meşgul** durumu tutuyor *(hangi proje, hangi kelime)*, `ProjectCard` o kelimeyi tarihin yerinde
gösteriyor ve üç düğmesini de kapatıyor.

## Adımlar

**1 · Bir yardımcı: elde tutulan söz.** Sahte `archiveProject` hemen çözülürse *"sürerken"* diye bir
an olmaz. Küçük bir `deferred()` testin istediği anda çözüyor.

**2 · `ProjectsScreen.test.jsx` — olgu 1–6.**

| Test | Ne bekler |
|---|---|
| `says what it is doing while the archive is in flight` | kartta `Arşivleniyor…` |
| `does not send a second request while the first is in flight` | ikinci tık → `archiveProject` yine 1 kez |
| `closes the card's other buttons too while it works` | sil ve ad değiştir `disabled` |
| `takes the word away once the list has been read again` | iş bitince kelime yok |
| `says what it is doing while a restore is in flight` | kartta `Geri alınıyor…` |
| `takes the word away when it fails, and leaves the sentence` | kelime yok, sunucunun cümlesi var |

Dördüncüsünün *"liste yeniden okunduktan sonra"* demesi tesadüf değil: kelime cevabın gelişinde
kalkarsa, arada kalan okuma boyunca ekran yine susar.

**3 · Takım koşulur**, dördü de:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: yalnız **queen-editor'ün ön yüzü kırmızı**, öteki üçü yeşil.

**4 · Kırmızı commit'lenir.**

## Değişen dosyalar

`queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx`.
