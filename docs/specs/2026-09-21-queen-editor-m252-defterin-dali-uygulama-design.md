# Madde 252 · Defter koşulan dalı klonlayacak — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m252-defterin-dali-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

Defterin CONFIG hücresinde tek satır: `BRANCH       = "feat/queen-editor-v6"`. Hizalama olduğu gibi
kalıyor — testin aradığı dize boşluklarıyla birlikte.

Başka hiçbir şey değişmiyor. Klon hücresi `BRANCH`'i zaten okuyor, ve 251 onun grafik yolunu
düzeltti.

## Merge'den önce ödenecek borç

`main`'e dönmeden önce **iki satır birden `main` olur**: defterin CONFIG hücresi ve
`test_notebook_clones_its_branch.py`'nin `BRANCH` sabiti. v5 tam bunu yapmadı — bu madde onun
bıraktığı işi kapatıyor, ve aynı borcu bu koşu için yazıya geçiriyor.

O yüzden **v6 birleşmeye hazır demek, bu iki satırın `main`'e dönmüş olması demektir**; ikisi bir
arada değişir, tek başına hiçbiri.

## Bu turda değişen

- `queeneditor.ipynb`: CONFIG hücresinin `BRANCH` satırı.
