# Madde 180 · test turu — araya kare

**Kaynağı:** [yol haritası, Madde 180](../plans/2026-09-05-queenagent-v7-roadmap.md).
Koşunun ilk maddesi, ve `feat/queenagent-v7.5`'in ilk kodu.

---

## Ne kanıtlanacak

Kullanıcı 2. ile 3. karenin arasına bir sahne istedi. `add_scene` yalnız sona eklediği için model
**21 `remove_frame`** çağırıp kuyruğu yeniden kurdu — ve geri eklenen kareler `add_scene`'ten
geçtiği için **action'sız** döndü. Bir saat önce yazdırılmış 21 Grok cümlesi çöpe gitti.

Kanıtlanacak tek şey bu: **araya girmek hiçbir kareyi silmez, dolayısıyla hiçbir `action` kaybolmaz.**

## On üç test

Hepsi `test_tools.py`'ye, **174'ün bölümünden sonra** — `WITH_ACTION` ve `_frames` orada tanımlı, ve
bu maddenin fikstürü tam olarak *action taşıyan kareler*. 173'ün bölümünde dursaydı fikstürü kendi
kurmak zorunda kalırdı, ve o kopya ilk değişiklikte ötekinden ayrılırdı.

| # | Test | Ne söylüyor |
|---|---|---|
| 1 | `before` o karenin önüne koyar | 3 karelik dosya, `before=2` → yeni sahne 2. sırada, eski 2 ve 3 kayar |
| 2 | **Kayan karelerin `action`'ı durur** | maddenin kendisi |
| 3 | Numaralar baştan sona 1..N | kayanlar da dahil |
| 4 | `before` verilmezse bugünkü davranış | sona ekler, hiçbir şey kaymaz |
| 5 | Cevap yaptığı kareleri adlandırır | `as frames 2-3` |
| 6 | Cevap kayanları söyler | *"; 2 frames after it moved up."* |
| 7 | Sona ekleyen `before` kayma cümlesi kurmaz | kaymış bir şey yok |
| 8 | `before` = uzunluk + 1 sona ekler | söylediği şey o |
| 9 | Olmayan kareden önce reddedilir | 174'ün cümlesi, ama tavan **uzunluk + 1** |
| 10 | Sayı olmayan `before` reddedilir | 174'ün öteki cümlesi |
| 11 | Kötü bir sahne varsa hiçbir şey yazılmaz | ve sorun cümlesi **gireceği** numarayı anar |
| 12 | Haritalara dokunulmaz | |
| 13 | Numarasız eski dosya numara kazanır | 174'ün silme tarafındaki testinin eşi |

Artı bir tane: **araç açıklaması `before`'u söylüyor mu.** Bir modelin görmediği parametre, bir
modelin uzanmadığı parametredir — 108 ve 118 bunu iki kez gösterdi.

## Cevabın şekli

```
Added 1 scene to scene.json as frame 2; 2 frames after it moved up.
```

Kayma cümlesi `remove_frame`'in *"2 frames left, renumbered from 1"*'inin karşılığı, ve aynı sebeple
var: **modelin elindeki numara bu çağrıdan sonra başka bir kareyi gösteriyor olabilir.** Sona
eklerken kurulmaz, çünkü kayan bir şey yok — olmayan işi anlatan cümle, 174'ün *"no frames left"*
kararının aynısı.

*"renumbered from 1"* denmiyor: silmede gerçekten hepsi kayar, burada yalnız **sonrakiler**. Yapılan
işi söylemeyen bir cümle, yanlış bir cümledir.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent` **14 kırmızı** vermeli; öteki üç takım
rakamlarını korumalı. Kırmızıların hepsi *"unexpected keyword"* ya da yanlış yerleşim olmalı —
`before`'u hiç bilmeyen bir `add_scene`'in verebileceği tek şey.

## Kırmızı turun tuzağı

Bu koşuda dört kez çıktı, sonuncusu Madde 176'da: **hiçbir şey olmadığı için geçen test.**
*"Araya eklemek haritalara dokunmaz"* diyen test, ekleme hiç olmazsa da geçer. Onun için 12. test
önce **eklemenin olduğunu** ölçer, sonra haritaların durduğunu.
