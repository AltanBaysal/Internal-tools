# Backlog — Queen Editor

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

---

### Fotoğraf üretim hızı — hız LoRA'ları

Üretim hızlansın; yol olarak hız LoRA'ları denenecek. Kazanç fotoğraf tarafında görünüyor, video
zaten hızlı koşacak şekilde ayarlı.

### Video LoRA denemesi — anatomik hatalar

Video üretiminde anatomik hatalar çıkıyor; üretim tarifinin LoRA'ları değiştirilip denenecek.

### Önbellek koşular arasında yaşamıyor — sabit adres

Her Colab koşusu yeni bir trycloudflare adresi alıyor. Tarayıcıda bayt saklayan her depo — HTTP
önbelleği, Cache Storage, IndexedDB — origin'e, yani konak adının kendisine göre bölünmüş durduğu
için dün tamamen inmiş bir fotoğraf bugün yabancı sayılıp yeniden iniyor. Kendi önbelleğimizi
yazmak bunu çözmüyor; tek kapı adresi sabitlemek, o da cloudflared'in named tunnel kipi ve
kullanıcının kendi alan adı.

İş defterin tünel satırında duruyor: uygulamanın kodu değişmiyor, foto rotasındaki `immutable`
başlığı adres sabitlendiği gün kendiliğinden ikinci yarısını da yapmaya başlar. Başlayabilmesi için
alan adının nameserver'larının Cloudflare'i göstermesi ve Colab secret'ına bir tünel token'ı
konması gerekiyor — ikisi de kullanıcının tarafında.

Kararı bekleyen yan etki: sabit adres, koşu ayaktayken herkesin bilebileceği kalıcı bir kapı demek;
bugünkü rastgele adresin sağladığı örtü kalkıyor. Yol haritası v14, madde 29.

### Galeri seçimi export dönüşünde dağılıyor

Galeride kare seçiliyken export ekranına gidip dönmek — ya da projeden çıkıp girmek — seçimi
dağıtıyor. Sebep her seferinde aynı: adres değişince proje ekranı sökülüyor ve seçim o bileşenin
state'inde duruyor.

**Detay sayfasıyla ilgisi yok.** Seçim modundayken bir kareyi açmanın yolu bulunmuyor: seçim varken
karta tıklamak kareyi açmıyor, seçime ekliyor. Bu yüzden v14'ün 34. maddesinden kullanıcı kararıyla
çıkarıldı — o madde detaydan dönüşü anlatıyordu ve bu durum orada hiç oluşmuyor.

Yapılırsa bedeli `Gallery.test.jsx`'in 112 testini test başına taze modül düzenine geçirmek: seçim
deposu modül seviyesinde duracak ve dosyanın tamamı tek bir proje adını paylaşıyor. Ayrıca
hatırlanan seçimin artık var olmayan kareleri ayıklaması gerekir — detay sayfasından kare
silinebiliyor.

### Prompt BREAK'i desteklemiyor — kalabalık kare tek bloğa kodlanıyor

SDXL'in metin kodlayıcısı promptu 75 jetonluk parçalar hâlinde okuyor, ve bir parçanın içindeki
etiketler birbirine bulaşıyor: iki karakter arka arkaya yazılınca birinin saçı ötekinin üstüne
geçiyor. `BREAK` bunun bilinen ilacı — yazıldığı yerde o parçayı kapatıp yenisini açıyor, böylece
iki taraf birbirinden bağımsız kodlanıyor.

**`BREAK` bir model özelliği değil, promptu okuyan arayüzün özelliği.** A1111 ve Forge kendi
ayrıştırıcısında tanıyor. ComfyUI tanımıyor; oradaki karşılığı ya metni bölüp iki kodlamayı
`Conditioning (Concat)` ile birleştirmek, ya da `comfyui-clip-with-break` gibi BREAK bilen bir
kodlayıcı düğümü koymak.

**Bugün desteklemiyoruz** *(27 Ağustos'ta `workflow_api.json` okunarak doğrulandı)*. Pozitif yol tek
zincir: `3` POSITIVE (`ImpactWildcardProcessor`) → `39` `RegexReplace` — yalnız baştaki ve sondaki
virgülü siliyor → `36` `CLIPTextEncode`. Grafikte `Conditioning (Concat)` hiç yok, ve
`ImpactWildcardProcessor` blok bölmüyor; onun işi wildcard ve LoRA etiketi. Yani prompta yazılan bir
`BREAK` zincirden dokunulmadan geçer ve CLIP tarafından **kelime olarak** kodlanır — ayırmaz,
kirletir.

**Değişecek tek düğüm `36`.** Hem `KSampler` hem `ToDetailerPipe` pozitifi onun çıkışından okuduğu
için tek bir değişiklik ikisini de kapsıyor; FaceDetailer ayrıca ele alınmıyor.

Yapılırsa üç adım: ComfyUI tarafına BREAK bilen düğümü kurmak, workflow'u API biçiminde yeniden dışa
aktarmak, ve `backend/tests/test_workflow_asset.py`'yi güncellemek — o test düğüm anahtarlarını ve
sınıf adlarını adıyla sabitliyor, yani grafik değişince kırmızı veriyor. Bilerek öyle yazılmış.

**Kimin için açılıyor:** promptu QueenAgent üretiyor, kullanıcı `PROMPTS = [...]` olarak buraya
yapıştırıyor *(`prompt_list.py`)*. Bu düğüm açılmadan QueenAgent tarafında `BREAK` üretmenin bir
anlamı yok; o tarafın karşılığı [QueenAgent backlog'unda](../queen-agent/BACKLOG.md) duruyor ve
oraya bağlı.

Araştırmanın tamamı ve kaynakları:
[skill problemleri belgesi](../docs/2026-08-27-queenagent-skill-problemleri.md).
