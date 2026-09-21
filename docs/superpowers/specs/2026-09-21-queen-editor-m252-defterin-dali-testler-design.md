# Madde 252 · Defter koşulan dalı klonlayacak — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Bugün ne oluyor

Defterin CONFIG hücresi `BRANCH       = "feat/queen-editor-v5"` diyor, ve
`test_notebook_clones_its_branch.py`'nin `BRANCH` sabiti aynı adı taşıyor. İkisi aynı olduğu için
takım yeşil — **testin tuttuğu şey ikisinin aynı olması**, doğru dal olması değil.

O dosyanın kendi kuralı: bir deneme iki satırı birlikte değiştirir, ve **merge'den önce ikisi de
`main`'e döner**. v5'in denemesi girdi, dönüş olmadı, ve `497b0a3e` v5'i main'e böyle aldı.

Sonucu bu koşunun kendisini vuruyor: Colab depoyu klonluyor *(FOUNDATION 1)*, yani defter bugün
açılsa v5'in ağacını indirir — 249, 250 ve 251'in hiçbiri o ağaçta yok.

## Seçilen yol

**Testin sabiti bu koşunun dalı olur, defter de onu söyler.** İki satır, ve zaten duran iki test
ikisinin ayrıldığı anda düşer — bu maddenin çivileyeceği yeni bir olgu yok, **değiştireceği bir
beklenti var**.

Bu, test turunu maddeye özel bir biçime sokuyor: kırmızıyı yazan şey yeni bir test değil,
**sabitin yeni değeri**. Sabit v6'ya döndüğü an defter hâlâ v5 dediği için
`test_the_notebook_clones_the_branch_this_tool_is_served_from` düşüyor — istenen kırmızı o.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Defter `feat/queen-editor-v6`'yı klonluyor | **kırmızı** *(sabit v6'ya döndükten sonra)* |
| 2 | Defterde başka hiçbir dal adı kalmamış | **kırmızı**, aynı sebeple |

2'nin de kırmızı olması sabitin değişmesinin doğal sonucu: defterdeki `feat/queen-editor-v5`, sabit
v6'yı söylediği anda *"başka bir dal adı"* oluyor. İkisi de defterin tek satırıyla yeşile dönüyor,
ve ikisinin birden düşmesi kuralın işlediğini gösteriyor — dal adı defterde tek yerde durmalı.

## Bu turda değişen

- `backend/tests/test_notebook_clones_its_branch.py`: `BRANCH` sabiti `feat/queen-editor-v6`, ve
  merge borcunu söyleyen yorum bu koşunun adıyla duruyor.

Defter bu turda değişmiyor — o, uygulama turunun işi.
