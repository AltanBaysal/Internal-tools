# Madde 284 · `pieces.txt` parçaların yanında duracak — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey. Madde kullanıcının sorusundan doğdu *(21 Eylül — "pieces txt ne")*.

## Bugün ne var, ve 282'den sonra ne kaldı

`merge()` `concat`'in okuma listesini **hedefin yanına** yazıyor:
`folder = os.path.dirname(target)`. Kullanıcı sorduğunda bunun somut sonucu vardı — hedef Drive'ın
export klasörüydü, yani liste export süresince kullanıcının klasöründe duruyordu ve süreç ortada
ölürse orada kalıyordu.

**282 o sonucu ortadan kaldırdı** ama **kuralı değiştirmedi:** hedef artık `/tmp`'de olduğu için
liste de orada doğuyor. Yani bugün belirti yok, ve kalan şey **yanlış kural**: liste hedefi takip
ediyor. Hedef bir gün yine Drive'da olursa liste de oraya döner, ve o dönüşü hiçbir test
durdurmaz.

**Bu yüzden madde düşmüyor, daralıyor:** kural, listeyi ait olduğu şeye bağlıyor —
**parçalara**. Liste onların okuma sırası; hedefle hiçbir ilgisi yok.

## Çivilenen olgular

**1 · Liste parçaların yanında doğuyor.** Parçalar bir klasörde, hedef başka bir klasörde olsa
bile liste **parçaların** klasöründe.

**2 · Hedefin klasörüne hiçbir şey yazılmıyor** — ne liste, ne kalıntı.

**3 · Liste yine silinip gidiyor**, ve okuma sırası aynı: iskele, export'un parçası değil.

## Beklenen kırmızı

Bir test: bugün liste hedefin yanına yazılıyor. **Bir**, ve sayı takımdan okunacak.
