# Madde 53 — FOUNDATION'ın iki kararı · Tasarım

**Madde:** [v4 yol haritası Madde 53](../plans/2026-08-20-queenagent-v4-colab-roadmap.md)
**Bu belgenin konusu:** hangi iki karar yanlış hâle geldi, yerlerine ne yazılacak, ve hangi cümle
hangi kipte kurulacak.

---

## Neden 54'ten sonra

Yol haritası 53 → 54 diyordu; ters çevrildi. Sebep: bu madde FOUNDATION'a "`dist` commit'lenir"
yazıyor. `dist` gerçekten commit'lenmeden bunu yazmak, belgenin bir commit boyunca yalan söylemesi
olurdu. Madde 54 gerçeği kurdu, bu madde yazıyor.

## Karar 1 — nerede çalıştığı

Bugün diyor ki: uygulama yalnız kullanıcının makinesinde çalışır; Colab'ın tek faydası (GPU) burada
geçersiz, bütün maliyetleri ise geçerli; **"paylaşmak, henüz vermediğimiz bir karar gerektirir."**

Bu son cümle artık yanlış — karar verildi. Ama kararın **gerekçesi** korunmalı, çünkü hâlâ doğru:
GPU faydası gerçekten yok. Değişen şey, paylaşma ihtiyacının ortaya çıkması ve alternatifin (elden
gönderilen bir exe) daha pahalı olması.

Yeni metin üç şeyi söyler:
- **Yerel birincil yoldur ve öyle kalır** — Colab ekleniyor, yerini almıyor.
- Kararı değiştiren şey paylaşmaktı; alternatif exe'ydi ve her değişiklikte elden gönderme
  maliyetini taşıyordu.
- Uygulama zaten defterin istediği şekle sahipti: kök `QUEENAGENT_ROOT` ile taşınıyor, anahtar onun
  altında yaşıyor, tek üçüncü parti bağımlılık Flask.

## Karar 3 — `dist`

Bugün diyor ki: geliştirici ile çalışma ortamı aynı makine olduğu için önceden derlenmiş bir çıktı
depoda hiçbir işe yaramaz ve bayatlar.

Öncülü çöktü: artık aynı makine değiller. Yeni metin, kuralı **ve** onu tutan şeyi adlandırır —
bir frontend değişikliği, `dist` kaynağıyla **aynı commit'te** yeniden derlenip eklenmeden bitmiş
sayılmaz, ve bunu `test_dist_is_committed.py` reddeder.

## Kip meselesi

Karar 1'in sonucu, tünel adresinin herkese açık olması ve bunun bir parola gerektirmesi. **Parola
henüz yok** — Madde 60. O yüzden cümle betimleme değil **kural** kipinde kurulur: "parolasız
sunulamaz". CLAUDE.md'nin kendi tanımı bunu zaten meşru kılıyor: bir belge, *henüz yazılmamış kodu
bağlayan bir kural* koyabilir; olmuş gibi anlatamaz.

Aynı yerde kernel proxy'nin neden elenmiş olduğu tek cümleyle kalır — yoksa altı ay sonra biri
"neden özel bir adres kullanmadık" diye sorar ve cevabı hiçbir yerde bulamaz.

## Diğer iki belge

- **CLAUDE.md** komut bloğu: bugün "queen-agent'ın dist'i commit'lenmez, önce derle" diyor ve
  queen-editor'ü istisna olarak anlatıyor. Artık ikisi de aynı kuralda; blok buna göre yeniden
  düzenlenir. QueenAgent'ın yerel koşusunun **birincil** olduğu korunur.
- **queen-agent/README.md**: derleme adımının artık yalnız kaynak değişince gerektiği, ve bundle'ın
  neden commit'lendiği. Defterin adı **anılmaz** — `app.ipynb` henüz yok, ve olmayan bir dosyayı
  adlandırmak bu maddenin kaçındığı yalanın aynısı. Onu Madde 58 yazar.

## Test turu neden yok

Değişen üç şey de düzyazı. Bir metnin belli bir cümleyi taşıdığını tutan test, davranışı değil
kelimeyi tutar: her yeniden yazımda kırmızıya döner ve düzeltilmesi testin kendisini anlamsızlaştırır.
Bu maddenin tuttuğu kuralın mekanik karşılığı zaten Madde 54'ün iki testinde duruyor.
