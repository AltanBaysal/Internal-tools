# Madde 117 — *Sen karar ver* yalnız sorulduğu adımı kapatır · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 117.
**Gözlenen** *(28 Ağustos, dördüncü deneme)*: mekân sorusu *"yatak odası, açık renkler, sen karar
ver"* ile cevaplandı ve akış bunu akışın tamamının yetkisi olarak okudu — mekân adımı onaysız
kapandı, sahne adımının *"kaç sahne, hangi anlar"* sorusu hiç sorulmadı, ve plana karar adsız
yazıldı *("user said sen karar ver")*, yani planı okuyan taze bir sohbet de aynı geniş yetkiyi
miras aldı.

## Nereye yazılır

**Akış metnine** *(`skills.py` · `START_A_SCENARIO`)* — taban yönergeye değil. Adım, soru ve onay
makinesi akışın kendi makinesi; skill'siz bir sohbette *"sen karar ver"* gerçekten işin tamamını
devreder ve taban yönergenin *"Ask rather than invent"* cümlesi bunu doğru karşılıyor. Yeri döngü
paragrafı: cevabın üç geliş yolunu sayan cümlelerin hemen ardı, çünkü eksik olan dördüncü yol.

## Kural

Üç cümle:

1. Kararın bırakılması bir cevaptır ve **yalnız sorulduğu adımı** kapatır; sonraki adımın sorusu
   yine sorulur.
2. Kararı bırakılan adım yine seçileni gösterip **onayla** biter — akışın seçmesi kullanıcının
   onaylaması değildir.
3. Plan kararı **hangi adımı kapattıysa o adla** yazar, genel yetki olarak asla — taze sohbet planı
   okur ve tam olarak yazılanı miras alır.

## Test — `test_skills.py`, akış bölümüne üç yeni

Sabitlenen parçalar *(tur 2'nin yazacağı cümlelerden)*:

| Test | Aradığı |
|---|---|
| devir tek soruyu kapatır | `answers only the question that was asked` ve `asked as ever` |
| devredilen adım onayla biter | `still ends when the user approves` |
| plan genel yetki yazmaz | `never as a standing authority` |

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_skills.py` | 3 |

## Bilerek yapılmayanlar

- **`skills.py` açılmaz** — tur 2'nin işi.
- **`prompt.py` ellenmez** — skill'siz sohbetin davranışı doğru.
- **prompt+ metni ellenmez** — kendi başına koşmak onun tasarımı.
- **`dist` derlenmez** — ön yüz bu maddede yok.
