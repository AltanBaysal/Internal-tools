# Madde 115 — Action yalnız kadrajda görüneni taşır · Tur 1 (testler) tasarımı

**Kaynak madde:** [v5 yol haritası, Blok 8, Madde 115](../plans/2026-08-25-queenagent-v5-roadmap.md)

## Neyi tarif ediyoruz

114 biçimi düzeltti; bu madde içeriği. Üçüncü denemenin iki değeri:

- `facing each other after argument, reconciling`
- `one cutting vegetables, other making coffee`

İlkinde *"after argument"* bir neden — kadrajda görünmez, çünkü tartışma resimde yok. İkincisi
Türkçe sahne cümlesinin yeniden anlatımı: *"birlikte atıştırmalık hazırlıyorlar"* cümlesi
kimin-ne-yaptığı anlatısı olarak geri geliyor.

Sahne listesi hikâyeyi taşır — kullanıcının okuduğu şey o, ve öyle kalmalı. Kare yalnız kadrajı
taşır. Bu ayrımı bugün hiçbir metin söylemiyor: şema *"An action carries the pose, the expression
and where the eyes look"* diyor, yani **ne taşıdığını** söylüyor, **ne taşımadığını** değil.

## Nereye yazılıyor: şema

Skill metni değil şema, çünkü soru *"bu skill ne yapar"* değil *"bu dosyanın değeri neye benzer"*
— modülün kendi ayrımı bu *(`skills.py` docstring'i)*. Ayrıca şemayı iki skill de çekiyor, yani
kareyi kim yazarsa yazsın kural bağlamda oluyor. prompt+'ın *"the sentence is a brief, never text
to copy"* cümlesi mekanizmayı zaten tutuyor; eksik olan kuralın kendisi.

## Üç pin

**1 · Yasak söyleniyor.** Yeni paragraf *"only what the camera sees"* diyor ve nedenin ait olduğu
yeri adlandırıyor *("what came before")*. Zayıf modelde *"ne taşır"* listesi tek başına yetmiyor;
yasak açıkça yazılmadıkça hikâye sızıyor.

**2 · Çevirinin nasıl yapıldığı söyleniyor.** Yalnız yasak, modeli sahneyi boşaltmaya iter. Neden
görünür karşılığıyla yazılır: `turned away, downcast eyes, tense shoulders`. Pin `downcast eyes`'a
basıyor — yalnız doğru biçim gösteriliyor, 114'teki gerekçeyle.

**3 · Kural defterinde 9. kural.** Defter yazmadan önce tutulan liste; hikâye sözü orada da
avlanabilir olmalı. Pin `9.` ve `cause`.

## Bilerek pinlenmeyen

- **Sahne listesi.** Hikâye onun işi; ayıklama kareyi yazarken olur, listeyi kısaltarak değil.
- **prompt+ metni.** Bir kopya sapar *(96'nın gerekçesi)*; kural tek yerde durur.
- **Kod.** `build_prompts` ne yazıldıysa onu basıyor.

## Görülür hâli

Üç kırmızı. 114'ün süpürme pini yeni paragrafı taramıyor — o yalnız JSON bloğunun değerlerine
bakıyor, düzyazıya değil. Ön yüz değişmiyor, `dist` derlenmiyor.
