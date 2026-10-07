# Madde 224 · Arşiv ekranı kendi düğmelerini taşıyacak — test turunun planı

**Spec:** [test turu](../specs/2026-09-16-queen-editor-m224-arsiv-ekrani-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar. Testler henüz olmayan şuna göre yazılıyor: arşiv görünümünün
başlığında tek bir ghost düğme, **Arşivden çık**, ve **Yeni proje**'nin orada hiç çizilmemesi.

## Adımlar

**1 · `ProjectsScreen.test.jsx` — olgu 1, 2, 5.** Var olan *"opens the archive from the header"*
testinin açtığı yolun devamı: `Arşiv`'e basılır, sonra başlığa bakılır.

| Test | Ne bekler |
|---|---|
| `has no way to make a project from inside the archive` | `queryByText("Yeni proje")` → null |
| `offers nothing to press in an empty archive either` | boş arşivde de ne o düğme ne *"İlk projeyi oluştur"* |
| `is left the way every other place in this app is left` | `getByText("Arşivden çık")` var |
| `comes back to the projects when the way out is pressed` | basınca `düğün` geri geliyor, `eski iş` gidiyor |

**2 · Olgu 4 zaten yeşil** ve öyle kalmalı: *"opens the archive from the header"* onu tutuyor.
**Olgu 3 tutulmuyormuş** — arşive giren test var, arşivden **çıkan** yok; yukarıdaki dördüncü test o
boşluğu da dolduruyor.

**3 · Takım koşulur**, dördü de:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: yalnız **queen-editor'ün ön yüzü kırmızı**, öteki üçü yeşil — arka uç bu maddede hiç
değişmiyor.

**4 · Kırmızı commit'lenir.**

## Değişen dosyalar

`queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx`.
