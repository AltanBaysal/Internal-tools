# v14 · Görev 24 — Proje ekranının hizalaması · **test turu**

**Kaynak:** yol haritası 24. madde · tasarım v4 fark listesi 5, 6, 8, 9 · fark listesinin 1. kararı ·
43, 44, 45. kararlar.

F bölümünün ikinci ve son maddesi, ve koşunun proje ekranına son dokunuşu. Dört farkın hiçbiri
davranış değil: biri bir çelişkinin kapanması, üçü ölçü ve söz sırası. Motor tarafında iş yok.

## Fark 5 · Çöp yıkıcı eylem standardına geçiyor

Tasarımın kendi metinleri burada birbirini tutmuyordu. Proje kuralları belgesi **proje silmeyi
yıkıcı eylem standardının örnekleri arasında** sayıyor — dolgusuz, kırmızı çerçeve, kırmızı metin,
çöp ikonu. Ekran notları ve kart çizimi ise aynı köşede **çerçevesiz iki ikon** gösteriyor.

Fark listesinin **1. kararı** bunu 20 Ağustos'ta kapattı: kural metnindeki örnek listesi geçerli,
ekran notlarının tarifi değil. 23. madde kalemi getirirken çöpe dokunmadı, çünkü karar o maddenin
değil bu maddenin işiydi.

Çöp bugün `border: none` ile çizilmiş, yalnız kırmızı bir ikon. Evin başka her yerinde yıkıcı düğme
tek bir kalıpta: `{ color: var(--danger), borderColor: var(--danger), background: none }` — kuyruğu
boşalt, hepsini tekrar dene, katman sil, onay penceresinin son düğmesi. Kart da o kalıba giriyor.

**Yazı yok.** Standart soluna çöp ikonu koyan bir düğme tarif ediyor ve düğmenin bir de sözü var;
kartın köşesinde o söze yer yok. Kullanıcının 9 Ağustos 2026 kararı da (v2 fark listesi N4) tam
buydu: kırmızı çerçeve + kırmızı çöp ikonu, **yazısız**. Standardın istediği söz, silme onayının
kendi penceresinde zaten duruyor.

### 43 · Kalem çerçevesiz kalıyor

Standart **yıkıcı** bir düğmenin neye benzediğini söylüyor; kalem yıkıcı değil, ve 3. fark bunu
ayrıca yazıyor. İkisini düzen adına birbirine benzetmek, standardın var olma sebebini silerdi:
kırmızı çerçeve, yanındaki çıplak ikondan **ayrıldığı için** işaret.

Kalem evin `ghost` varyantını alıyor — `background: transparent`, `border-color: transparent`.
Çizgisiz ama aynı kutu: ikisi 4px arayla aynı hizada duruyor, biri çerçeve çiziyor, öteki
çizmiyor. `border: none` ile olmuyordu, çünkü o kutuyu her kenardan bir piksel küçültüyor ve
düğmeler birbirine göre kayıyor.

## Fark 6 · Yeni proje penceresi 380'e iniyor

Tasarım iki pencereye de 380 diyor. 23. madde yeniden adlandırmayı 380'de açtı, yeni projeyi
bugünkü 400'ünde bıraktı ve farkı buraya not etti.

**Ölçü artık dışarıdan gelmiyor.** `NameModal` genişliği çağıranından alıyordu, çünkü iki ayrı ölçü
bekleniyordu; tek ölçü kalınca o kapı boşuna açık duruyor. 105. maddenin kuralı — *ölçü sözlere
aittir, dolayısıyla çağıranın verdiğidir* — burada da geçerli ve aynı yere çıkıyor: iki pencerenin
sözleri **aynı**; aynı etiket, aynı kutu, aynı iki düğme. O yüzden bir ölçü var ve o ölçü pencerenin
kendisinin. `ConfirmModal`'da kapı açık kalıyor: onun üç penceresi gerçekten farklı cümleler
taşıyor.

## Fark 8 · Liste kendi içinde kayıyor

Tasarım: liste sekizi geçince sağında ince bir kaydırma tutamağı belirir, listenin altında zemine
karışan bir soluklaşma bandı çıkar; **liste alanı sabit kalır, içi kayar.**

### 44 · 9 Ağustos'un N3 kararı geri alınıyor

9 Ağustos 2026'da kullanıcı şuna karar vermişti: *"Uzun listede ızgara kendi içinde kaymaz, sayfa
kayar — yapılacak iş yok."* O karar **tasarım v2'ye** karşı verildi ve v2'de hiçbir yerde çizilmiş
bir tutamak yoktu; ortada seçilecek bir şey yerine yalnız "bugünkü hâl yeter mi" sorusu vardı.

v4 tutamağı da bandı da çiziyor, ve ikisi yalnız **kırpılmış bir kutuda** var olabilir: sayfa
kayıyorsa tarayıcının kendi çubuğu zaten var ve altı soluklaşacak bir liste alanı yok. Yol
haritasının 24. maddesi de farkı iş olarak sayıyor. Yeni karar eskisini eziyor.

Yan fayda: uygulamanın diğer dört ekranı (`ProjectScreen`, `PhotoDetail`, `ExportScreen`,
`ProjectLoading`) zaten `height: 100vh` + içeride kayan gövde ile kurulu. Proje ekranı tek
istisnaydı.

### 45 · Gösterge sayıya bakıyor, taşmaya değil

Tasarımın kendi ölçüsü bir **sayı**: "liste sekizi geçince". Sekiz, dört sütunun iki satırı.

Taşmayı ölçmek de bir yol ama uygulanabilir değil: `scrollHeight > clientHeight` karşılaştırması
jsdom'da iki sıfırı karşılaştırır, yani o kuralı doğrulayan test yerleşimi taklit etmek zorunda
kalır ve doğruladığı şey artık uygulamanın davranışı olmaz. Tasarımın söylediği sayıdır, sayılabilen
de odur.

Tutamak bu ayrımdan etkilenmiyor: kutu `overflow-y: auto` ile duruyor ve tarayıcı, kayacak bir şey
yoksa tutamağı zaten çizmiyor. Sayıya bakan yalnız **bant**.

**İnce tutamak bir sınıfla geliyor.** `app.css`'e `.qe-thin-scroll` giriyor; kural WebKit'in
sözde-elemanları, çünkü uygulama yalnız Chrome'da — Colab'ın çıktı çerçevesinde — koşuyor.

## Fark 9 · Silme onayının cümle sırası

Bugün önce silinecek kareler, sonra üretim yazıyor. Tasarım tersini istiyor: **önce çalışan üretimin
duracağı**, sonra karelerin üç dosyasıyla birlikte gideceği. "Bu işlem geri alınamaz." sonda kalıyor.

Cümlelerin kendisi değişmiyor, yalnız yerleri.

## Kapsam dışı

- **Boş listenin ikinci satırı** (fark 7) — 4. kararla kapandı, "kare" kalıyor.
- **Liste ve hata hâlleri** (fark 10), **yazarken doğrulama** (fark 11) — 9. kararla kapandı.
- **Panel şeridi** (fark 12–17) — yol haritasında yok.
- **Motor** — dört farkın hiçbiri sunucuya dokunmuyor.

## Yazılacak testler

### Ön yüz — `ProjectsScreen.test.jsx` (6 yeni, 2 değişen)

| # | Ne diyor | Fark |
|---|---|---|
| 1 | Çöp yıkıcı eylem kalıbını giyiyor: kırmızı çerçeve, kırmızı metin, dolgusuz, çöp ikonu *(değişen)* | 5 |
| 2 | Kalem kendi çizgisini çizmiyor ve kırmızı değil | 5 · karar 43 |
| 3 | Yeni proje penceresi yeniden adlandırma penceresiyle aynı ölçüde açılıyor | 6 |
| 4 | Liste sayfayı değil kendi kutusunu kaydırıyor | 8 · karar 44 |
| 5 | Tutamak listenin kendisinin ve ince | 8 · karar 45 |
| 6 | Sekizi geçince listenin dibinde bant beliriyor ve bant tıklamayı yemiyor | 8 · karar 45 |
| 7 | Sekiz ve altında bant yok | 8 · karar 45 |
| 8 | Onay önce üretimi, sonra kareleri söylüyor *(değişen)* | 9 |

### Ön yüz — `NameModal.test.jsx` (1 değişen)

| # | Ne diyor | Fark |
|---|---|---|
| 9 | Pencere kendi ölçüsünde açılıyor — dışarıdan genişlik almıyor | 6 |

**Ön yüzde 6 yeni test: 527 → 533. Kırmızı duran 9 test** — altı yenisi ve üç değişeni.

## Bitti sayılır

Dört komut da koşuyor; queen-editor'ün frontend takımında **9** kırmızı duruyor, Python takımı
**709** ile yeşil kalıyor. Testler kırmızı commit ediliyor.
