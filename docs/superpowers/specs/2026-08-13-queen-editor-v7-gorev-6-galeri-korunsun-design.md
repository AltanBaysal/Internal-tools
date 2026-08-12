# Görev 6 — Ekran değişince galeri sıfırdan yüklenmesin

**Roadmap:** [v7](../plans/2026-08-13-queen-editor-v7-roadmap.md) · Blok 3

## Sorun

Bir kareye tıklamak proje ekranını **tamamen söküyor**: yönlendirici detay sayfasını onun yerine
koyuyor, dolayısıyla galeriyi tutan kanca da sıfırdan başlıyor. Liste "henüz bilmiyorum" hâlinde
doğuyor, ekran boşalıyor, istek yeniden gidiyor. Geri dönmek aynı şeyi tekrar yapıyor. Elde duran
cevap her seferinde çöpe gidiyor.

## Ölçüm (Görev 8'e devredilir)

Bu görevin spec'i, roadmap'in söylediği gibi maliyeti de ölçtü — **bir galeri isteği beş ayrı Drive
dosya okuması**:

| Okuma | Neden |
|---|---|
| `photos.jsonl` | katman durumları |
| `photos.jsonl` | duran fotoğraflar |
| `photos.jsonl` | katmanların prompt'ları |
| plan dosyası | kuyruğun ne borçlu olduğu |
| sıra dosyası | galerinin dizilişi |

Kayıt dosyası **üç kez** okunuyor ve her seferinde satır satır ayrıştırılıyor; üç soruyu soran üç
ayrı metot var ve her biri dosyayı kendisi açıyor. Üstüne ekran, üretim koşarken bunu **2 saniyede
bir** istiyor.

Bu maliyet bu görevde düzeltilmiyor: burada değişen şey, elindekini atmamak. Sayı **Görev 8'in
girdisi** — kökün gerçekten orada olduğu ölçüldü, tahmin edilmedi.

## Kararlar

1. **Ekran elindekini atmaz.** Bir projenin en son aldığı liste hatırlanır; ekran yeniden
   kurulduğunda o liste anında çizilir, tazesi gelince yerini alır. Bu bir çizim kararı, kural
   değil — sunucunun cevabı hâlâ tek doğru
   ([FOUNDATION madde 4](../../../queen-editor/FOUNDATION.md)).
2. **Tek yer, iki ekran.** Galeri de detay da aynı kancadan besleniyor, dolayısıyla hafıza oraya
   konur ve ikisi birden düzelir. İkinci bir kopya, iki ekranın farklı şey göstermesi demekti.
3. **Hafıza projeye aittir.** Proje değiştiğinde ekran o projenin kendi listesini gösterir, ya da
   hiçbir şey — bir projenin galerisi başka bir projenin ekranında görünemez.
4. **"Bilinmiyor" hâli gerçek kalır.** Hiç görülmemiş bir proje yine bilinmiyor diye başlar;
   yükleniyor ekranı sahte bir boşluğa değil, gerçek bir bilinmezliğe karşılık gelir.
5. **Sunucuya bu görevde dokunulmaz.** Maliyet Görev 8'in konusu; ikisini bir görevde yapmak,
   hangi değişikliğin neyi düzelttiğini ölçülemez hale getirirdi.
6. **Cevaplanmamış bir duruma göre karar verilmez.** *(Koşu sırasında çıktı, testler yakaladı.)*
   Proje ekranı, yarım kalmış bir kuyruğu kendiliğinden sürdürüyor ve bunu kuyrukta iş varken
   "boşta" durumunu görünce yapıyor. O "boşta", sunucunun söylediği bir şey değil — kanca ilk
   cevabı gelene kadar taşıdığı yer tutucu. Bugüne kadar zararsızdı çünkü galeri de aynı anda
   boştu; hatırlanan galeriyle birlikte kareler durumdan **önce** ekrana geliyor, ve kullanıcının
   durdurduğu bir kuyruk kendiliğinden yeniden başlıyordu. Kanca artık sunucudan haber alıp
   almadığını da söylüyor; ekran o haber gelmeden hiçbir şeye karar vermiyor.

## Testler

- Aynı projeye ikinci kez kurulan kanca, listeyi sunucudan hiçbir cevap gelmeden verir.
- Hiç görülmemiş bir proje bilinmiyor diye başlar.
- Bir projenin listesi başka bir projenin kancasına sızmaz.
- Sıra değiştiğinde ve kare silindiğinde hatırlanan liste de güncellenir — ekran yeniden
  kurulduğunda eski sırayı geri getirmez.

## Öz eleştiri

- *Hatırlanan liste eskiyse kullanıcı eski veriye bakmaz mı?* — Bir isteğin ömrü kadar bakar, ve
  bugün onun yerine boş ekrana bakıyor. Eski liste, boş ekrandan hem daha bilgili hem daha az
  rahatsız edici; taze cevap geldiğinde de sessizce yerini alıyor.
- *Bellek büyümez mi?* — Ziyaret edilen proje başına bir liste. Sekme kapanınca gider. Bir
  projenin galerisi zaten aynı anda ekranda tutulabilen bir şey.
- *Neden sağlayıcı (context) değil de modül hafızası?* — Sağlayıcı da işi görürdü, ama
  yönlendirici ağacın en tepesinde ve iki ekran arasında paylaşılacak tek şey bu liste; onun için
  bütün ağacı bir sağlayıcıya sarmak, kazandığından fazlasını taşırdı.
- *Testler arasında hafıza sızmaz mı?* — Sızar, ve bu bilinerek yapıldı: hafızayı test için
  temizleyen bir üretim fonksiyonu, yalnız testin çağırdığı bir üretim yolu olurdu. Bunun yerine
  boş başlangıcı sınayan test kendi proje adını kullanıyor ve nedenini yazıyor.
