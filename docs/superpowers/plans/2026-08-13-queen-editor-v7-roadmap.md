# Queen Editor — Yol Haritası v7

**Tarih:** 2026-08-13 · **Koşu dalı:** `feat/queen-editor-v3` · **Durum:** yazıldı, koşu başlamadı.
**Yerini aldığı doküman:** yok — [v6](2026-08-13-queen-editor-v6-roadmap.md) kapandıktan sonra
açılan yeni koşu.
**Kaynak:** [queen-editor/EKSIKLER.md](../../../queen-editor/EKSIKLER.md) — kullanıcının elle UI
turunda bulduğu 10 madde ve koşu sırasında çıkan 2 madde.

## Neden bu koşu var

v6 bitti, uygulama Colab'da ilk kez elden geçirildi ve **üretim hiç çalışmadı**. Turdan çıkan
liste üç kümede toplanıyor: çalışmayan üretim, defterin üstlendiği kurulum işi, ve kullanıcıyı
bekleten/yanıltan arayüz. Bu koşu o listeyi kapatır.

## Kapsam sınırı

- **Yeni yetenek yok.** Bu koşu yalnız bulunan eksikleri kapatır; hiçbir görev yeni bir ekran,
  yeni bir üretim türü veya yeni bir dosya türü getirmez.
- **Motorlar değişmiyor.** Foto ve video ComfyUI'de, ses süreç içinde kalır
  ([FOUNDATION madde 6](../../../queen-editor/FOUNDATION.md)).
- **Ön yüz aptal kalır.** Hiçbir görevin **kuralı** tarayıcıya yazılmaz: süre bilgisi de, "kurulu
  mu" cevabı da, bir işin ne kadar sürdüğü de sunucunundur — tarayıcı yalnız çizer
  ([FOUNDATION madde 4](../../../queen-editor/FOUNDATION.md)). Bir görev ön yüzde çözülebiliyor
  gibi duruyorsa, önce sunucuda karşılığı var mı diye bakılır. Ayrım şurada: elindekini ekranda
  tutmak çizim işidir ve ön yüzde kalır; o şeyin **ne kadar sürede geldiği** sunucunun işidir.
- **Katman kuralları aynen geçerli.** `presentation → domain ← data → services`, `feature ↛
  feature`, somut bağlama yalnız `backend/main.py`
  ([CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)).

## Bozulan yazılı karar

Blok 2 bugün yazılı olan bir kararı iptal ediyor: **CODE-STANDARD'ın bağımsızlık tablosu**, model
indirme/doğrulama makinesinin `app.ipynb`'e birebir kopyalandığını söylüyor, ve `model_groups`
foto üreticisinin "defterin kurduğu" üretici olduğunu yazıyor. Bundan sonra **defter hiçbir model
indirmez**; kurulum uygulamanın kurulum ekranının işidir, defterin işi kod ve kütüphane kurmaktır.
Bu iki belgenin (FOUNDATION + CODE-STANDARD) güncellenmesi **Görev 4'ün işidir** — gerekçesiyle
birlikte, çünkü "modeller neden defterden inmiyor" sorusunu ilk soran kişi oraya bakacak.

## Nasıl çalışacağız

v5 ve v6'daki dört adımın aynısı; görev bitmeden sonrakine geçilmez:

1. **Spec** — `docs/superpowers/specs/`, görevin kararları burada verilir.
2. **Plan** — `docs/superpowers/plans/`, TDD adımlarıyla.
3. **Full TDD** — hiçbir üretim kodu satırı, önce kırmızı bir test yokken yazılmaz.
4. **Commit** — görev başına bir commit; ön yüz değiştiyse `dist/` aynı commit'te.

Komutlar her seferinde birebir aynı: `python -m pytest queen-editor -q`,
`npm test --prefix queen-editor/frontend -- --run`, `npm run build --prefix queen-editor/frontend`.

## Bağımlılık haritası

- **Blok 1 herkesin önkoşulu:** üretim çalışmadan hiçbir madde elle doğrulanamaz.
- **Blok 2 kendi içinde zincir:** 2 → 3 → 4 → 5.
- **Blok 3'te 7, 6'ya bağlı.** 8 en sona bırakıldı: 6 ve 7 bittikten sonra geriye kalan gerçek
  maliyet ölçülebilir olur.
- **Blok 4 serbest:** dört görev birbirinden bağımsız, sıra tercih meselesi.

---

## Blok 1 · Uygulama çalışsın

### Görev 1 · Üretim sözleşmesi tek olsun

**Bulgu:** Fotoğraf üretimi hiç çalışmıyor — aynı kare üç kez denenip üretim duruyor. Ses üreticisi
de kuyruğun beklediğinden başka bir şey döndürüyor; ilk ses işinde düşer.

**Ne olacak:** Üç üretici de (foto, video, ses) kuyruğun beklediği tek sözleşmeyi karşılar, ve o
sözleşme yazılı olduğu yerde de doğru yazar. Kuyruğu üç üreticiyle birlikte baştan sona koşan bir
test gelir — bugün böyle bir test olmadığı için takım yeşilken uygulama çalışmıyordu.

**Bağımlılık:** Yok. Diğer on bir görevin önkoşulu.

**Bitti sayılır:** Foto, video ve ses işleri kuyrukta uçtan uca geçiyor; sözleşmeyi bozan bir
üretici eklendiğinde test kırmızı veriyor.

---

## Blok 2 · Kurulum uygulamanın işi

### Görev 2 · Civitai anahtarı uygulamaya geçsin

**Bulgu:** Uygulama anahtar isteyen bir kaynaktan indiremiyor. Civitai'de duran modeller bu yüzden
"uygulamadan inmez" diye işaretli ve defterin işi.

**Kullanıcı kararı (2026-08-13):** Anahtar Colab Secret'ta durur, defter onu uygulamaya geçirir,
indirmeyi uygulama yapar. Kullanıcıdan fazladan bir adım istenmez; anahtar hiçbir yere yazılmaz ve
hiçbir yerde basılmaz.

**Ne olacak:** Kurulum ekranı Civitai'deki video modellerini kendi indirir.

**Bağımlılık:** Görev 1 — kurulumun doğru olduğu ancak çalışan bir üretimle görülebilir.

**Bitti sayılır:** Video üreticisi "kurulu değil" durumundan tek tıkla kuruluyor, defter hiçbir
video modeline dokunmuyor.

### Görev 3 · Foto modelleri kurulum listesine girsin

**Bulgu:** Foto üreticisinin kurulum listesi boş. Uygulama "foto kurulu mu" sorusuna cevap veremiyor
ve kuramıyor.

**Ne olacak:** Foto modelleri de diğer üreticiler gibi listede yerini alır ve kurulum ekranından
kurulur.

**Bağımlılık:** Görev 2 — bu modeller anahtar olmadan inmiyor.

**Bitti sayılır:** Kurulum ekranı üç üreticiyi de aynı dille gösteriyor; hiçbiri "bunu defter
kurar" demiyor.

### Görev 4 · Defter model indirmeyi bıraksın

**Bulgu:** Defter hâlâ foto modellerini ve ses modelini indiriyor.

**Ne olacak:** Defterin model indirme işi tamamen kalkar; defter yalnız kod ve kütüphane kurar,
uygulama modelleri kurulmamış halde açılır ve kullanıcı kurulum ekranından kurar. Bu görev
**FOUNDATION ve CODE-STANDARD'ı da günceller** — yukarıdaki *Bozulan yazılı karar*.

**Bağımlılık:** Görev 2 ve 3 — önce uygulama indirebilir olmalı, yoksa defterin de indirmediği bir
ara durum kalır.

**Bitti sayılır:** Temiz bir Colab turunda uygulama açılıyor, hiçbir model inmemiş oluyor, üçü de
ekrandan kuruluyor; iki belge de yeni durumu anlatıyor.

### Görev 5 · Kurulum ekranı doğruyu söylesin

**Bulgu:** Kur'a basınca anında geri bildirim yok, tepki gecikmeli geliyor — arada ne olduğu belli
değil. Kurulum kartındaki ilerleme çubuğu da gerçek indirmeyle uyuşmuyor.

**Ne olacak:** Tıklar tıklamaz durum görünür. Uydurma çubuk kalkar; yerine ne indiğini söyleyen
dürüst bir satır kalır.

**Bağımlılık:** Görev 2–4 — kurulumun nihai davranışına karşı bir kez yazılsın, iki kez değil.

**Bitti sayılır:** Kur'a basan kullanıcı bir daha basmak zorunda kalmıyor; ekranda gördüğü hiçbir
şey gerçekten sapmıyor.

---

## Blok 3 · Bekleme hissi

Üç görev büyük ihtimalle **tek bir kökü** paylaşıyor: galerinin listesini almak pahalı, ve o liste
her ekran değişiminde yeniden isteniyor. Görev 6'nın spec'i bunu ölçtüğünde kök gerçekten oradaysa
Görev 8 kendiliğinden küçülür — o zaman 8, kalan farkı kapatan görev olur, ayrı bir iş değil.

### Görev 6 · Ekran değişince galeri sıfırdan yüklenmesin

**Bulgu:** Detaya girip galeriye dönünce yükleme baştan başlıyor; detayda da bekleniyor.

**Ne olacak:** Ekranlar arasında gidip gelmek elde olanı çöpe atmaz — bu bir çizim kararıdır ve ön
yüzde kalır. Listenin **maliyeti** ise sunucunun işi ve bu görevin spec'inde ölçülür; ölçüm
Görev 8'in ne olduğunu da belirler.

**Bağımlılık:** Blok 1.

**Bitti sayılır:** Detay ↔ galeri geçişi beklemesiz.

### Görev 7 · Kuyruğa eklenen kare anında görünsün

**Bulgu:** "Eklendi" yazıyor ama kare bir dakika kadar ekrana düşmüyor; insan bir daha basıyor.

**Ne olacak:** Kuyruğa giren kare, girdiği anda listede olur.

**Bağımlılık:** Görev 6 — aynı liste yolunu kullanıyor, önce o yol düzelmeli.

**Bitti sayılır:** Ekle'ye basınca kare hemen görünüyor; ikinci basış refleksi kalmıyor.

### Görev 8 · Açılışta galeri hızlı dolsun

**Bulgu:** Uygulama açılışında fotoğraflar çok yavaş yükleniyor.

**Ne olacak:** İlk dolum kullanıcıyı bekletmez. Neyin pahalı olduğu 6 ve 7'den sonra ölçülür ve
maliyet nerede ise orada azaltılır — kararın yeri yine sunucu.

**Bağımlılık:** Görev 6 ve 7.

**Bitti sayılır:** Proje açılışı, dolu bir galeride bile bekleme hissi vermiyor.

---

## Blok 4 · Arayüz

Dördü birbirinden bağımsız; sıra serbest.

### Görev 9 · Yan barda açık ikona basınca panel kapansın

**Bulgu:** Açık panelin ikonuna tekrar basmak hiçbir şey yapmıyor.

**Ne olacak:** Aynı ikona basınca panel komple kapanır ve tuval genişler — kod editörlerindeki gibi.

**Bitti sayılır:** İkon aç/kapa gibi çalışıyor; kapalıyken tuval genişlemiş oluyor.

### Görev 10 · Kare hover'da yerinden oynamasın

**Bulgu:** Karenin üstüne gelince kart garip biçimde ortalanıyor.

**Ne olacak:** Kare üstüne gelindiğinde yerinde kalır.

**Bitti sayılır:** Galeride fare gezdirmek hiçbir kareyi kaydırmıyor.

### Görev 11 · Durum yazısı okunur olsun

**Bulgu:** "foto kuyrukta" yazısı çok soluk, okunmuyor.

**Ne olacak:** Durum etiketi okunacak kadar açık olur — üç durumun üçünde de aynı ölçüyle.

**Bitti sayılır:** Etiket normal bakışta okunuyor.

### Görev 12 · Video süresi tek yerden gelsin

**Bulgu:** Video süresi iki yerde yazılı: grafikte ve export'un kendi sabitinde. Bugün tutuyorlar;
grafik değişirse export yanlış süre gösterir.

**Ne olacak:** Süre tek bir kaynaktan okunur, ikinci kopya kalkar.

**Bitti sayılır:** Grafikteki süre değiştiğinde export'un söylediği süre kendiliğinden takip ediyor.

---

## Koşunun sonu

Son görev commit edildikten sonra:

1. **Push** — defter repoyu klonluyor, bu yüzden Colab turu ancak push'tan sonra mümkün
   ([FOUNDATION madde 1](../../../queen-editor/FOUNDATION.md)).
2. **Kullanıcının elle Colab turu** — temiz makine, hiçbir model kurulu değil: kurulum ekranından
   üçünü kur, bir kare üret, videosunu ve sesini yap, export al.
3. **CLAUDE.md** queen-editor bölümü v7'yi göstersin, v6 kapandı olarak işaretlensin.
4. **EKSIKLER.md** kapanan maddelerden temizlenir — bir sonraki tur temiz listeyle başlar.
