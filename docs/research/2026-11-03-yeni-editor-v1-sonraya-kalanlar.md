# Yeni editör — Sonraya kalanlar

v1'de yapılmayanlar: yaşanırsa çözülecek sorunlar ve sonra eklenecek özellikler.

## Yaşanırsa çözülecekler

Her birinde: sorun ne, bugün ne yapıyoruz, yaşanırsa ne yapılır.

### Aynı proje iki Colab'da

- **Sorun:** İki Colab aynı projeyi aynı anda değiştirirse biri ötekinin değişikliğini fark etmeden
  silebilir. Drive'da "başkası değiştirdiyse yazma" diye bir şey yok.
- **Bugün:** Koruma yok, queen-editor'daki gibi; aynı projeyi iki Colab'da açmıyoruz (kullanıcı,
  4 Kasım — "şimdilik gereksiz complexity ekleyecek, yaşamadığımız bir problem için"). Core yine de
  bir projeye yazmadan hemen önce Drive'daki halini okur; böylece projeyi sırayla iki Colab'da
  kullanmak ve kuyruğu bir Colab'da çalışan projenin başka Colab'da değişmesi güvenlidir. Aynı
  saniyedeki iki yazma korunmaz: önce yazanın değişikliği bütünüyle kaybolur, proje bozulmaz;
  kaybeden core bunu sonraki bakışında görür ve söyler.
- **Yaşanırsa:** Proje başına kilit: bir proje bir anda yalnız bir Colab'da değiştirilir; öteki onu
  görür ama değiştiremez, "bu proje öbür Colab'da açık" der.

## Sonra eklenecekler

### Edit'te kırpma

- **Ne:** Edit'teki bir yer videonun yalnız bir kısmını kullanır: başlangıç ve bitiş saniyesi.
  Kırpma karede değil yerde tutulur; aynı video bir yerde tam, başka yerde kırpılmış olabilir. Export
  ve UI'daki izleme kırpılmış haliyle oynar.
- **Neden sonra:** v1 için gerek yok (kullanıcı, 4 Kasım — "bence v1 için gerek yok, vazgeçtim
  şimdilik").

### Bütün projelerde aramak

- **Ne:** Kareleri, işleri, edit'leri ya da history'yi bütün projelerde birden aramak (ör. bütün
  projelerde promptunda "yağmur" geçen kareler).
- **Neden sonra:** Depodaki en pahalı işlemdi: yeni açılmış bir Colab'da bütün projeleri Drive'dan
  okur, 500 projede dakikalar sürer. v1'de her adres tek bir projenin altındadır; agent projeleri
  tek tek arar (kullanıcı, 4 Kasım). Tek veritabanına geçince bir sorguyla ucuzlar.

### Export'ta ekran kartıyla kodlama

- **Ne:** ffmpeg önce ekran kartının kodlayıcısını (NVENC) dener, olmazsa işlemciyle kodlar
  (queen-editor madde 257). T4 ve L4'te vardır; A100'de olmadığı kontrol edilecek. Kodlayıcı ekran
  kartında ayrı bir parçadır; ComfyUI'yle aynı anda çalışabilir.
- **Neden sonra:** v1'de export işlemcide kodlanır (kullanıcı, 4 Kasım — "şimdilik CPU'da kalsın,
  sonra düşünürüz").

### Agent'ların skill'leri

- **Ne:** Agent'lara verilecek skill'ler, ör. queen-editor'ın video promptu kuralları (madde 483 ve
  H3 promptunun bölümleri).
- **Neden sonra:** queen-editor'dan taşınmaz; v1 bitince birlikte yazılır.

### Videonun belli bir anına bakmak

- **Ne:** Agent videonun istediği saniyesindeki kareye bakar (ör. 2,5. saniye), bir şeye özellikle
  bakmak için.
- **Neden sonra:** v1'de agent videoya core'un seçtiği saniyede bir karelerle bakar (kullanıcı, 5
  Kasım — "özellikle bir şeye baksın model, şimdilik onu sonra yapılacaklara koyalım").
- **Kaynak:** araştırmada agent için yapılmış video araçlarının çoğu bunu sunuyor (ör. bir genel
  bakış ve istenen saniyede tek kare).

### Agent ile editör arasında iki yönlü hook

- **Ne:** Agent tarafına ve editör tarafına hook eklenebilir mi, iki yönlü; bakılacak. Henüz bir
  fikir; neyin nereye haber vereceği konuşulmadı (kullanıcı, 5 Kasım — "agentta, queen editor
  tarafında hook ekleyebilir miyiz ona bakalım, iki yönlü hook gibi").
- **Neden sonra:** v1'de değil (kullanıcı, 5 Kasım — "bu v1 değil, fikir, unutmayayım diye
  söyledim").

### MCP'de Code Mode benzeri

- **Ne:** Agent liste yerine kısa bir kod yazar; endpoint'ler fonksiyondur, `if`, döngü ve önceki
  çağrının sonucunu kullanmak (ör. `$1.id`) serbesttir. Kod, dosyaya erişemeyen ve ağda yalnız
  core'a çıkabilen bir çalıştırıcıda koşar (ör. Deno).
- **Neden sonra:** Agent koşulu zaten kendisi kurar, API küçük, sonuç kullanmayı gerektiren işler
  (proje oluşturup içine iş vermek, edit oluşturup export almak) nadir ve iki listeyle yapılır; kodu
  önizlemek ve onaylamak listeden zordur.
- **Kaynak:** [Code Mode: the better way to use MCP](https://blog.cloudflare.com/code-mode/),
  [Code Mode: give agents an entire API in 1,000 tokens](https://blog.cloudflare.com/code-mode-mcp/).

Adımlarda "şimdilik yok" denenler de sonraya kalır: yetim dosya süpürmesi, geri alma, `t2v`/`fl2v`,
referans havuzu, export'ta fotoğraf seçeneği ve başka biçimler, queen-editor projelerini açmak, Drive'ın
eski sürümlerini silmek.
