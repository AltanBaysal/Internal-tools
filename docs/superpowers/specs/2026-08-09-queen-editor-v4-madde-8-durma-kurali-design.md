# Madde 8 — Durma kuralı ve hata

**Tarih:** 2026-08-09 · **Branch:** `feat/queen-editor-v2` · **Yol haritası:**
[v4, Madde 8](../plans/2026-08-08-queen-editor-v4-roadmap.md) ·
**Kaynak:** [tasarım v2 farkları](../research/2026-08-08-queen-editor-tasarim-v2-farklari.md),
**P26**, **G10** ve "üretim sürerken Tekrar dene çalışmıyor" sapması

---

## 1 · Bugünkü hâl ve sorun

Üretim üç kuralla duruyor, üçü de tasarımın istediği değil:

- **Model yükleyici hatası ilk seferde durduruyor.** Hangi node'un patladığına bakılıp karar
  veriliyor.
- **Üst üste 3 *ayrı kare*** patlayınca duruluyor. Bağlantı kesildiğinde sıradaki üç kare peş peşe
  patlıyor, üçü de galeride kırmızı kalıyor; sorun düzelince tek tek kurtarılmaları gerekiyor.
- **Aynı iş bir kez deneniyor.** Tek seferlik bir istek düşse bile kare harcanıyor.

Ayrıca **Tekrar dene**, kareyi plandaki kendi yerinden alıyor — yani kuyrukta bekleyen işlerin
**önüne geçiyor**.

## 2 · Karar özeti

| Kod | Karar |
|---|---|
| **P26** | Ölümcül hatada **aynı kare** en çok **3 kez** denenir; olmazsa üretim durur ve kare kuyrukta kalır |
| **P26** | Tek karenin patlaması üretimi **durdurmaz** — kare kırmızı olur, sıradakiyle devam edilir |
| **P26** | Model yükleyici ayrımı **kalkar**; ölümcül hatalar kendi aralarında sınıflanmaz |
| **G10** | **Tekrar dene** akan kuyruğu kesmez ve kareyi kuyruğun **sonuna** alır |
| sapma | Üretim sürerken Tekrar dene çalışır (Madde 1'de kapandı, burada testi yazılır) |
| — | Proje açılınca kuyrukta iş varsa üretim **kendiliğinden** sürer |

## 3 · "Ölümcül" ne demek — tahmin değil, mekanik ayrım

Tasarım "hata türüne göre ayrım yapılmaz" derken **model yükleyici özel durumunu** kastediyor
(fark belgesi 8.3): bugün patlayan node'un adına bakılıp "bu ölümcüldür" deniyor, bu kalkıyor. Ama
"tek karenin patlaması üretimi durdurmaz" cümlesi ayakta kaldığı için **bir** ayrım şart. Ayrımı
sebebi tahmin etmeden yapmanın tek yolu, cevabın kimden geldiğine bakmak:

| Ne oldu | Kimin hatası | Ne yapılır |
|---|---|---|
| ComfyUI grafiği çalıştırdı ve **bu render başarısız** dedi | **karenin** | kare kırmızı, kuyruk devam |
| Cevap **hiç gelmedi** — sunucuya ulaşılamadı, HTTP hatası, zaman aşımı, beklenmeyen çıktı | **koşunun** | aynı kare yeniden denenir |

Ayrım **render çağrısının** içindir. Render tuttuktan sonra fotoğrafın Drive'a yazılamaması bu
kuralın dışında kalır ve bugünkü gibi koşuyu olduğu yerde bitirir: yeniden denemek render'ı da
tekrarlar, yani en pahalı işi bir daha yaptırır — ve zaten Madde 8'in konusu değil.

Bu bir sebep sınıflaması değil: "iş başarısız oldu" ile "makine cevap vermedi" ayrımı. Kod tarafında
karşılığı da tek: ComfyUI servisi yalnız render başarısızlığında kendi istisnasını fırlatır, geri
kalan her şey olduğu gibi yukarı çıkar. Alan katmanı servisi **import etmez**, istisnanın üzerinde
bir işaret arar (bugünkü `getattr(exc, "infra", …)` kalıbının aynısı, adı düzeltilerek).

**Yükleyici hatasının bedeli yazılı olsun:** checkpoint eksikse artık her kare aynı hatayla kırmızı
olur ve kuyruk sonuna kadar akar; bugün ilk karede duruyordu. Tasarımın kararı bu ve gerekçesi
sadelik — hata türü tahmin etmek kolayca yanlış tahmine dönüşüyor. Kayıt olsun diye buraya yazıldı.

## 4 · Üç deneme

- Sayaç **kareye ait**: sıradaki kare değişince sıfırlanır.
- Sayaç **yalnız koşunun hafızasında** durur, diske yazılmaz. Ölü bir sürecin geride sayı bırakması
  yanlış olur; sunucu yeniden başladığında üç hakkın yeniden verilmesi de doğru davranıştır.
- 2. ya da 3. deneme tutarsa hiçbir şey olmamış gibi devam edilir: kırmızı kare yok, uyarı yok.
- Üçü de tutmazsa üretim durur. Duran koşunun mesajı iki satırdır: kuralın kendi cümlesi
  (**"Aynı kare 3 kez denendi — üretim durduruldu"**) ve **sunucunun kendi son çıktısı**, olduğu gibi.
- **Kare kırmızıya boyanmaz.** Hiç satır yazılmaz, yani kare kuyrukta bekliyor kalır ve
  **Kaldığı yerden devam et** aynı kareden sürer. Tasarımın "kırmızı kare hiç oluşmuyor" dediği yer
  tam burası.

**Denemeler arasında bekleme yok — bilerek.** Sorulacak ilk soru bu, o yüzden reddi de yazılı: bu
uygulamanın gerçekten gördüğü kesintiler (runtime ölümü, tünelin düşmesi) saniyeler değil dakikalar
sürüyor. Kuyruğu dondurmayacak kadar kısa bir bekleme bu kesintilerde işe yaramaz, işe yarayacak
kadar uzun olanı ise ölü bir runtime'ı sessiz bir duraklamanın arkasına saklar. Üç deneme, düşen tek
bir isteği yutmak içindir; asıl kurtarma yolu **Kaldığı yerden devam et**.

## 5 · Tekrar dene kuyruğun sonuna alır

Kuyruk sırası bugün "plan sırası"dır. Yeni kural: **hiç denenmemiş kareler plan sırasında, sonra
tekrar kuyruğa alınmış kareler.** Böylece kırmızı bir kareye basmak sırada bekleyen işleri
geciktirmez.

- **Galerideki yeri değişmez.** Madde 5'in kuralı duruyor: bir kare nereye konduysa orada kalır,
  durumu yalnız görünümünü değiştirir. Değişen tek şey **hangi sırayla üretileceği**.
- Birden fazla kare tekrar kuyruğa alınmışsa aralarındaki sıra yine plan sırasıdır. Tasarımın istediği
  "sıradakilerin önüne geçmesin" karşılanıyor; bunun ötesinde bir sıra sözü verilmiyor.
- **Akan kuyruk kesilmez:** Tekrar dene yalnız kuyruğa bir satır yazar, worker meşgulse bir sonraki
  turda kareyi kendisi görür (Madde 1'in canlı kuyruğu). Bu sapma zaten kapanmıştı; burada testi
  yazılıyor ki bir daha kapanmasın.

## 6 · Proje açılınca kuyruk kendiliğinden sürer

Roadmap'in cümlesi: *"Proje yeniden açıldığında kuyrukta iş varsa üretim kendiliğinden sürer; elle
Kaldığı yerden devam et yalnız ölümcül hatadan ve duraklatmadan sonra istenir."*

- Proje ekranı açıldığında, worker boştaysa ve kuyrukta iş varsa sunucuya bir kez "devam et" denir.
  Neyin yapılacağına sunucu karar verir — uç nokta zaten iş yoksa reddediyor.
- **Duraklatılmış** ya da **ölümcül hatayla durmuş** koşuda bu istek gönderilmez: o iki hâlin kendi
  butonu var ve kullanıcının kararını beklemesi gerekiyor.
- **Foto detay sayfası bunu yapmaz.** Madde 7'de detay sayfası da aynı canlı kancayı kullanıyor;
  ama bir fotoğrafa bakmak üretim başlatmaz. "Proje açıldı" olayının karşılığı proje ekranıdır.
- **Sınır yazılı olsun:** "duraklatıldı" ve "durdu" hâlleri koşunun hafızasında durur, diske
  yazılmaz. Sunucu yeniden başlarsa bu iki hâl kaybolur ve kuyruk kendiliğinden akmaya devam eder.
  Bilerek: Colab'da yeniden başlamak yeni bir runtime demek, oradaki doğru davranış kaldığı yerden
  devam etmektir. Ölümcül hata hâlâ duruyorsa kuyruk üç denemede yeniden durur ve kart geri gelir.

## 7 · Değişmeyenler

- **Duraklat** çalışan kareyi keser ve kare kuyruğa geri döner (Madde 4).
- Duraklatma sırasında ölen render bir hata değildir: satır yazılmaz, kare kuyrukta kalır.
- Kırmızı karenin galerideki hâli, kendi **Tekrar dene** butonu ve kuyruk panelindeki
  "N kare üretilemedi — galeride göster" satırı.
- Kuyruk panelinin hâlleri, **Kaldığı yerden devam et** butonu ve kartın metinleri (Madde 4).
- Dosya numarası ayırma kuralı: hiçbir numara geri kullanılmaz.

## 8 · Yok

- Denemeler arasında bekleme, üstel geri çekilme.
- Hata türüne göre farklı davranış, hata sınıflandırması, sebep tahmini.
- Deneme sayısının ayara açılması — 3 sabittir, tek yerde yazılıdır.
- Kaç kez denendiğinin ekranda gösterilmesi: kullanıcı sonucu görür, sayacı değil.

## 9 · Kabul kriterleri (testler bunları kanıtlar)

**Arka uç**

1. Render hatası (ComfyUI cevap verdi, kare patladı) → kare kırmızı, kuyruk **sıradaki kareyle
   devam eder**, üretim durmaz.
2. Peş peşe üç kare render hatasıyla patlasa bile üretim durmaz — "üst üste 3 kare" sayımı yok.
3. Ulaşılamayan sunucu → **aynı kare** üç kez denenir; galeride kırmızı kare **oluşmaz**.
4. Üçüncü deneme de düşerse koşu `error` durumuyla biter, mesaj hem kural cümlesini hem sunucunun
   kendi çıktısını taşır; kare **kuyrukta kalır**.
5. İkinci denemede tutarsa fotoğraf yazılır, hiçbir hata satırı kalmaz.
6. Deneme hakkı kare başınadır: bir kare iki kez düşüp sonra tutarsa, bir sonraki karenin hakkı yine
   üçtür.
7. Yükleyici hatası artık ayrıcalıklı değil: ilk hatada durmaz, kare kırmızı olur.
8. **Tekrar dene** ile kuyruğa alınan kare, hiç denenmemiş karelerin **arkasına** girer.
9. Üretim sürerken **Tekrar dene** reddedilmez ve akan koşuyu kesmez.

**Ön yüz**

10. Proje ekranı açıldığında worker boş ve kuyrukta iş varsa bir kez "devam et" istenir.
11. Duraklatılmış, ölümcül hatayla durmuş ya da zaten akan kuyrukta bu istek gönderilmez.
12. İstek proje başına bir kezdir — her yoklamada tekrarlanmaz.

## 10 · Kendi eleştirim

- **"Hata türüne göre ayrım yok" ile "tek kare patlaması durdurmaz" çelişiyordu.** İkisi birden
  ancak ayrım *sebep* üzerinden değil *cevabın kaynağı* üzerinden yapılırsa doğru olur. 3. bölüm
  bunun için var; ayrımın kod tarafında tek bir işarete indiği de orada yazılı.
- **"Kırmızı kare hiç oluşmuyor" cümlesi bir davranış gerektiriyordu.** Üç deneme sonunda kareyi
  kırmızıya boyamak kolay olurdu, ama o zaman tasarımın vaat ettiği kazanç kaybolurdu: kurtarma
  yeniden tek tek kareleri kurtarmaya dönerdi. Satır hiç yazılmıyor.
- **Denemeler arasında bekleme sorusu.** Yazmadan geçilirse "unutulmuş" görünürdü; reddi ve gerekçesi
  4. bölümde.
- **Yükleyici hatasının bedeli.** Karar tasarımın, ama sonucu bizim: eksik checkpoint artık bütün
  kuyruğu kırmızıya boyar. Sessizce uygulamak yerine 3. bölümde açıkça yazıldı.
- **Otomatik devam nereye konur.** Madde 7'de detay sayfası da canlı kancayı kullanır oldu; kancaya
  konsaydı bir fotoğrafa bakmak üretim başlatırdı. Proje ekranına konuyor.
- **Sunucu yeniden başlayınca duraklatma kaybolur.** Otomatik devamın yan etkisi; gizlenmek yerine
  6. bölümde sınır olarak yazıldı.
