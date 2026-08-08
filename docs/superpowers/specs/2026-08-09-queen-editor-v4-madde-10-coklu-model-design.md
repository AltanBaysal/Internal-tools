# Madde 10 — Çoklu model

**Tarih:** 2026-08-09 · **Branch:** `feat/queen-editor-v2` · **Yol haritası:**
[v4, Madde 10](../plans/2026-08-08-queen-editor-v4-roadmap.md) ·
**Kaynak:** [tasarım v2 farkları](../research/2026-08-08-queen-editor-tasarim-v2-farklari.md),
**P12** ve "model alanı hiç yok" sapması

---

## 1 · Bugünkü hâl ve sorun

Grafik tek bir checkpoint'e bağlı: `workflow_api.json` içindeki 45 numaralı node'un `ckpt_name`
alanı sabit yazılı ve hiçbir yerden değiştirilemiyor. Panelde model alanı **hiç yok** — tasarımda
v1'den beri panelin ilk alanı olmasına rağmen.

Sonuç: içerik çeşitliliği notebook'un o anda kurduğu tek modelle sınırlı, ve modeli değiştirmek
grafiği elle düzenlemeyi gerektiriyor.

## 2 · Karar özeti

| Konu | Karar |
|---|---|
| **P12** | Panelin ilk alanı model açılır listesi olur; seçilen modelle üretilir |
| Liste nereden gelir | **Kurulu olandan** — render sunucusuna sorulur, uygulamada ikinci bir liste tutulmaz |
| Seçim nerede durur | Proje ayarlarında (projeyle birlikte kaydedilir) **ve** her karenin kendisinde |
| Liste okunamazsa | Ayrı ekran yok: alanın yanında hata kartı, **üretim yine çalışır** |
| Hangi modeller kurulacak | Notebook'un CONFIG'inde bir satır — uygulama kaç tane olduğunu bilmez |

## 3 · Liste kurulu modellerden okunur

Uygulama hangi modellerin var olduğunu **bilmez, sorar**: render sunucusuna "checkpoint yükleyicin
hangi dosyaları görüyor?" diye sorulur ve cevap olduğu gibi listelenir.

**Neden ikinci bir liste tutulmuyor:** modelleri notebook kuruyor. Uygulamada da bir liste olsaydı,
notebook'a bir model eklendiğinde iki yerde iki farklı gerçek olurdu ve kullanıcı listede görüp
seçemediği ya da seçip bulunamayan bir modelle karşılaşırdı. Tek soru, tek cevap.

**Yeni model eklemek uygulamayı hiç ilgilendirmez:** notebook'un model listesine bir satır eklenir,
sunucu yeniden başlar, model açılır listede belirir.

## 4 · Seçim karenin üstünde taşınır

Model, negatif prompt gibi **kareye ait**tir. Gerekçe Madde 1'in kararının aynısı: kuyruk canlı,
içinde farklı partiler var ve bir kare hangi ayarla gönderildiyse onunla üretilmelidir. Model
plandaki karede yazılı olduğu için sunucu yeniden başlasa da kare kendi modeliyle üretilir.

Ayrıca **proje ayarlarında** da durur — panel açıldığında son seçim geri gelsin diye. İkisi
birbirinin kopyası değil: ayarlardaki "bir dahaki partide ne seçili olacak", karedeki "bu kare neyle
üretilecek".

**Model yazılmamış eski kareler** (bu maddeden önce planlanmış olanlar) modelsiz kalır ve grafiğin
kendi varsayılan checkpoint'iyle üretilir — bugünkü davranışın aynısı.

## 5 · Liste okunamazsa üretim durmaz

Roadmap: *"Model listesi yüklenemezse ayrı bir ekran değil, kuyruk panelindeki hata kalıbına
girer."*

- Kart, kuyruk panelinin kullandığı **hata kartı kalıbıdır**; ama sorunun olduğu yerde, model
  alanının yanında durur. Ayrı bir ekran yok, ayrı bir kalıp da yok.
- **Üretim engellenmez.** Liste okunamadığında kare modelsiz gider ve grafik kendi varsayılanıyla
  üretir. Bir listeyi okuyamamak, üretimi durdurmak için sebep değil.
- Hiç model kurulu değilse liste boş döner; alan pasifleşir ve boş olduğunu söyler. Üretim yine
  denenir ve grafiğin varsayılanı yoksa **render sunucusunun kendi hatasıyla** durur — uydurma bir
  sebep yazılmaz.

## 6 · Kayıtlı model artık kurulu değilse

Ayarlarda yazan model listede yoksa **seçim sessizce değiştirilmez**: kullanıcının seçtiği ad
listede görünmeye devam eder ve alanın altında tek satır uyarı çıkar. Sessizce başka bir modele
kaydırmak, kullanıcının bir sonraki partiyi hiç istemediği modelle üretmesi demek olurdu.

Uygulama modeli **doğrulamaz**: kurulu olup olmadığına render anında sunucu karar verir ve
olmayanı kendi cümlesiyle söyler. Bu Madde 8'in kuralına da uyar — kare kırmızı olur, kuyruk devam
eder.

## 7 · Değişmeyenler

- Grafiğin geri kalanı, node id'leri, prompt/negatif/seed enjeksiyonu.
- Formun hiç kilitlenmemesi (Madde 3), varyant kuralları, kuyruk davranışı.
- Ayarların **Üretime ekle**'ye basınca kaydedilmesi (model de o anda yazılır).
- Notebook'un model indirme akışı: gated probe, doğrulama, fail-loud.

## 8 · Yok

- Model yükleme/silme arayüzü, model indirme, model başına ayar.
- LoRA seçimi, sampler/adım/CFG alanları (tasarım istemiyor).
- Seçilen modelin doğrulanması, listenin önbelleğe alınması.
- Kare kare farklı model seçme arayüzü — seçim parti bazındadır.

## 9 · Kabul kriterleri (testler bunları kanıtlar)

**Arka uç**

1. Model listesi uç noktası render sunucusunun bildirdiği checkpoint adlarını döndürür.
2. Sunucuya ulaşılamazsa uç nokta hatayı **sunucunun kendi sözleriyle** bildirir, uydurmaz.
3. Gönderilen parti, seçilen modeli **her karesinde** taşır.
4. Döngü kareyi kendi modeliyle üretir; modeli olmayan eski kare modelsiz üretilir.
5. Üretici, modeli grafiğin checkpoint node'una yazar; model boşsa node'a hiç dokunmaz.
6. Model proje ayarlarına yazılır ve geri okunur.

**Ön yüz**

7. Panelin ilk alanı model açılır listesidir ve kurulu modelleri gösterir.
8. Seçim değişip **Üretime ekle**'ye basılınca istek seçilen modelle gider.
9. Liste okunamazsa hata kartı çıkar ama **Üretime ekle** basılabilir kalır.
10. Kayıtlı model listede yoksa seçili kalır ve uyarı satırı çıkar.

## 10 · Kendi eleştirim

- **En kolay yol yine yanlış yoldu.** Uygulamaya sabit bir model listesi yazmak beş dakikalık iş
  olurdu ve notebook'a eklenen her modelde iki listeyi elle eşitlemek gerekirdi. Liste sorularak
  alınıyor; 3. bölüm gerekçesiyle yazılı.
- **"Liste yüklenemedi" üretimi durdurabilirdi.** Alan boş kalınca butonu kilitlemek en kolay
  savunma; ama o zaman render sunucusunun bir uç noktası düştüğü için üretim tamamen durur.
  Modelsiz kare grafiğin varsayılanına düşüyor — bugünkü davranışın aynısı.
- **Kayıtlı modelin kaybolması sessiz bir tuzaktı.** Listeye düşünce ilk modele kaymak kolay ve
  yanlış: kullanıcı farkında olmadan başka bir modelle üretirdi. Seçim korunuyor, uyarı çıkıyor.
- **Model kareye mi ayara mı ait?** İkisi de gerekli ve ikisi farklı soruyu cevaplıyor; birini
  diğerinin kopyası sanıp atmak, canlı kuyrukta yanlış modelle üretime yol açardı.
- **Notebook'ta hangi modeller kurulu olacağı hâlâ kullanıcının kararı.** Uygulama tarafında
  çözülmüş bir soru değil, çözülmesi gerekmeyen bir soru: bir satırlık CONFIG işi ve karar
  kullanıcıda kalıyor.
