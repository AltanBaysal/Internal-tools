# Madde 180 · uygulama turu — araya kare

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m180-araya-kare-testler-design.md).
Commit `62fe9f2` 11 kırmızı bıraktı.

---

## Dört değişiklik

**`_renumbered(frames)` — yeni, ve ortak.** Bugün numaralama döngüsü `_remove_frame`'in içinde
duruyor. Ekleme de aynı işi yapıyor, ve *bir kural iki yerde yazılırsa kendisiyle çelişecek olan bir
kuraldır*. Döngü kendi adını alıyor, ikisi de onu çağırıyor. 173 öncesi numarasız kareleri onarması
da bu fonksiyonun içinde kalıyor — yerinden okumak yerine saymak, tam da onu onaran şey.

**`_numbered`'a bir tavan.** `before` **son kareden bir fazlasını** adlandırabilir — sona eklemek
demektir bu. Ama cümle *"scene.json has 3 frames"* demeli, çünkü dosyada üç kare var; yer sayısı
dört olsa da. Dolayısıyla sınır ile cümledeki sayı ayrılıyor: `_numbered(wanted, source, many,
ceiling=None)`, `many` cümlenin, `ceiling` sınırın. `ceiling` verilmezse ikisi aynı — 174'ün iki
çağrısı olduğu gibi kalıyor.

**`_add_scene`'in yerleşimi.** `before` yoksa yer `len(frames) + 1`, yani bugünkü davranış. Varsa
`_numbered` onu geçiriyor, doğan kareler oradan başlayarak numaralanıyor *(`_frame_from`'a giden sayı
`place + offset`, ki reddedilen bir sahne **gireceği** numarayla anılsın)*, dilim ataması listeye
oradan giriyor, ve `_renumbered` hepsini yeniden sayıyor.

**Kayma cümlesi.** `moved = len(frames) - (place - 1)`, **eklemeden önce** hesaplanıyor. Sıfırsa
cümle kurulmuyor: kaymayan kareyi anlatan bir cümle, 174'ün *"no frames left"* kararının ihlali
olurdu.

## Araç açıklaması

Açılış cümlesi *"Add scenes to the end of a structure file"* artık yanlış — sona da gidiyor, araya
da. Ve *"Where a frame goes is not yours to give"* yerini daha dar bir doğruya bırakıyor: **yer
verilebilir, numara verilemez.** `before` bir kare numarası, listede bir sıra değil; numara hâlâ
karenin yerinin kendisi.

`before`'un metni ne yaptığını değil **neden var olduğunu** söylüyor: kayan kareler taşıdıkları her
şeyi, `action`'lar dahil, koruyor — kuyruğu söküp yeniden eklemenin yapmadığı şey. Modelin Deneme
4'te seçtiği yolu bir daha seçmemesi bu cümleye bağlı.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **824 yeşil.** 11 kırmızının hepsi dönmeli, ve 174'ün silme testleri — ortaklaşan döngünün öteki
   kullanıcısı — kımıldamamalı.
3. Öteki üç takım rakamlarını korumalı: **589 · 739 · 591.** `dist` derlenmiyor.
