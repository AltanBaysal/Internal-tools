# Kuyruktan çıkarılmış katman yeniden istenebilir: TEST döngüsü (tasarım)

**Tarih:** 2026-08-14 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3` · **Döngü:** 1/2
**Bu döngüde kod yazılmıyor** — yalnız testler, ve takım kırmızı commit'leniyor.

## Ne oldu

2026-08-14: kullanıcı kuyruğu boşalttı, sonra aynı 9 kare için sesi tekrar ekledi. Arayüz *"9 ses
kuyruğa eklendi"* dedi, "Duraklat" düğmesi belirdi, birkaç saniye sonra kayboldu ve yerine biten bir
koşunun eski raporu geldi. Tek bir ses üretilmedi ve bir daha da üretilemez.

## Sebep

Bir iş **(kare, katman)** çiftiyle tanınıyor ve o çiftin son satırı işi kapatıyor. `QUEUED` dışında
her durum temelli kapatıyor — `queue.is_open` yalnız "hiç yazılmamış" ile "yeniden sıraya kondu"yu
açık sayıyor.

*"Kuyruğu boşalt"* bekleyen her işin hücresine `REMOVED` yazıyor. Sonra `queue_layer` plana yeni bir
iş ekliyor ama **o hücreyi açmıyor** — açan satırı hiç yazmıyor. Yani iş planda var, kuyruk onu
görmüyor, koşu hiçbir şey bulamadan bitiyor.

İki kural birbirine bakmıyor:

| Soru | Cevabı veren | `REMOVED` için cevap |
|---|---|---|
| Bu yuvaya üretilebilir mi? | `layers.is_taken` | **Evet**, yuva boş |
| Bu iş hâlâ borçlu mu? | `queue.is_open` | **Hayır**, kapanmış |

`layers`'ın kendi başlığı bu ayrımı bilerek yapıyor ("silinen bir fotoğrafın yuvası boşalır ama kare
sıraya geri girmez") — ama **yeni iş isterken** ikisinin aynı şeyi söylemesi gerekiyor, ve
söylemiyorlar.

`FAILED` bu delikte değil: başarısız bir yuva **dolu** sayılıyor, dolayısıyla `queue_layer` oraya iş
eklemek yerine **kopya kare** doğuruyor ve o yol çalışıyor. Delik yalnız dolu sayılmayan ama kapanmış
olan iki durumda: `REMOVED` ve `DELETED`.

## Hangi davranış doğru sayılacak

**Kapanmış bir yuvaya iş eklenirken yuva yeniden açılır.** Mekanizma zaten var ve sistemin kendi
sözlüğünde yazılı: *"QUEUED, bir işi yeniden açan tek yazılı durumdur."* "Tekrar dene" bunu yapıyor;
`queue_layer` da yapacak.

**Yalnız kapanmış yuvalar için.** Hiç yazılmamış bir yuvaya satır yazmak gereksiz; dolu bir yuva
(`DONE`, `FAILED`) zaten kopya kare yoluna gidiyor ve o yola dokunulmuyor.

**Katmandan bağımsız.** Delik ses'e özgü değil — video ve fotoğraf da aynı kuralla kapanıyor. Test
bunu ses üstünden değil, en az iki katman üstünden söyleyecek.

## Yazılacak testler

Hepsi `test_photo_usecases.py`'de, `queue_layer`'ın kendi bloğunda.

1. **Kuyruktan çıkarılmış ses tekrar istenince üretiliyor.** Ses yuvası `removed` olan bir kare;
   `queue_layer(audio)` sonrası üretici gerçekten çağrılıyor ve dosya kaydediliyor. Kullanıcının
   yaşadığı şeyin aynısı.
2. **Kuyruktan çıkarılmış video da öyle.** Aynı delik, başka katman — düzeltmenin sese özgü
   olmadığını söyler.
3. **Silinmiş katman tekrar istenince üretiliyor.** `deleted` yuva da kapanmış sayılıyor.
4. **Yuvanın yeniden açıldığı kayda geçiyor.** İşlemden sonra kaydın o hücresi `queued` diyor —
   mekanizma varsayılmıyor, yazılıyor. Bu olmadan biri deliği `is_open`'ı gevşeterek "düzeltebilir"
   ve kuyruğun tek kuralı iki yere bölünür.
5. **Başarısız katman, kimsenin seçmediği kapsamda yok.** Bekçi. Testleri yazarken çıktı: başarısız
   bir yuva **dolu** sayıldığı için kare üretim panelinin kapsamından tümüyle çıkıyor ve yalnız
   "Tekrar dene" onu kurtarıyor — bir kare aynı anda iki yoldan üretilemesin diye
   (`layers.py`'nin kendi kuralı). Kapanmış yuvaları açan düzeltme, başarısız olanları geri
   sürüklememeli.
6. **Elle seçilen başarısız katman kopya kare doğuruyor.** İkinci bekçi: kareyi seçmek "şunlar"
   demektir, ve zaten sahip olduğu bir katmanı istemek ikincisini istemektir — o da kopya kare
   olarak doğar, birincisinin üstüne yazılmaz.

## Kırmızı ne olacak

1, 2, 3 ve 4 kırmızı — bugün iş kuyruğa hiç girmiyor, üretici çağrılmıyor. 5 ve 6 yeşil: ikisi de
bugünkü doğru davranışı kilitliyor.

**Bekçiyi yazarken düzeltilen iki varsayım.** İlki yukarıda: başarısız katman seçilmeden kapsama
girmiyor, dolayısıyla "kopya kare doğar" ancak elle seçince doğru. İkincisi adlandırma: bir ses
karenin kimliğinden değil **üstüne bindiği videodan** ad alıyor, ve kopya kare kaynağının videosunu
taşıdığı için dosya adı ikisini ayırt etmiyor — ayıran şey kaydın yazdığı kare kimliği.

## Kapsam dışı

- **Biten koşunun raporunun yenilemeyi aşması.** Aynı turda bulundu, ayrı iş — o ön yüzde, bu
  sunucuda.
- **"Kuyruğu boşalt"ın ne yazdığı.** `REMOVED` doğru: iş üretilmeden çıkarıldı. Değişen, o satırın
  sonsuza dek kapatması.

## Bitti sayılır

`python -m pytest queen-editor/backend/tests -q` dört düşen test veriyor, hepsi kapanmış yuvaya
yeniden iş eklemekle ilgili; geri kalan takım yeşil. Commit kırmızı gidiyor ve mesajı bunu söylüyor.
