# Madde 15 — Mesaj etiketleri ve bekleme bloğu · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 15](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 3, 46, 47 · sapma 80 · **karar 10** · `HANDOFF.md` §3
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 0 · Yol haritasının kaynak etiketi yanlış

Yol haritası bu maddeyi "karar 9" diye anıyor; karar 9 **projenin rengi** ile ilgili ve Madde 8'de
uygulandı. Buradaki karar **karar 10 — "Kullanıcı adı etiketi kalkıyor"**. Bu maddede doğru numara
kullanılıyor. (Aynı kayma Madde 5, 6, 10 ve 11'de de çıkmıştı.)

---

## 1 · Kullanıcının etiketi yalnız saat (fark 3, karar 10)

Bugün "You · 11:04" yazıyor. Tasarım kişinin **kendi adını** çiziyor ("ALEX · 14:32") ama adın
nereden geleceğini hiçbir yerde söylemiyor; uygulamada kullanıcı adı diye bir ayar da yok. Karar 10
bunu çözdü: **ad tümüyle kalkıyor, yerinde yalnız saat kalıyor.** Kimin yazdığı zaten balonun sağa
yaslı olmasından belli.

Cevap tarafı değişmiyor: "QueenAgent · saat" — büyük harfe çeviren `.msg__label`'ın kendisi.

---

## 2 · Bekleme etiketi saatlidir (fark 47, sapma 80)

Bugün üç noktanın üstünde yalnız ürün adı var; saat ancak akış bitip cevap kaydedildikten sonra
beliriyor. Tasarım etiketi beklemenin **başından** itibaren saatli istiyor.

**Saati ön yüz vuruyor** ve bu FOUNDATION karar 4'ü çiğnemiyor: henüz sunucuda bir kayıt yok, ortada
kaydedilecek bir olgu da yok — ekranda "bu bekleme ne zaman başladı" diye bir sunum bilgisi var.
Cevap kaydedildiğinde etiketin saati sunucunun `at` alanından gelmeye başlar; ön yüzün damgası o anda
düşer.

Bekleme başladığında bir kez damgalanır, akış boyunca aynı kalır — akan her parçada saatin ilerlemesi
"cevap ne zaman istendi" sorusunun cevabını bozardı.

**Üç nokta ile etiket arası 10px.** Mesaj bloğunun kendi boşluğu 6px; bekleme bloğu kendi
boşluğunu yazıyor.

---

## 3 · "creating file…" bekleme bloğunun içine giriyor (fark 46)

Bugün kesik çerçeveli kutu akan cevabın ve o ana kadar doğmuş kartların **altında**, kendi başına
duruyor; içinde yalnız mono yazı var ve kutu yazı kadar geniş.

Tasarım onu üç noktanın hemen altına, **aynı bekleme bloğunun içine** koyuyor: solunda 30×30, 7px
yarıçaplı **boş** bir rozet yeri, en çok 340px genişlik — yani doğacak dosya kartının iskeleti.

**Bir durumu tasarım düşünmemiş: metin akarken doğan dosya.** Tasarımın kendi akışında dosya
akışın *sonunda* doğuyor, bizimkinde `create_file` bir araç çağrısı ve modelin önce metin yazması
mümkün. O anda üç nokta çoktan kaybolmuş oluyor.

**Karar:** kutu "üç noktanın altında" değil, **bekleyen bloğun altında** durur. Bekleme sırasında bu
üç noktanın altıdır — tasarımın istediği yer. Akış sırasında akan metnin altıdır. Kutunun iki ayrı
evi olmuyor; tek kuralı var ve o kural tasarımın cümlesini kapsıyor.

---

## 4 · Katman denetimi

Tek dosya çifti: `ChatScreen.jsx` ve `workspace.css`. Yeni bileşen yok — kutu bekleme bloğunun
parçası olduğu için dışarı çıkarmak onu yine iki yere bölerdi.

---

## 5 · Kabul ölçütü

1. Kullanıcı balonunun etiketi yalnız saattir; "You" hiçbir yerde geçmez.
2. Bekleme etiketi "QueenAgent · saat" okur ve saat beklemenin başındandır.
3. Akış boyunca o saat değişmez.
4. Etiket ile noktalar arası 10px.
5. "creating file…" bekleyen bloğun içindedir, solunda 30×30 boş rozet yeri vardır ve kutu en çok
   340px genişler.

## 6 · Risk

Bekleme uzarsa etiket cevap kaydedildiği anda bir dakika **ileri** atlayabilir: bekleyen etiket
sorunun sorulduğu anı, kaydedilen mesaj cevabın yazıldığı anı gösteriyor. Kabul edilebilir — ikisi
gerçekten iki ayrı an, ve tasarım hangisini istediğini yalnız bekleme için söylüyor.
